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
        
        this.scrollAmount = 430; // slide width + gap
        
        this.init();
    }
    
    init() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.scrollPrev());
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.scrollNext());
        }
        
        // Update button states on scroll
        this.slider.addEventListener('scroll', () => this.updateButtons());
        this.updateButtons();
    }
    
    scrollPrev() {
        this.slider.scrollBy({
            left: -this.scrollAmount,
            behavior: 'smooth'
        });
    }
    
    scrollNext() {
        this.slider.scrollBy({
            left: this.scrollAmount,
            behavior: 'smooth'
        });
    }
    
    updateButtons() {
        const scrollLeft = this.slider.scrollLeft;
        const maxScroll = this.slider.scrollWidth - this.slider.clientWidth;
        
        // Disable prev button at start
        if (this.prevBtn) {
            if (scrollLeft <= 0) {
                this.prevBtn.style.opacity = '0.3';
                this.prevBtn.style.pointerEvents = 'none';
            } else {
                this.prevBtn.style.opacity = '1';
                this.prevBtn.style.pointerEvents = 'auto';
            }
        }
        
        // Disable next button at end
        if (this.nextBtn) {
            if (scrollLeft >= maxScroll - 10) {
                this.nextBtn.style.opacity = '0.3';
                this.nextBtn.style.pointerEvents = 'none';
            } else {
                this.nextBtn.style.opacity = '1';
                this.nextBtn.style.pointerEvents = 'auto';
            }
        }
    }
}

// Initialize collections slider
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
