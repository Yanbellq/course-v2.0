import showNotification from './toast.js';
import debounce from '../utility/debounce.js';

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

const resultsContainer = document.getElementById("searchResults");

async function performSearch(query) {
    if (query.length < 3) {
        resultsContainer.innerHTML = "";
        return;
    }

    const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
    const data = await response.json();

    if (!data.results.length) {
        resultsContainer.innerHTML = `<p style="padding: 20px; text-align: center; color: #666; font-size: 15px;">No results found</p>`;
        return;
    }

    resultsContainer.innerHTML = data.results.map(p => `
        <a href="/product/${p.id}" class="search-result-item">
            <div class="search-result-image-container">
                <img src="${p.image_url}" alt="${p.name}" class="search-result-image">
            </div>
            <div class="search-result-info">
                <h4>${p.name}</h4>
                <p>$${p.price}</p>
            </div>
        </a>
    `).join('');
}

searchInput.addEventListener("input", debounce(e => {
    performSearch(e.target.value);
}, 250));

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
async function logout() {

    const user = localStorage.getItem('user') || sessionStorage.getItem('user');
    const userData = JSON.parse(user);
    
    const resp = await fetch('/api/user/auth/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userData.tokens.access}`
        }
    });

    localStorage.removeItem('user');
    sessionStorage.removeItem('user');

    showNotification('Logged out successfully', 'success');

    setTimeout(() => {
        if (window.location.pathname === '/') {
            window.location.reload();
        } else {
            window.location.href = '/';
        }
    }, 100);
}

// Add logout button functionality (you can add this to the header)
document.addEventListener('DOMContentLoaded', () => {
    const user = localStorage.getItem('user') || sessionStorage.getItem('user');
    const userBtn = document.getElementById('userBtn');

    if (user) {
        // Create a logout button in the header

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

        console.log('User is logged in. Add logout button to UI.');
    }

    if (user) {
        userBtn.href = '/profile/';
    }
});