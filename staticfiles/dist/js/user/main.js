import showNotification from './toast.js';


// ============ MOBILE MENU ============
const mobileToggle = document.getElementById('mobileToggle');
const navMenu = document.getElementById('navMenu');

if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        mobileToggle.classList.toggle('active');
    });
}

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.navbar') && navMenu) {
        navMenu.classList.remove('active');
        if (mobileToggle) mobileToggle.classList.remove('active');
    }
});

// ============ SEARCH OVERLAY ============
const searchToggle = document.getElementById('searchToggle');
const searchOverlay = document.getElementById('searchOverlay');
const searchClose = document.getElementById('searchClose');
const searchInput = document.getElementById('searchInput');

if (searchToggle) {
    searchToggle.addEventListener('click', () => {
        searchOverlay.classList.toggle('active');
        searchInput.focus();
    });
}

if (searchClose) {
    const resultsContainer = document.getElementById('searchResults');

    searchClose.addEventListener('click', () => {
        // searchOverlay.classList.remove('active');
        searchInput.value = '';
        if (resultsContainer) resultsContainer.innerHTML = '';
    });
}

document.addEventListener('click', (e) => {
    if (
        searchOverlay &&
        !e.target.closest('.navbar') &&
        !e.target.closest('#searchOverlay')
    ) {
        searchOverlay.classList.remove('active');
        if (searchInput) searchInput.value = '';
    }
});

// Search functionality
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const resultsContainer = document.getElementById('searchResults');

        if (query.length > 2) {
            // Mock search results
            const products = [
                { name: 'iPhone 15 Pro', price: 999.99, image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500' },
                { name: 'MacBook Pro', price: 1999.99, image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500' },
                { name: 'Sony Headphones', price: 399.99, image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500' },
                { name: 'Canon Camera', price: 899.99, image: 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500' }
            ];

            const filtered = products.filter(p => p.name.toLowerCase().includes(query));

            if (filtered.length > 0) {
                resultsContainer.innerHTML = filtered.map(product => `
                    <a href="#" class="search-result-item">
                        <div class="search-result-image-container">
                            <img src="${product.image}" alt="${product.name}" class="search-result-image">
                        </div>
                        <div class="search-result-info">
                            <h4>${product.name}</h4>
                            <p>$${product.price.toFixed(2)}</p>
                        </div>
                    </a>
                `).join('');
            } else {
                resultsContainer.innerHTML = '<p style="padding: 20px; text-align: center; color: #666; font-size: 15px;">No results found</p>';
            }
        } else {
            resultsContainer.innerHTML = '';
        }
    });
}

// ============ ACCORDION ============
const accordionHeaders = document.querySelectorAll('.accordion-header');

accordionHeaders.forEach(header => {
    header.addEventListener('click', () => {
        const item = header.parentElement;
        const wasActive = item.classList.contains('active');

        // Close all accordion items
        document.querySelectorAll('.accordion-item').forEach(i => {
            i.classList.remove('active');
        });

        // Open clicked item if it wasn't active
        if (!wasActive) {
            item.classList.add('active');
        }
    });
});

// ============ USER BUTTON ============
// const userBtn = document.getElementById('userBtn');
//
// if (userBtn) {
//     userBtn.addEventListener('click', () => {
//         window.location.href = '/auth/';
//     });
// }

// ============ NEWSLETTER ============
const newsletterForm = document.getElementById('newsletterForm');

if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = newsletterForm.querySelector('input').value;

        if (email) {
            alert(`Thank you for subscribing with: ${email}`);
            newsletterForm.reset();
        }
    });
}

// ============ PRODUCTS GENERATION ============
const products = [
    { id: 1, name: 'Premium Headphones', status: 'In stock', price: 299.99, rating: 3, image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500' },
    { id: 2, name: 'MacBook Pro', status: 'In stock', price: 1999.99, rating: 5, image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500' },
    { id: 3, name: 'Digital Camera', status: 'In stock', price: 899.99, rating: 5, image: 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500' },
    { id: 4, name: 'Smart Watch', status: 'In stock', price: 399.99, rating: 4, image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500' },
    { id: 5, name: 'iPhone 15 Pro', status: 'In stock', price: 999.99, rating: 5, image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500' },
    { id: 6, name: 'Wireless Earbuds', status: 'In stock', price: 249.99, rating: 3, image: 'https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7?w=500' },
    { id: 7, name: 'Gaming Laptop', status: 'In stock', price: 1599.99, rating: 4, image: 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500' },
    { id: 8, name: 'Tablet Pro', status: 'In stock', price: 799.99, rating: 2, image: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500' }
];

const productsGrid = document.getElementById('productsGrid');

if (productsGrid) {
    productsGrid.innerHTML = products.map(product => `
        <div class="catalog-product-card">

            <div class="product-image">
                <img src="${product.image}" alt="${product.name}">
                <div class="product-badge">${product.status}</div>
                <button class="product-like">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M10 17L3 10C1 8 1 5 3 3C5 1 8 1 10 3C12 1 15 1 17 3C19 5 19 8 17 10L10 17Z"
                            stroke="white" stroke-width="1.5" fill="none" />
                    </svg>    
                </button>
            </div>

            <div class="product-details">
                <div class="product-rating">${'★'.repeat(product.rating)}${'☆'.repeat(5 - product.rating)}</div>
                <h4>${product.name}</h4>
                <p class="product-price">$${product.price.toFixed(2)}</p>
                <button class="btn-add-cart" data-id="${product.id}" data-name="${product.name}" data-price="${product.price}" data-image="${product.image}">
                    Add to Cart
                </button>
            </div>
            
        </div>
    `).join('');
}

// Product Like Buttons
const likeButtons = document.querySelectorAll('.product-like');

likeButtons.forEach(btn => {
    btn.addEventListener('click', function () {
        this.classList.toggle('liked');
        const svg = this.querySelector('svg path');
        if (this.classList.contains('liked')) {
            svg.setAttribute('fill', 'white');
        } else {
            svg.setAttribute('fill', 'none');
        }
    });
});

// ============ SMOOTH SCROLL ============
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                if (navMenu) navMenu.classList.remove('active');
                if (mobileToggle) mobileToggle.classList.remove('active');
            }
        }
    });
});

// ============ SCROLL ANIMATIONS ============
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'all 0.6s ease-out';
    observer.observe(section);
});

const scrollToTopBtn = document.getElementById("scrollToTopBtn");
const logoScrollToTopBtn = document.getElementById("logoScrollToTop");

// ============ Scroll to top button functionality ============
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
    if (navMenu) navMenu.classList.remove('active');
    if (mobileToggle) mobileToggle.classList.remove('active');
}

if (scrollToTopBtn) {
    scrollToTopBtn.addEventListener("click", scrollToTop);
}

if (logoScrollToTopBtn) {
    logoScrollToTopBtn.addEventListener("click", scrollToTop);
}


// ============ CHECK IF USER IS LOGGED IN ============
function checkAuth() {
    const user = localStorage.getItem('user') || sessionStorage.getItem('user');
    const admin = localStorage.getItem('admin') || sessionStorage.getItem('admin');

    if (user || admin) {
        const userData = JSON.parse(user || admin);
        console.log('Logged in as:', userData);

        // Update UI if on main page
        const userBtn = document.getElementById('userBtn');
        if (userBtn && userData.username) {
            userBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <circle cx="10" cy="7" r="4"/>
                    <path d="M3 19C3 15 6 13 10 13C14 13 17 15 17 19"/>
                </svg>
            `;
            userBtn.title = `Logged in as ${userData.username || userData.email}`;
        }
    }
}

// Check auth on page load
checkAuth();

// ============ LOGOUT FUNCTIONALITY ============
function logout() {
    localStorage.removeItem('user');
    localStorage.removeItem('admin');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('admin');

    showNotification('Logged out successfully', 'success');

    setTimeout(() => {
        if (window.location.pathname.includes('index.html')) {
            window.location.reload();
        } else {
            window.location.href = 'index.html';
        }
    }, 1000);
}

// Add logout button functionality (you can add this to the header)
document.addEventListener('DOMContentLoaded', () => {
    const user = localStorage.getItem('user') || sessionStorage.getItem('user');
    const admin = localStorage.getItem('admin') || sessionStorage.getItem('admin');

    if (user || admin) {
        // Create a logout button in the header

        const userBtn = document.getElementById('userBtn');
        const navIcons = document.getElementById('navIcons');

        const header = document.querySelector('header') || document.body;
        let logoutBtn = document.getElementById('logoutBtn');
        if (!logoutBtn) {
            logoutBtn = document.createElement('button');
            logoutBtn.id = 'logoutBtn';
            logoutBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M7 2H3C2.44772 2 2 2.44772 2 3V17C2 17.5523 2.44772 18 3 18H7"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                    <path d="M13 14L18 10M18 10L13 6M18 10H7" stroke="currentColor" stroke-width="2"
                        stroke-linecap="round" stroke-linejoin="round" />
                </svg>
            `;
            logoutBtn.classList.add('icon-btn', 'logout-btn');
            logoutBtn.addEventListener('click', logout);
            navIcons.appendChild(logoutBtn);
        }

        // <button class="icon-btn logout-btn" id="logoutBtn" aria-label="Logout">
        //     <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        //         <path d="M7 2H3C2.44772 2 2 2.44772 2 3V17C2 17.5523 2.44772 18 3 18H7"
        //             stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        //         <path d="M13 14L18 10M18 10L13 6M18 10H7" stroke="currentColor" stroke-width="2"
        //             stroke-linecap="round" stroke-linejoin="round" />
        //     </svg>
        // </button>
        console.log('User is logged in. Add logout button to UI.');
    }
});//# sourceMappingURL=main.js.map
