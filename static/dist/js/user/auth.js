import showNotification from "./toast.js";
import { env } from "./env.js";
// ============ AUTH PAGE FUNCTIONALITY ============

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initAuthPage();
});

// Also run immediately if DOM is already loaded (for modules)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuthPage);
} else {
    initAuthPage();
}

function initAuthPage() {
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
            const targetContainer = document.getElementById(targetTab + 'Tab');
            if (targetContainer) {
                targetContainer.classList.add('active');
            }
        });
    });

    // Switch between login, register, forgot password, and reset password forms
    const showRegisterBtn = document.getElementById('showRegister');
    const showLoginBtn = document.getElementById('showLogin');
    const showForgotPasswordBtn = document.getElementById('showForgotPassword');
    const showLoginFromForgotBtn = document.getElementById('showLoginFromForgot');
    const showLoginFromResetBtn = document.getElementById('showLoginFromReset');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    const resetPasswordForm = document.getElementById('resetPasswordForm');

    // Helper function to hide all forms and show specific one
    function showForm(formToShow) {
        [loginForm, registerForm, forgotPasswordForm, resetPasswordForm].forEach(form => {
            if (form) form.classList.remove('active');
        });
        if (formToShow) {
            formToShow.classList.add('active');
        }
    }

    if (showRegisterBtn) {
        showRegisterBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(registerForm);
        });
    }

    if (showLoginBtn) {
        showLoginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(loginForm);
        });
    }

    if (showForgotPasswordBtn) {
        showForgotPasswordBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Forgot password clicked, showing form');
            if (forgotPasswordForm) {
                showForm(forgotPasswordForm);
            } else {
                console.error('forgotPasswordForm not found');
            }
        });
    }

    if (showLoginFromForgotBtn) {
        showLoginFromForgotBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(loginForm);
        });
    }

    if (showLoginFromResetBtn) {
        showLoginFromResetBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(loginForm);
        });
    }

    // Check if reset token is in URL
    const urlParams = new URLSearchParams(window.location.search);
    const resetToken = urlParams.get('token');
    if (resetToken && resetPasswordForm) {
        // Set token in hidden input
        const tokenInput = document.getElementById('reset-token');
        if (tokenInput) {
            tokenInput.value = resetToken;
            showForm(resetPasswordForm);
        }
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

    // ============ FORGOT PASSWORD ============
    const forgotPasswordFormElement = document.getElementById('forgotPasswordFormElement');
    const forgotSubmitBtn = document.getElementById('forgot-submit');

if (forgotPasswordFormElement) {
    forgotPasswordFormElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(forgotPasswordFormElement);
        const emailOrUsername = formData.get('email_or_username');
        
        // Validate
        if (!emailOrUsername) {
            showNotification('Please enter your email or username', 'error');
            return;
        }

        // Disable submit button
        forgotSubmitBtn.disabled = true;
        forgotSubmitBtn.innerText = 'Sending...';

        try {
            const response = await fetch(`/api/user/auth/forgot-password/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    email: emailOrUsername.includes('@') ? emailOrUsername : null,
                    username: emailOrUsername.includes('@') ? null : emailOrUsername
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw data.error || 'Failed to send reset link. Please try again.';
            }
            
            showNotification(data.message || 'If an account exists, a password reset link has been sent.', 'success');
            
            // In development, show token if available
            if (data.data && data.data.token) {
                console.log('Reset Token (DEV):', data.data.token);
                console.log('Reset URL (DEV):', data.data.reset_url);
            }
            
            // Clear form
            forgotPasswordFormElement.reset();
            
            // Optionally redirect to login after a delay
            setTimeout(() => {
                showForm(loginForm);
            }, 2000);

        } catch (error) {
            showNotification(error, 'error');
        } finally {
            forgotSubmitBtn.disabled = false;
            forgotSubmitBtn.innerText = 'Send Reset Link';
        }
    });
    }

    // ============ RESET PASSWORD ============
    const resetPasswordFormElement = document.getElementById('resetPasswordFormElement');
    const resetSubmitBtn = document.getElementById('reset-submit');

if (resetPasswordFormElement) {
    resetPasswordFormElement.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(resetPasswordFormElement);
        const token = formData.get('token');
        const newPassword = formData.get('new_password');
        const confirmPassword = formData.get('confirm_password');
        
        // Validate
        if (!token) {
            showNotification('Reset token is missing', 'error');
            return;
        }
        
        if (!newPassword || !confirmPassword) {
            showNotification('Please fill in all fields', 'error');
            return;
        }
        
        if (newPassword.length < 6) {
            showNotification('Password must be at least 6 characters', 'error');
            return;
        }
        
        if (newPassword !== confirmPassword) {
            showNotification('Passwords do not match', 'error');
            return;
        }

        // Disable submit button
        resetSubmitBtn.disabled = true;
        resetSubmitBtn.innerText = 'Resetting...';

        try {
            const response = await fetch(`/api/user/auth/reset-password/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    token,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw data.error || 'Failed to reset password. Please try again.';
            }
            
            showNotification(data.message || 'Password reset successfully!', 'success');
            
            // Clear form
            resetPasswordFormElement.reset();
            
            // Redirect to login after a delay
            setTimeout(() => {
                showForm(loginForm);
                // Remove token from URL
                window.history.replaceState({}, document.title, window.location.pathname);
            }, 1500);

        } catch (error) {
            showNotification(error, 'error');
        } finally {
            resetSubmitBtn.disabled = false;
            resetSubmitBtn.innerText = 'Reset Password';
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
}
//# sourceMappingURL=auth.js.map
