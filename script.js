document.addEventListener('DOMContentLoaded', () => {
    // 1. Sticky Navbar Effect on Scroll
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // 2. Mobile Menu Toggle
    const mobileToggle = document.getElementById('mobileToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link, .mobile-cta');

    if (mobileToggle && mobileMenu) {
        mobileToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            mobileToggle.classList.toggle('open');
        });

        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('active');
            });
        });
    }

    // 3. Colorway Selector Microinteraction
    const colorBtns = document.querySelectorAll('.color-btn');
    const colorNameBadge = document.getElementById('colorNameBadge');
    const gradStop1 = document.getElementById('gradStop1');
    const gradStop2 = document.getElementById('gradStop2');
    const cupStop1 = document.getElementById('cupStop1');
    const cupStop2 = document.getElementById('cupStop2');
    const cupLeft = document.getElementById('cupLeft');
    const cupRight = document.getElementById('cupRight');
    const heroAura = document.getElementById('heroAura');

    const colorPresets = {
        beige: {
            name: "Calm Beige",
            grad1: "#EADCC9",
            grad2: "#BFAC90",
            cup1: "#F5ECE1",
            cup2: "#D9C7B2",
            stroke: "#B5A188",
            aura: "radial-gradient(circle, rgba(212, 175, 55, 0.25) 0%, rgba(0,0,0,0) 70%)"
        },
        black: {
            name: "Carbon Black",
            grad1: "#333A42",
            grad2: "#1A1D24",
            cup1: "#252B33",
            cup2: "#12151B",
            stroke: "#3A424D",
            aura: "radial-gradient(circle, rgba(100, 116, 139, 0.25) 0%, rgba(0,0,0,0) 70%)"
        },
        teal: {
            name: "Tropical Teal",
            grad1: "#2C6E7A",
            grad2: "#16383E",
            cup1: "#3B8896",
            cup2: "#1B4750",
            stroke: "#2A6470",
            aura: "radial-gradient(circle, rgba(44, 110, 122, 0.3) 0%, rgba(0,0,0,0) 70%)"
        }
    };

    colorBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            colorBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const colorKey = btn.getAttribute('data-color');
            const preset = colorPresets[colorKey];

            if (preset) {
                if (colorNameBadge) colorNameBadge.textContent = preset.name;
                if (gradStop1) gradStop1.setAttribute('stop-color', preset.grad1);
                if (gradStop2) gradStop2.setAttribute('stop-color', preset.grad2);
                if (cupStop1) cupStop1.setAttribute('stop-color', preset.cup1);
                if (cupStop2) cupStop2.setAttribute('stop-color', preset.cup2);
                if (cupLeft) cupLeft.setAttribute('stroke', preset.stroke);
                if (cupRight) cupRight.setAttribute('stroke', preset.stroke);
                if (heroAura) heroAura.style.background = preset.aura;
            }
        });
    });

    // 4. FAQ Accordion Logic
    const faqQuestions = document.querySelectorAll('.faq-question');
    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            const faqItem = question.parentElement;
            const isOpen = faqItem.classList.contains('active');

            // Close all other FAQ items
            document.querySelectorAll('.faq-item').forEach(item => {
                item.classList.remove('active');
            });

            // Toggle current item
            if (!isOpen) {
                faqItem.classList.add('active');
            }
        });
    });

    // 5. Scroll Reveal IntersectionObserver
    const revealElements = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('reveal-active');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15
    });

    revealElements.forEach(el => revealObserver.observe(el));

    // 6. Number Counter Animation for Stats
    const counters = document.querySelectorAll('.counter');
    const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'), 10);
                let current = 0;
                const increment = Math.ceil(target / 40);

                const updateCounter = () => {
                    current += increment;
                    if (current >= target) {
                        counter.textContent = target.toLocaleString();
                    } else {
                        counter.textContent = current.toLocaleString();
                        requestAnimationFrame(updateCounter);
                    }
                };

                updateCounter();
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => counterObserver.observe(counter));

    // 7. Video Modal Logic
    const openVideoBtn = document.getElementById('openVideoModal');
    const closeVideoBtn = document.getElementById('closeVideoModal');
    const videoModal = document.getElementById('videoModal');

    if (openVideoBtn && videoModal && closeVideoBtn) {
        openVideoBtn.addEventListener('click', () => {
            videoModal.classList.add('active');
        });

        closeVideoBtn.addEventListener('click', () => {
            videoModal.classList.remove('active');
        });

        videoModal.addEventListener('click', (e) => {
            if (e.target === videoModal) {
                videoModal.classList.remove('active');
            }
        });
    }
});
