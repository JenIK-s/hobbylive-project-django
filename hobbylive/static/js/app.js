(function () {
    'use strict';

    function $(sel, root) { return (root || document).querySelector(sel); }
    function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

    var veil = $('[data-veil]');
    var cart = $('[data-cart]');
    var menu = $('[data-menu]');
    var search = $('[data-search]');
    var header = $('[data-header]');

    function closeAll() {
        [veil, cart, menu, search].forEach(function (el) {
            if (el) el.classList.remove('is-open');
        });
        document.body.style.overflow = '';
    }

    function openPanel(panel) {
        closeAll();
        if (veil) veil.classList.add('is-open');
        if (panel) panel.classList.add('is-open');
        document.body.style.overflow = 'hidden';
    }

    $$('[data-open]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            var name = btn.getAttribute('data-open');
            if (name === 'cart') openPanel(cart);
            if (name === 'menu') openPanel(menu);
            if (name === 'search') {
                closeAll();
                if (search) {
                    search.classList.add('is-open');
                    document.body.style.overflow = 'hidden';
                    var input = $('input[name="q"]', search);
                    if (input) setTimeout(function () { input.focus(); }, 40);
                }
            }
        });
    });

    $$('[data-close]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            closeAll();
        });
    });

    if (veil) veil.addEventListener('click', closeAll);

    if (search) {
        search.addEventListener('click', function (e) {
            if (e.target === search) closeAll();
        });
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAll();
    });

    if (header) {
        var onScroll = function () {
            header.classList.toggle('is-scrolled', window.scrollY > 6);
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    $$('.flash__item').forEach(function (item) {
        var closeBtn = $('[data-flash-close]', item);
        if (closeBtn) closeBtn.addEventListener('click', function () { item.remove(); });
        setTimeout(function () {
            item.classList.add('is-hide');
            setTimeout(function () { item.remove(); }, 250);
        }, 4500);
    });

    $$('[data-profile-nav]').forEach(function (nav) {
        var buttons = $$('[data-profile-tab]', nav);
        var root = nav.parentElement;
        buttons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var id = btn.getAttribute('data-profile-tab');
                buttons.forEach(function (b) { b.classList.remove('is-on'); });
                btn.classList.add('is-on');
                $$('[data-profile-panel]', root).forEach(function (panel) {
                    panel.classList.toggle('is-on', panel.getAttribute('data-profile-panel') === id);
                });
            });
        });
    });

    var qty = $('#qtybutton');
    var dec = $('#decrement');
    var inc = $('#increment');
    if (qty && dec && inc) {
        dec.addEventListener('click', function () {
            var v = parseInt(qty.value, 10) || 1;
            if (v > 1) qty.value = v - 1;
        });
        inc.addEventListener('click', function () {
            qty.value = (parseInt(qty.value, 10) || 1) + 1;
        });
    }
})();
