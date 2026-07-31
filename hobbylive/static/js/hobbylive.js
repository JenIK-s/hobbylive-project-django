(function () {
    'use strict';

    if (typeof WOW !== 'undefined') {
        new WOW({ mobile: true, live: false }).init();
    }

    document.querySelectorAll('.hl-toast').forEach(function (toast) {
        setTimeout(function () {
            toast.classList.add('hl-toast--hide');
            setTimeout(function () { toast.remove(); }, 400);
        }, 5000);
    });

    var heroScroll = document.querySelector('.hl-hero__scroll');
    if (heroScroll) {
        heroScroll.addEventListener('click', function (e) {
            e.preventDefault();
            var target = document.querySelector('#categories');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    var header = document.querySelector('.hl-header');
    if (header) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                header.classList.add('hl-header--scrolled');
            } else {
                header.classList.remove('hl-header--scrolled');
            }
        });
    }

    var path = window.location.pathname;
    document.querySelectorAll('.hl-nav__link').forEach(function (link) {
        var href = link.getAttribute('href');
        if (!href) return;
        if (path === href || (href !== '/' && path.startsWith(href))) {
            link.classList.add('active');
        }
    });
})();
