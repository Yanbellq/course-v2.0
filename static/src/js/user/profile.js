import showNotification from './toast.js';

const username = document.getElementById('username')
const email = document.getElementById('email')
const currentPassword = document.getElementById('current-password')
const newPassword = document.getElementById('new-password')
const confirmPassword = document.getElementById('confirm-new-password')
const changeProfileBtn = document.getElementById('changeProfileBtn')

// Завантажуємо дані користувача
const data_session = JSON.parse(sessionStorage.getItem('user'))
const data_local = JSON.parse(localStorage.getItem('user'))
if (data_session) {
    username.value = data_session.user.username
    email.value = data_session.user.email
} else if (data_local) {
    username.value = data_local.user.username
    email.value = data_local.user.email
}

// Обробка зміни паролю
if (changeProfileBtn) {
    changeProfileBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        // Перевіряємо, чи заповнені поля для зміни паролю
        const hasPasswordFields = currentPassword.value || newPassword.value || confirmPassword.value;
        
        if (hasPasswordFields) {
            // Валідація полів паролю
            if (!currentPassword.value) {
                showNotification('Enter current password', 'error');
                return;
            }
            
            if (!newPassword.value) {
                showNotification('Enter new password', 'error');
                return;
            }
            
            if (newPassword.value.length < 6) {
                showNotification('New password must be at least 6 characters long', 'error');
                return;
            }
            
            if (newPassword.value !== confirmPassword.value) {
                showNotification('New passwords do not match', 'error');
                return;
            }
            
            // Відправляємо запит на зміну паролю
            try {
                changeProfileBtn.disabled = true;
                changeProfileBtn.textContent = 'Saving...';
                
                const response = await fetch('/api/user/auth/change-password/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include', // Важливо для cookies з access_token
                    body: JSON.stringify({
                        current_password: currentPassword.value,
                        new_password: newPassword.value,
                        confirm_password: confirmPassword.value
                    })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Error changing password');
                }
                
                if (data.success) {
                    showNotification('Password changed successfully!', 'success');
                    
                    // Очищаємо поля паролю
                    currentPassword.value = '';
                    newPassword.value = '';
                    confirmPassword.value = '';
                } else {
                    throw new Error(data.error || 'Error changing password');
                }
                
            } catch (error) {
                console.error('Change password error:', error);
                showNotification(error.message || 'Error changing password. Please try again.', 'error');
            } finally {
                changeProfileBtn.disabled = false;
                changeProfileBtn.textContent = 'Save changes';
            }
        } else {
            // Якщо поля паролю не заповнені, можна додати логіку для оновлення інших даних
            showNotification('To change the password, fill in the password fields', 'info');
        }
    });
}