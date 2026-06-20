document.addEventListener('DOMContentLoaded', () => {

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
});
