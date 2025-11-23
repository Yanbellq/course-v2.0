// ============ HERO SLIDER ============
class HeroSlider {
    constructor(sliderId) {
        this.slider = document.getElementById(sliderId);
        if (!this.slider) return;

        this.slides = this.slider.querySelectorAll('.hero-slide');
        this.currentSlide = 0;
        this.totalSlides = this.slides.length;

        this.prevBtn = document.getElementById('prevSlide');
        this.nextBtn = document.getElementById('nextSlide');
        this.dotsContainer = document.getElementById('sliderDots');

        this.init();
    }

    init() {
        // Create dots
        this.createDots();

        // Event listeners
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevSlide());
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextSlide());
        }

        // Auto play
        this.startAutoPlay();

        // Pause on hover
        this.slider.addEventListener('mouseenter', () => this.stopAutoPlay());
        this.slider.addEventListener('mouseleave', () => this.startAutoPlay());

        this.dotsContainer.addEventListener('mouseenter', () => this.stopAutoPlay());
        this.dotsContainer.addEventListener('mouseleave', () => this.startAutoPlay());
    }

    createDots() {
        if (!this.dotsContainer) return;

        for (let i = 0; i < this.totalSlides; i++) {
            const dot = document.createElement('button');
            dot.classList.add('slider-dot');
            if (i === 0) dot.classList.add('active');

            dot.addEventListener('click', () => this.goToSlide(i));
            this.dotsContainer.appendChild(dot);
        }
    }

    goToSlide(index) {
        // Remove active class from current slide
        this.slides[this.currentSlide].classList.remove('active');

        // Update current slide
        this.currentSlide = index;

        // Add active class to new slide
        this.slides[this.currentSlide].classList.add('active');

        // Update dots
        this.updateDots();
    }

    nextSlide() {
        const next = (this.currentSlide + 1) % this.totalSlides;
        this.goToSlide(next);
    }

    prevSlide() {
        const prev = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
        this.goToSlide(prev);
    }

    updateDots() {
        if (!this.dotsContainer) return;

        const dots = this.dotsContainer.querySelectorAll('.slider-dot');
        dots.forEach((dot, index) => {
            if (index === this.currentSlide) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    startAutoPlay() {
        this.autoPlayInterval = setInterval(() => {
            this.nextSlide();
        }, 5000);
    }

    stopAutoPlay() {
        clearInterval(this.autoPlayInterval);
    }
}

// Initialize hero slider
const heroSlider = new HeroSlider('heroSlider');

// ============ COLLECTIONS SLIDER ============
class CollectionsSlider {
    constructor(sliderId) {
        this.slider = document.getElementById(sliderId);
        if (!this.slider) return;

        this.prevBtn = document.getElementById('collectionsPrev');
        this.nextBtn = document.getElementById('collectionsNext');
        this.slidesPerScroll = 3;
        this.isAnimating = false;

        this.init();
    }

    init() {
        this.prevBtn?.addEventListener('click', () => this.scroll(-1));
        this.nextBtn?.addEventListener('click', () => this.scroll(1));
        this.slider.addEventListener('scroll', () => this.updateButtons());
        this.updateButtons();
    }

    getSlideMetrics() {
        const firstSlide = this.slider.querySelector(':scope > *');
        if (!firstSlide) return { width: 400, gap: 0 };
        const slideWidth = firstSlide.offsetWidth;
        const gap = parseFloat(window.getComputedStyle(this.slider).gap || 0);
        return { width: slideWidth, gap };
    }

    getScrollAmount() {
        const { width, gap } = this.getSlideMetrics();
        return (width + gap) * this.slidesPerScroll;
    }

    // ⚡ Миттєвий запуск анімації, без затримок
    scroll(direction) {
        if (this.isAnimating) return; // щоб не дублювати кліки
        this.isAnimating = true;

        const start = this.slider.scrollLeft;
        const change = this.getScrollAmount() * direction;
        const target = start + change;
        const duration = 400;
        const startTime = performance.now();

        const easeOut = t => 1 - Math.pow(1 - t, 3);

        const animate = currentTime => {
            const progress = Math.min((currentTime - startTime) / duration, 1);
            this.slider.scrollLeft = start + change * easeOut(progress);

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.isAnimating = false;
                this.updateButtons();
            }
        };

        requestAnimationFrame(animate);
    }

    updateButtons() {
        const scrollLeft = this.slider.scrollLeft;
        const maxScroll = this.slider.scrollWidth - this.slider.clientWidth;
        const atStart = scrollLeft <= 5;
        const atEnd = scrollLeft >= maxScroll - 5;

        if (this.prevBtn) {
            this.prevBtn.classList.toggle('opacity-30', atStart);
            this.prevBtn.classList.toggle('pointer-events-none', atStart);
        }

        if (this.nextBtn) {
            this.nextBtn.classList.toggle('opacity-30', atEnd);
            this.nextBtn.classList.toggle('pointer-events-none', atEnd);
        }
    }
}

const collectionsSlider = new CollectionsSlider('collectionsSlider');





// ============ TOUCH SWIPE SUPPORT ============
function addSwipeSupport(element, onSwipeLeft, onSwipeRight) {
    if (!element) return;

    let touchStartX = 0;
    let touchEndX = 0;

    element.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });

    element.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeThreshold = 50;

        if (touchEndX < touchStartX - swipeThreshold) {
            // Swipe left
            if (onSwipeLeft) onSwipeLeft();
        }

        if (touchEndX > touchStartX + swipeThreshold) {
            // Swipe right
            if (onSwipeRight) onSwipeRight();
        }
    }
}

// Add swipe support to hero slider
if (document.getElementById('heroSlider')) {
    addSwipeSupport(
        document.getElementById('heroSlider'),
        () => heroSlider.nextSlide(),
        () => heroSlider.prevSlide()
    );
}

// Add swipe support to collections slider
if (document.getElementById('collectionsSlider')) {
    const collectionsSliderElement = document.getElementById('collectionsSlider');
    addSwipeSupport(
        collectionsSliderElement,
        () => collectionsSliderElement.scrollBy({ left: 430, behavior: 'smooth' }),
        () => collectionsSliderElement.scrollBy({ left: -430, behavior: 'smooth' })
    );
}

// ============ KEYBOARD NAVIGATION ============
document.addEventListener('keydown', (e) => {
    // Only if no input is focused
    if (document.activeElement.tagName === 'INPUT') return;

    if (e.key === 'ArrowLeft' && heroSlider) {
        heroSlider.prevSlide();
    }

    if (e.key === 'ArrowRight' && heroSlider) {
        heroSlider.nextSlide();
    }
});
//# sourceMappingURL=slider.js.map
