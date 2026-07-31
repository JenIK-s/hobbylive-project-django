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
        $$('.search-history--dropdown').forEach(function (el) {
            el.hidden = true;
        });
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
                    var input = $('[data-search-input]', search) || $('input[name="q"]', search);
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

    /* —— Search history —— */
    var HISTORY_KEY = 'shop_search_history';
    var HISTORY_MAX = 8;
    var REMOVE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';

    function readHistory() {
        try {
            var raw = localStorage.getItem(HISTORY_KEY);
            var list = raw ? JSON.parse(raw) : [];
            return Array.isArray(list) ? list.filter(function (item) {
                return typeof item === 'string' && item.trim();
            }) : [];
        } catch (err) {
            return [];
        }
    }

    function writeHistory(list) {
        try {
            localStorage.setItem(HISTORY_KEY, JSON.stringify(list.slice(0, HISTORY_MAX)));
        } catch (err) { /* ignore quota */ }
    }

    function addHistory(query) {
        var q = (query || '').trim();
        if (!q) return;
        var next = [q].concat(readHistory().filter(function (item) {
            return item.toLowerCase() !== q.toLowerCase();
        }));
        writeHistory(next);
    }

    function clearHistory() {
        writeHistory([]);
        $$('[data-search-shell]').forEach(function (shell) {
            if (shell.contains(document.activeElement)) {
                showHistory(shell);
            } else {
                hideHistory(shell);
            }
        });
    }

    function searchUrl(query) {
        var form = $('[data-search-form]');
        var base = form ? form.getAttribute('action') : '/search/';
        return base + (base.indexOf('?') >= 0 ? '&' : '?') + 'q=' + encodeURIComponent(query);
    }

    function hideHistory(shell) {
        var panel = $('[data-search-history]', shell);
        if (panel) panel.hidden = true;
    }

    function filterHistory(query) {
        var q = (query || '').trim().toLowerCase();
        var items = readHistory();
        if (!q) return items;
        return items.filter(function (item) {
            return item.toLowerCase().indexOf(q) !== -1;
        });
    }

    function showHistory(shell) {
        var panel = $('[data-search-history]', shell);
        var listEl = panel && $('[data-search-history-list]', panel);
        var input = $('[data-search-input]', shell);
        if (!panel || !listEl || !input) return;

        var items = filterHistory(input.value);
        listEl.innerHTML = '';
        if (!items.length) {
            panel.hidden = true;
            return;
        }

        items.forEach(function (item) {
            var li = document.createElement('li');
            var link = document.createElement('a');
            link.href = searchUrl(item);
            link.textContent = item;
            link.addEventListener('mousedown', function (e) {
                e.preventDefault();
                addHistory(item);
                window.location.href = link.href;
            });

            var remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'search-history__remove';
            remove.setAttribute('aria-label', 'Удалить запрос');
            remove.innerHTML = REMOVE_ICON;
            remove.addEventListener('mousedown', function (e) {
                e.preventDefault();
                e.stopPropagation();
            });
            remove.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                writeHistory(readHistory().filter(function (entry) {
                    return entry.toLowerCase() !== item.toLowerCase();
                }));
                showHistory(shell);
            });

            li.appendChild(link);
            li.appendChild(remove);
            listEl.appendChild(li);
        });
        panel.hidden = false;
    }

    $$('[data-search-form]').forEach(function (form) {
        form.addEventListener('submit', function () {
            var input = $('input[name="q"]', form);
            if (input) addHistory(input.value);
        });
        var save = form.getAttribute('data-search-save');
        if (save) addHistory(save);
    });

    $$('[data-search-history-clear]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            clearHistory();
        });
    });

    $$('[data-search-shell]').forEach(function (shell) {
        var input = $('[data-search-input]', shell);
        if (!input) return;

        input.addEventListener('focus', function () { showHistory(shell); });
        input.addEventListener('click', function () { showHistory(shell); });
        input.addEventListener('input', function () { showHistory(shell); });
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') hideHistory(shell);
        });
    });

    document.addEventListener('click', function (e) {
        $$('[data-search-shell]').forEach(function (shell) {
            if (!shell.contains(e.target)) hideHistory(shell);
        });
    });
})();
