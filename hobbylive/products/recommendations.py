from collections import defaultdict

from django.db.models import F, Q
from django.db.models.functions import Coalesce

from .models import Product, ProductPopularity, UserInterest

WEIGHTS = {
    "view": 1.0,
    "search": 2.0,
    "wishlist": 3.0,
    "cart": 5.0,
    "purchase": 10.0,
    "category_view": 0.8,
    "category_search": 1.2,
    "category_cart": 2.0,
    "category_wishlist": 1.5,
    "category_purchase": 4.0,
    "query_search": 3.0,
}

SEARCH_HIT_LIMIT = 12


def _ensure_popularity(product):
    pop, _ = ProductPopularity.objects.get_or_create(product=product)
    return pop


def _bump_popularity(product, field, amount=1):
    pop = _ensure_popularity(product)
    ProductPopularity.objects.filter(pk=pop.pk).update(**{field: F(field) + amount})
    pop.refresh_from_db()
    pop.recalculate_score()
    pop.save(update_fields=["score", "updated_at"])
    return pop


def _normalize_query(query):
    return " ".join((query or "").strip().lower().split())[:255]


def _is_auth(user):
    return bool(user and getattr(user, "is_authenticated", False))


def _add_interest(user, kind, key, delta):
    if not _is_auth(user) or not key or not delta:
        return
    key = str(key)[:255]
    interest, created = UserInterest.objects.get_or_create(
        user=user,
        kind=kind,
        key=key,
        defaults={"weight": float(delta)},
    )
    if not created:
        UserInterest.objects.filter(pk=interest.pk).update(weight=F("weight") + float(delta))


def _product_category_ids(product):
    return list(product.Categories.values_list("id", flat=True))


def track_product_view(user, product):
    _bump_popularity(product, "views")
    if _is_auth(user):
        _add_interest(user, UserInterest.KIND_PRODUCT, product.pk, WEIGHTS["view"])
        for cat_id in _product_category_ids(product):
            _add_interest(user, UserInterest.KIND_CATEGORY, cat_id, WEIGHTS["category_view"])


def track_search(user, query, matched_products):
    normalized = _normalize_query(query)
    if not normalized:
        return

    products = list(matched_products[:SEARCH_HIT_LIMIT])
    for product in products:
        _bump_popularity(product, "search_hits")

    if not _is_auth(user):
        return

    _add_interest(user, UserInterest.KIND_QUERY, normalized, WEIGHTS["query_search"])
    seen_cats = set()
    for product in products:
        _add_interest(user, UserInterest.KIND_PRODUCT, product.pk, WEIGHTS["search"] * 0.5)
        for cat_id in _product_category_ids(product):
            if cat_id in seen_cats:
                continue
            seen_cats.add(cat_id)
            _add_interest(user, UserInterest.KIND_CATEGORY, cat_id, WEIGHTS["category_search"])


def track_cart_add(user, product):
    _bump_popularity(product, "cart_adds")
    if _is_auth(user):
        _add_interest(user, UserInterest.KIND_PRODUCT, product.pk, WEIGHTS["cart"])
        for cat_id in _product_category_ids(product):
            _add_interest(user, UserInterest.KIND_CATEGORY, cat_id, WEIGHTS["category_cart"])


def track_wishlist_add(user, product):
    _bump_popularity(product, "wishlist_adds")
    if _is_auth(user):
        _add_interest(user, UserInterest.KIND_PRODUCT, product.pk, WEIGHTS["wishlist"])
        for cat_id in _product_category_ids(product):
            _add_interest(
                user, UserInterest.KIND_CATEGORY, cat_id, WEIGHTS["category_wishlist"]
            )


def track_purchase(user, products):
    seen = set()
    for product in products:
        if product.pk in seen:
            continue
        seen.add(product.pk)
        _bump_popularity(product, "purchases")
        if _is_auth(user):
            _add_interest(user, UserInterest.KIND_PRODUCT, product.pk, WEIGHTS["purchase"])
            for cat_id in _product_category_ids(product):
                _add_interest(
                    user, UserInterest.KIND_CATEGORY, cat_id, WEIGHTS["category_purchase"]
                )


def _base_qs():
    return Product.objects.prefetch_related("images", "Categories").all()


def get_popular_products(limit=8):
    qs = (
        _base_qs()
        .filter(popularity__isnull=False)
        .order_by("-popularity__score", "-id")[:limit]
    )
    products = list(qs)
    if len(products) >= limit:
        return products

    exclude_ids = [p.pk for p in products]
    need = limit - len(products)
    discounted = list(
        _base_qs()
        .filter(discount__gt=0)
        .exclude(pk__in=exclude_ids)
        .order_by("-discount", "-id")[:need]
    )
    products.extend(discounted)
    if len(products) >= limit:
        return products[:limit]

    exclude_ids = [p.pk for p in products]
    need = limit - len(products)
    products.extend(
        list(_base_qs().exclude(pk__in=exclude_ids).order_by("-id")[:need])
    )
    return products[:limit]


def get_personalized_products(user, limit=8):
    if not _is_auth(user):
        return get_popular_products(limit=limit)

    interests = list(
        UserInterest.objects.filter(user=user).order_by("-weight", "-updated_at")[:40]
    )
    if not interests:
        return get_popular_products(limit=limit)

    product_weights = defaultdict(float)
    category_ids = []
    queries = []

    for item in interests:
        if item.kind == UserInterest.KIND_PRODUCT:
            try:
                product_weights[int(item.key)] += float(item.weight) * 3.0
            except (TypeError, ValueError):
                continue
        elif item.kind == UserInterest.KIND_CATEGORY:
            try:
                category_ids.append((int(item.key), float(item.weight)))
            except (TypeError, ValueError):
                continue
        elif item.kind == UserInterest.KIND_QUERY and item.key:
            queries.append((item.key, float(item.weight)))

    if category_ids:
        cat_map = {cid: w for cid, w in category_ids}
        for product in (
            Product.objects.filter(Categories__id__in=cat_map.keys())
            .distinct()
            .only("id")
        ):
            # weight by strongest matching category interest
            cats = product.Categories.filter(id__in=cat_map.keys()).values_list("id", flat=True)
            boost = max((cat_map[c] for c in cats), default=0)
            product_weights[product.pk] += boost * 2.0

    for query, weight in queries[:8]:
        matched = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).values_list("id", flat=True)[:20]
        for pk in matched:
            product_weights[pk] += weight * 1.5

    # blend in global popularity so feed is not empty/closed
    for pop in ProductPopularity.objects.order_by("-score")[:limit * 2]:
        product_weights[pop.product_id] += max(pop.score, 1) * 0.15

    if not product_weights:
        return get_popular_products(limit=limit)

    ranked_ids = sorted(product_weights.keys(), key=lambda pk: product_weights[pk], reverse=True)
    ranked_ids = ranked_ids[: max(limit * 3, limit)]

    products_by_id = {
        p.pk: p
        for p in _base_qs().filter(pk__in=ranked_ids)
    }
    ordered = [products_by_id[pk] for pk in ranked_ids if pk in products_by_id][:limit]

    if len(ordered) < limit:
        exclude = [p.pk for p in ordered]
        ordered.extend(
            [p for p in get_popular_products(limit=limit) if p.pk not in exclude][
                : limit - len(ordered)
            ]
        )
    return ordered[:limit]


def get_related_products(product, limit=8):
    """Товары из тех же категорий, с приоритетом популярных."""
    category_ids = list(product.Categories.values_list("id", flat=True))
    qs = (
        _base_qs()
        .exclude(pk=product.pk)
        .annotate(pop_score=Coalesce("popularity__score", 0))
    )
    if category_ids:
        related = list(
            qs.filter(Categories__id__in=category_ids)
            .distinct()
            .order_by("-pop_score", "-id")[:limit]
        )
        if len(related) >= limit:
            return related
        exclude = [product.pk] + [p.pk for p in related]
        need = limit - len(related)
        related.extend(
            list(qs.exclude(pk__in=exclude).order_by("-pop_score", "-id")[:need])
        )
        return related[:limit]

    return list(qs.order_by("-pop_score", "-id")[:limit])
