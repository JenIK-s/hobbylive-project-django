(function () {
    'use strict';

    function qs(sel, root) {
        return (root || document).querySelector(sel);
    }

    function qsa(sel, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(sel));
    }

    function openEl(el) {
        if (el) el.classList.add('is-open');
    }

    function closeEl(el) {
        if (el) el.classList.remove('is-open');
    }

    var overlay = qs('[data-store-overlay]');
    var cart = qs('[data-store-cart]');
    var menu = qs('[data-store-menu]');
    var search = qs('[data-store-search]');
    var header = qs('[data-store-header]');

    function closeAll() {
        closeEl(overlay);
        closeEl(cart);
        closeEl(menu);
        closeEl(search);
        document.body.style.overflow = '';
    }

    function openPanel(panel) {
        closeAll();
        openEl(overlay);
        openEl(panel);
        document.body.style.overflow = 'hidden';
    }

    qsa('[data-store-open]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            var target = btn.getAttribute('data-store-open');
            if (target === 'cart') openPanel(cart);
            if (target === 'menu') openPanel(menu);
            if (target === 'search') {
                closeAll();
                openEl(search);
                document.body.style.overflow = 'hidden';
                var input = qs('input[name="q"]', search);
                if (input) setTimeout(function () { input.focus(); }, 50);
            }
        });
    });

    qsa('[data-store-close]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            closeAll();
        });
    });

    if (search) {
        search.addEventListener('click', function (e) {
            if (e.target === search) closeAll();
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeAll);
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeAll();
    });

    if (header) {
        var onScroll = function () {
            if (window.scrollY > 8) header.classList.add('is-scrolled');
            else header.classList.remove('is-scrolled');
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    qsa('.store-toast').forEach(function (toast) {
        var closeBtn = qs('.store-toast__close', toast);
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                toast.remove();
            });
        }
        setTimeout(function () {
            toast.classList.add('is-hide');
            setTimeout(function () { toast.remove(); }, 300);
        }, 4500);
    });

    qsa('[data-store-tabs]').forEach(function (tabs) {
        var buttons = qsa('[data-tab]', tabs);
        var root = tabs.parentElement;
        buttons.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                var id = btn.getAttribute('data-tab');
                buttons.forEach(function (b) { b.classList.remove('is-active'); });
                btn.classList.add('is-active');
                qsa('[data-tab-panel]', root).forEach(function (panel) {
                    panel.classList.toggle('is-active', panel.getAttribute('data-tab-panel') === id);
                });
            });
        });
    });

    var qtyInput = qs('#qtybutton');
    var dec = qs('#decrement');
    var inc = qs('#increment');
    if (qtyInput && dec && inc) {
        dec.addEventListener('click', function () {
            var v = parseInt(qtyInput.value, 10) || 1;
            if (v > 1) qtyInput.value = v - 1;
        });
        inc.addEventListener('click', function () {
            var v = parseInt(qtyInput.value, 10) || 1;
            qtyInput.value = v + 1;
        });
    }
})();
