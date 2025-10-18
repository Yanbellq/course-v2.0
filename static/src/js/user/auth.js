import showNotification from "./toast.js";
import { env } from "./env.js";
// ============ AUTH PAGE FUNCTIONALITY ============

// Tab switching
const authTabs = document.querySelectorAll('.auth-tab');
const authContainers = document.querySelectorAll('.auth-form-container');

authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;
        
        // Remove active class from all tabs and containers
        authTabs.forEach(t => t.classList.remove('active'));
        authContainers.forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked tab and corresponding container
        tab.classList.add('active');
        document.getElementById(targetTab + 'Tab').classList.add('active');
    });
});

// Switch between login and register forms
const showRegisterBtn = document.getElementById('showRegister');
const showLoginBtn = document.getElementById('showLogin');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

if (showRegisterBtn) {
    showRegisterBtn.addEventListener('click', () => {
        loginForm.classList.remove('active');
        registerForm.classList.add('active');
    });
}

if (showLoginBtn) {
    showLoginBtn.addEventListener('click', () => {
        registerForm.classList.remove('active');
        loginForm.classList.add('active');
    });
}

// ============ USER LOGIN ============
const userLoginForm = document.getElementById('userLoginForm');

if (userLoginForm) {
    userLoginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const formData = new FormData(userLoginForm);
        const username = formData.get('username');
        const password = formData.get('password');
        const remember = formData.get('remember');
        
        // Validate
        if (!username || !password) {
            showNotification('Please fill in all fields', 'error');
            return;
        }
        
        // Mock authentication
        console.log('User Login:', { username, password, remember });
        
        // Save user data
        const userData = {
            type: 'user',
            username: username,
            loginTime: new Date().toISOString()
        };
        
        if (remember) {
            localStorage.setItem('user', JSON.stringify(userData));
        } else {
            sessionStorage.setItem('user', JSON.stringify(userData));
        }
        
        showNotification('Login successful!', 'success');
        
        // Redirect after 1.5 seconds
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1500);
    });
}

// ============ USER REGISTRATION ============
const userRegisterForm = document.getElementById('userRegisterForm');
const regSubmitBtn = document.getElementById('reg-submit');

if (userRegisterForm) {
    userRegisterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const formData = new FormData(userRegisterForm);
        const username = formData.get('username');
        const email = formData.get('email');
        const password = formData.get('password');
        // const confirm = formData.get('confirm');
        const terms = formData.get('terms');
        
        // Validate
        if (!username || !email || !password) {
            showNotification('Please fill in all fields', 'error');
            return;
        }
        
        if (password.length < 6) {
            showNotification('Password must be at least 6 characters', 'error');
            return;
        }
        
        if (!terms) {
            showNotification('Please accept the terms and conditions', 'error');
            return;
        }
        
        // Mock registration
        console.log('User Registration:', { username, email, password });

        // Disable submit button
        regSubmitBtn.disabled = true;
        regSubmitBtn.innerText = 'Registering...';
        
        const resp = fetch(`${env.apiBaseUrl}/api/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        resp.then(res => {
            if (res.status === 201) {
                showNotification('Registration successful!', 'success');
            } else {
                showNotification('Registration failed. Please try again.', 'error');
            }

            // Disable submit button
            regSubmitBtn.disabled = false;
            regSubmitBtn.innerText = 'Create Account';

            userRegisterForm.reset();
        });

        
        // Switch to login form
        // setTimeout(() => {
        //     registerForm.classList.remove('active');
        //     loginForm.classList.add('active');
        //     userRegisterForm.reset();
        // }, 1500);
    });
}

// ============ ADMIN LOGIN ============
const adminLoginForm = document.getElementById('adminLoginForm');

if (adminLoginForm) {
    adminLoginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const formData = new FormData(adminLoginForm);
        const email = formData.get('email');
        const password = formData.get('password');
        const remember = formData.get('remember');
        
        // Validate
        if (!email || !password) {
            showNotification('Please fill in all fields', 'error');
            return;
        }
        
        // Mock admin authentication (you should use proper backend authentication)
        if (email === 'admin@electronic.com' && password === 'admin123') {
            const adminData = {
                type: 'admin',
                email: email,
                loginTime: new Date().toISOString()
            };
            
            if (remember) {
                localStorage.setItem('admin', JSON.stringify(adminData));
            } else {
                sessionStorage.setItem('admin', JSON.stringify(adminData));
            }
            
            showNotification('Admin login successful!', 'success');
            
            setTimeout(() => {
                window.location.href = `${env.apiBaseUrl}/crm/`;
            }, 1500);
        } else {
            showNotification('Invalid admin credentials', 'error');
        }
    });
}

// ============ PASSWORD VISIBILITY TOGGLE ============
document.querySelectorAll('input[type="password"]').forEach(input => {
    const wrapper = input.parentElement;
    const toggleBtn = document.createElement('button');
    toggleBtn.type = 'button';
    toggleBtn.innerHTML = `<i data-lucide="eye-off" class='h-8 w-8'></i>`;
    toggleBtn.style.cssText = `
        position: absolute;
        right: 15px;
        top: 69%;
        transform: translateY(-50%);
        background: none;
        border: none;
        cursor: pointer;
        opacity: 0.6;
    `;
    
    wrapper.style.position = 'relative';
    wrapper.appendChild(toggleBtn);

    lucide.createIcons();
    
    toggleBtn.addEventListener('click', () => {
        if (input.type === 'password') {
            input.type = 'text';
            toggleBtn.innerHTML = `<i data-lucide="eye" class='h-8 w-8'></i>`;
        } else {
            input.type = 'password';
            toggleBtn.innerHTML = `<i data-lucide="eye-off" class='h-8 w-8'></i>`;
        }

        lucide.createIcons();
    });
});
