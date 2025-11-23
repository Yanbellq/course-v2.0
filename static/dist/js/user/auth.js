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
const loginSubmitBtn = document.getElementById('login-submit');

if (userLoginForm) {
    userLoginForm.addEventListener('submit', async (e) => {
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

        // Disable submit button
        loginSubmitBtn.disabled = true;
        loginSubmitBtn.innerText = 'Logging in...';

        try {
            const response = await fetch(`/api/user/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',  // Важливо для cookies на Render
                body: JSON.stringify({ username, password })
            });
            if (!response.ok) {
                throw 'Login failed. Please check your credentials.'
            }
            
            // Save user data
            const userData = await response.json();
            
            if (remember) {
                localStorage.setItem('user', JSON.stringify(userData.data));
            } else {
                sessionStorage.setItem('user', JSON.stringify(userData.data));
            }
            
            showNotification('Login successful!', 'success');
            console.log(userData);
            
            // Redirect to next URL or default to profile
            const urlParams = new URLSearchParams(window.location.search);
            const nextUrl = urlParams.get('next') || '/profile/';
            
            setTimeout(() => {
                window.location.href = nextUrl;
            }, 500);

        } catch (error) {
            showNotification(error, 'error');
        } finally {
            loginSubmitBtn.disabled = false;
            loginSubmitBtn.innerText = 'Login';
        }
    });
}

// ============ USER REGISTRATION ============
const userRegisterForm = document.getElementById('userRegisterForm');
const regSubmitBtn = document.getElementById('reg-submit');

if (userRegisterForm) {
    userRegisterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(userRegisterForm);
        const username = formData.get('username');
        const email = formData.get('email');
        const password = formData.get('password');
        const confirm = formData.get('confirm');
        const terms = formData.get('terms');
        
        // Validate
        if (!username || !email || !password || !confirm) {
            showNotification('Please fill in all fields', 'error');
            return;
        }
        
        if (password.length < 6) {
            showNotification('Password must be at least 6 characters', 'error');
            return;
        }
        
        if (password !== confirm) {
            showNotification('Passwords do not match', 'error');
            return;
        }
        
        if (!terms) {
            showNotification('Please accept the terms and conditions', 'error');
            return;
        }

        // Disable submit button
        regSubmitBtn.disabled = true;
        regSubmitBtn.innerText = 'Registering...';

        try {
            const resp = await fetch(`/api/user/auth/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',  // Важливо для cookies на Render
                body: JSON.stringify({
                    username,
                    email,
                    password,
                    password_confirm: confirm,
                })
            });
    
            if (!resp.ok) {
                throw 'Registration failed. Please check your credentials. Or try again later.'
            }
            
            // Save user data
            const userData = await resp.json();
            
            sessionStorage.setItem('user', JSON.stringify(userData.data));
            
            showNotification('Registration successful!', 'success');
            console.log(userData);
            
            setTimeout(() => {
                window.location.href = '/profile/';
            }, 500);

        } catch (error) {
            showNotification(error, 'error');
        } finally {
            // Disable submit button
            regSubmitBtn.disabled = false;
            regSubmitBtn.innerText = 'Create Account';
        }
    });
}

// ============ ADMIN LOGIN ============
const adminLoginForm = document.getElementById('adminLoginForm');
const adminSubmitBtn = document.getElementById('admin-submit');

if (adminLoginForm) {
    adminLoginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(adminLoginForm);
        const username = formData.get('username');
        const password = formData.get('password');
        
        // Validate
        if (!username || !password) {
            showNotification('Please fill in all fields', 'error');
            return;
        }

        adminSubmitBtn.disabled = true;
        adminSubmitBtn.innerText = 'Logging in...';
        
        try {
            const resp = await fetch(`/api/user/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',  // Важливо для cookies на Render
                body: JSON.stringify({
                    username,
                    password,
                })
            });
            
            if (!resp.ok) {
                throw 'Login failed. Please check your credentials. Or try again later.'
            }
            
            // Save admin data
            const adminData = await resp.json();

            if (adminData.data.user.role !== 'operator' && adminData.data.user.role !== 'admin') {
                throw 'You are not authorized to access the admin panel.'
            }
            
            sessionStorage.setItem('admin', JSON.stringify(adminData.data));
            
            showNotification('Login successful!', 'success');
            
            setTimeout(() => {
                window.location.href = `/crm/`;
            }, 500);
        } catch (error) {
            showNotification(error, 'error');
        } finally {
            adminSubmitBtn.disabled = false;
            adminSubmitBtn.innerText = 'Admin Login';
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
//# sourceMappingURL=auth.js.map
