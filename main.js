document.addEventListener('DOMContentLoaded', () => {

    /* --- 0. Deferred Video Autoplay --- */
    const heroVideo = document.querySelector('.slide-video');
    if (heroVideo) {
        window.addEventListener('load', () => {
            heroVideo.play().catch(() => {});
        }, { once: true });
    }

    /* --- 1. Hero Slider --- */
    const slides = document.querySelectorAll('.slide');

    // Only initialize slider if there are multiple slides
    if (slides.length > 1) {
        const dots = document.querySelectorAll('.dot');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        let currentSlide = 0;
        let slideInterval;
        const intervalTime = 5000;

        function goToSlide(n) {
            const currentVideo = slides[currentSlide].querySelector('video');
            if (currentVideo) currentVideo.pause();

            slides[currentSlide].classList.remove('active');
            if (dots[currentSlide]) dots[currentSlide].classList.remove('active');

            currentSlide = (n + slides.length) % slides.length;

            slides[currentSlide].classList.add('active');
            if (dots[currentSlide]) dots[currentSlide].classList.add('active');

            const nextVideo = slides[currentSlide].querySelector('video');
            if (nextVideo) nextVideo.play();
        }

        function nextSlide() { goToSlide(currentSlide + 1); }
        function prevSlide() { goToSlide(currentSlide - 1); }
        function startSlideShow() { slideInterval = setInterval(nextSlide, intervalTime); }
        function resetSlideShow() { clearInterval(slideInterval); startSlideShow(); }

        if (nextBtn) nextBtn.addEventListener('click', () => { nextSlide(); resetSlideShow(); });
        if (prevBtn) prevBtn.addEventListener('click', () => { prevSlide(); resetSlideShow(); });

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => { goToSlide(index); resetSlideShow(); });
        });

        startSlideShow();
    } else if (slides.length === 1) {
        // If only one slide, just ensure it's active and video plays
        slides[0].classList.add('active');
        const video = slides[0].querySelector('video');
        if (video) video.play().catch(e => console.warn("Video autoplay prevented:", e));
    }

    /* --- 2. Mobile Navigation --- */
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const headerNav = document.querySelector('.header-nav');
    const navOverlay = document.getElementById('nav-overlay');

    if (mobileMenuBtn && headerNav) {
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
        
        const toggleMenu = () => {
            const isActive = headerNav.classList.toggle('mobile-active');
            if (navOverlay) navOverlay.classList.toggle('active');
            
            mobileMenuBtn.setAttribute('aria-expanded', isActive ? 'true' : 'false');
            mobileMenuBtn.innerHTML = isActive
                ? '<i class="ph ph-x"></i>'
                : '<i class="ph ph-list"></i>';
                
            // Prevent body scroll when menu is open
            document.body.style.overflow = isActive ? 'hidden' : '';
        };

        mobileMenuBtn.addEventListener('click', toggleMenu);
        if (navOverlay) navOverlay.addEventListener('click', toggleMenu);
    }

    /* --- 3. Scroll Reveal --- */
    const revealElements = document.querySelectorAll('.scroll-reveal');
    if (revealElements.length > 0) {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (prefersReducedMotion) {
            revealElements.forEach(el => el.classList.add('revealed'));
        } else {
            const revealObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.15 });

            revealElements.forEach(el => revealObserver.observe(el));
        }
    }

    /* --- 4. Gallery Lightbox --- */
    const galleryItems = document.querySelectorAll('.gallery-item');
    if (galleryItems.length > 0) {
        // Create Lightbox Modal
        const lightbox = document.createElement('div');
        lightbox.id = 'lightbox-modal';
        lightbox.className = 'lightbox-modal';
        lightbox.innerHTML = `
            <span class="lightbox-close">&times;</span>
            <img class="lightbox-content" id="lightbox-img" alt="Gallery Image">
        `;
        document.body.appendChild(lightbox);

        const lightboxImg = document.getElementById('lightbox-img');
        const closeBtn = lightbox.querySelector('.lightbox-close');

        galleryItems.forEach(item => {
            item.addEventListener('click', () => {
                const img = item.querySelector('img');
                if (img) {
                    lightboxImg.src = img.src;
                    lightbox.classList.add('active');
                    document.body.style.overflow = 'hidden'; // Prevent scroll
                }
            });
        });

        const closeLightbox = () => {
            lightbox.classList.remove('active');
            document.body.style.overflow = '';
        };

        closeBtn.addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && lightbox.classList.contains('active')) {
                closeLightbox();
            }
        });
    }

    /* --- 6. Cookie Consent Banner --- */
    if (!localStorage.getItem('cookie_consent')) {
        const isBlogPage = window.location.pathname.includes('/blog/');
        const cookiePolicyHref = isBlogPage ? '../cookie-policy.html' : 'cookie-policy.html';
        const cookieBanner = document.createElement('div');
        cookieBanner.id = 'cookie-banner';
        cookieBanner.className = 'cookie-banner';
        cookieBanner.setAttribute('role', 'dialog');
        cookieBanner.setAttribute('aria-label', 'Informativa sui cookie');
        cookieBanner.innerHTML = `
            <div class="cookie-banner-content">
                <div class="cookie-banner-title"><i class="ph ph-cookie"></i> Utilizziamo i cookie</div>
                <p class="cookie-banner-text">Questo sito utilizza cookie tecnici necessari per il corretto funzionamento e risorse di terze parti per migliorare la tua esperienza di navigazione. Leggi la nostra <a href="${cookiePolicyHref}">Cookie Policy</a>.</p>
                <div class="cookie-banner-actions">
                    <button type="button" class="cookie-btn cookie-btn-accept" id="cookie-accept">Accetta tutti</button>
                    <button type="button" class="cookie-btn cookie-btn-decline" id="cookie-decline">Solo necessari</button>
                </div>
            </div>
        `;
        document.body.appendChild(cookieBanner);

        // Show banner after a short delay so it doesn't flash immediately
        setTimeout(() => {
            cookieBanner.classList.add('visible');
        }, 1500);

        const acceptBtn = document.getElementById('cookie-accept');
        const declineBtn = document.getElementById('cookie-decline');

        const hideBanner = () => {
            cookieBanner.classList.remove('visible');
            setTimeout(() => {
                cookieBanner.remove();
            }, 300);
        };

        if (acceptBtn) {
            acceptBtn.addEventListener('click', () => {
                localStorage.setItem('cookie_consent', 'accepted');
                hideBanner();
            });
        }

        if (declineBtn) {
            declineBtn.addEventListener('click', () => {
                localStorage.setItem('cookie_consent', 'declined');
                hideBanner();
            });
        }
    }

    /* --- 7. Search Overlay --- */
    const searchBtn = document.querySelector('.header-search button');
    if (searchBtn) {
        const searchOverlay = document.createElement('div');
        searchOverlay.className = 'search-overlay';
        searchOverlay.id = 'search-overlay';
        searchOverlay.innerHTML = `
            <button class="search-overlay-close" aria-label="Chiudi ricerca"><i class="ph ph-x"></i></button>
            <div class="search-box">
                <i class="ph ph-magnifying-glass"></i>
                <h2>Cerca nel sito</h2>
                <p>Trova prodotti, servizi e guide</p>
                <form class="search-form" id="search-form">
                    <input type="search" id="search-input" placeholder="Cerca finestre, sicurezza, preventivo..." aria-label="Cerca">
                    <button type="submit" class="btn btn-primary">Cerca</button>
                </form>
                <div id="search-results" class="search-results"></div>
            </div>
        `;
        document.body.appendChild(searchOverlay);

        const searchInput = document.getElementById('search-input');
        const searchResults = document.getElementById('search-results');

        const openSearch = () => {
            searchOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        };

        const closeSearch = () => {
            searchOverlay.classList.remove('active');
            document.body.style.overflow = '';
            if (searchInput) searchInput.value = '';
            if (searchResults) searchResults.innerHTML = '';
        };

        searchBtn.addEventListener('click', openSearch);

        const closeBtn = searchOverlay.querySelector('.search-overlay-close');
        if (closeBtn) closeBtn.addEventListener('click', closeSearch);

        searchOverlay.addEventListener('click', (e) => {
            if (e.target === searchOverlay) closeSearch();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
                closeSearch();
            }
        });

        // Search index of site pages
        const searchIndex = [
            { title: 'Home', url: 'index.html', keywords: 'infissi serramenti showroom casa finestre porte home' },
            { title: 'Finestre e Portefinestre', url: 'finestre.html', keywords: 'finestre portefinestre pvc alluminio legno rehau schuco veka salamander energia risparmio energetico serramenti' },
            { title: 'Porte Blindate', url: 'porte-blindate.html', keywords: 'porte blindate sicurezza antieffrazione serrature mottura cisa evva disec cilindri classe 4 blindata' },
            { title: 'Persiane', url: 'persiane.html', keywords: 'persiane legno alluminio pvc imposte finestre sicurezza estetica protezione' },
            { title: 'Avvolgibili', url: 'avvolgibili.html', keywords: 'avvolgibili tapparelle pvc alluminio coibentato acciaio isolamento oscuramento sicurezza' },
            { title: 'Cassonetti', url: 'cassonetti.html', keywords: 'cassonetti coibentati isolamento termico acustico tapparelle foro finestra' },
            { title: 'Zanzariere', url: 'zanzariere.html', keywords: 'zanzariere insetti rullo plissettate scorrevoli fisse battente rete moscerini' },
            { title: 'Grate di Sicurezza', url: 'grate-sicurezza.html', keywords: 'grate sicurezza inferriate acciaio ferro battuto finestre antieffrazione' },
            { title: 'Tende da Sole', url: 'tende-da-sole.html', keywords: 'tende sole terrazze giardini bracci cassonetto tessuti uv protezione ombreggianti' },
            { title: 'Chi Siamo', url: 'chi-siamo.html', keywords: 'chi siamo azienda storia infissi paradise roma dal 1992 produzione' },
            { title: 'Contatti', url: 'contatti.html', keywords: 'contatti preventivo express email whatsapp telefono roma modulo' },
            { title: 'Bonus Sicurezza 2025: Detrazione 50% per Infissi', url: 'blog/bonus-sicurezza.html', keywords: 'bonus sicurezza 50% detrazione fiscale inferriate grate infissi 2025 2026' },
            { title: 'Detrazioni Fiscali Infissi 2026: Guida Completa', url: 'blog/detrazioni-fiscali-infissi.html', keywords: 'detrazioni fiscali 2026 ecobonus bonus ristrutturazioni infissi 50% guida' },
            { title: 'IVA Agevolata al 10% per Inferriate di Sicurezza', url: 'blog/iva-agevolata-inferriate.html', keywords: 'iva agevolata 10% inferriate grate sicurezza tasse aliquota' },
            { title: 'Quali Materiali Scegliere per le Finestre?', url: 'blog/materiali-finestre.html', keywords: 'materiali finestre pvc legno alluminio legno-alluminio acciaio pro contro guida' },
            { title: 'Privacy Policy', url: 'privacy.html', keywords: 'privacy dati personali gdpr trattamento cookie informative' },
            { title: 'Cookie Policy', url: 'cookie-policy.html', keywords: 'cookie policy cookie tecnici consenso navigazione' }
        ];
        const urlPrefix = window.location.pathname.includes('/blog/') ? '../' : '';

        const performSearch = (query) => {
            if (!searchResults) return;
            const q = query.toLowerCase().trim();
            if (q.length < 2) {
                searchResults.innerHTML = '';
                return;
            }

            const matches = searchIndex.filter(item => {
                return item.title.toLowerCase().includes(q) || item.keywords.toLowerCase().includes(q);
            });

            if (matches.length === 0) {
                searchResults.innerHTML = '<p class="search-no-results">Nessun risultato trovato. Prova con altre parole come "finestre", "sicurezza", "preventivo"...</p>';
                return;
            }

            searchResults.innerHTML = matches.slice(0, 8).map(item =>
                `<a href="${urlPrefix}${item.url}" class="search-result-item"><h3>${item.title}</h3></a>`
            ).join('');
        };

        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                if (searchInput) performSearch(searchInput.value);
            });
        }
        if (searchInput) {
            searchInput.addEventListener('input', () => performSearch(searchInput.value));
        }
    }
});
