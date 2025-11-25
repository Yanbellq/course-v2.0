// static/src/js/crm/crm.js

import showNotification from "../user/toast.js";

// ============ ADMIN LOGOUT FUNCTIONALITY ============
async function adminLogout() {
    try {
        const admin = sessionStorage.getItem('admin') || localStorage.getItem('admin');
        
        if (admin) {
            const adminData = JSON.parse(admin);
            
            // Викликаємо logout endpoint
            try {
                await fetch('/api/user/auth/logout/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${adminData.tokens?.access || ''}`
                    },
                    credentials: 'include'
                });
            } catch (err) {
                console.warn('Logout API call failed:', err);
                // Продовжуємо навіть якщо API виклик не вдався
            }
        }
        
        // Видаляємо дані адміна зі storage
        sessionStorage.removeItem('admin');
        localStorage.removeItem('admin');
        
        // Видаляємо cookies (якщо є)
        document.cookie.split(";").forEach(function(c) { 
            document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
        });
        
        showNotification('You have been logged out successfully', 'success');
        
        // Перенаправляємо на сторінку авторизації
        setTimeout(() => {
            window.location.href = '/auth/';
        }, 500);
        
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('Logout error', 'error');
        
        // Навіть при помилці видаляємо дані і перенаправляємо
        sessionStorage.removeItem('admin');
        localStorage.removeItem('admin');
        setTimeout(() => {
            window.location.href = '/auth/';
        }, 1000);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // ============ DELETE FORMS ============
    const deleteForms = document.querySelectorAll("form.delete-item");

    deleteForms.forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const url = form.action;  // Django URL /crm/***/delete/ID/

            const csrf = form.querySelector("input[name='csrfmiddlewaretoken']")?.value;

            try {
                const response = await fetch(url, {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "X-CSRFToken": csrf,
                        "Accept": "application/json",
                    },
                });

                const data = await response.json();

                if (data.success) {
                    showNotification("Successfully deleted");

                    // Видаляємо HTML-рядок
                    const row = form.closest("tr");
                    if (row) row.remove();
                } else {
                    showNotification("Delete error", "error");
                }
            } catch (err) {
                console.error("Delete error:", err);
                showNotification(`Request error ${err}`, "error");
            }
        });
    });
    
    // ============ ADMIN LOGOUT BUTTON ============
    const adminLogoutBtn = document.getElementById('adminLogoutBtn');
    if (adminLogoutBtn) {
        adminLogoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            adminLogout();
        });
    }
});
//# sourceMappingURL=crm.js.map
