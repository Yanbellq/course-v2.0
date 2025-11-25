/**
 * Система допомоги користувача
 * Відкривається на клавішу F1
 */

class HelpSystem {
    constructor() {
        this.modal = null;
        this.overlay = null;
        this.isOpen = false;
        this.userRole = this.getUserRole();
        
        this.init();
    }

    getUserRole() {
        // Спробуємо отримати роль з різних джерел
        // 1. З data-атрибута на body (якщо передано з сервера)
        const bodyRole = document.body.getAttribute('data-user-role');
        if (bodyRole && bodyRole !== 'guest') return bodyRole;

        // 2. З localStorage/sessionStorage для CRM (admin)
        try {
            const admin = localStorage.getItem('admin') || sessionStorage.getItem('admin');
            if (admin) {
                const adminData = JSON.parse(admin);
                return adminData.role || 'admin';
            }
        } catch (e) {
            console.warn('Could not parse admin from storage:', e);
        }

        // 3. З localStorage/sessionStorage (для API авторизації)
        try {
            const user = localStorage.getItem('user') || sessionStorage.getItem('user');
            if (user) {
                const userData = JSON.parse(user);
                return userData.role || 'user';
            }
        } catch (e) {
            console.warn('Could not parse user from storage:', e);
        }

        // 4. Використовуємо data-атрибут (навіть якщо guest)
        if (bodyRole) return bodyRole;

        // 5. За замовчуванням - guest
        return 'guest';
    }

    init() {
        // Створюємо модальне вікно
        this.createModal();
        
        // Додаємо обробник клавіші F1
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F1') {
                e.preventDefault();
                this.open();
            }
        });

        // Закриваємо при натисканні Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    createModal() {
        // Створюємо overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'help-overlay';
        this.overlay.addEventListener('click', () => this.close());

        // Створюємо модальне вікно
        this.modal = document.createElement('div');
        this.modal.className = 'help-modal';
        this.modal.innerHTML = this.getModalContent();

        // Додаємо кнопку закриття
        const closeBtn = this.modal.querySelector('.help-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Додаємо в DOM
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.modal);
    }

    getModalContent() {
        const role = this.userRole;
        const content = this.getHelpContent(role);

        return `
            <div class="help-modal-header">
                <h2 class="help-title">User Guide</h2>
                <button class="help-close" aria-label="Close">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
            <div class="help-modal-body">
                <div class="help-role-badge">
                    <span class="help-role-label">Your role:</span>
                    <span class="help-role-value help-role-${role}">${this.getRoleName(role)}</span>
                </div>
                ${content}
            </div>
            <div class="help-modal-footer">
                <p class="help-hint">Press <kbd>F1</kbd> to open this guide, <kbd>ESC</kbd> to close</p>
            </div>
        `;
    }

    getRoleName(role) {
        const names = {
            'guest': 'Guest',
            'user': 'User',
            'operator': 'Operator',
            'admin': 'Admin'
        };
        return names[role] || role;
    }

    getHelpContent(role) {
        const contents = {
            'guest': this.getGuestContent(),
            'user': this.getUserContent(),
            'operator': this.getOperatorContent(),
            'admin': this.getAdminContent()
        };
        return contents[role] || contents['guest'];
    }

    getGuestContent() {
        return `
            <div class="help-section">
                <h3 class="help-section-title">What you can do:</h3>
                <ul class="help-list">
                    <li>✅ View the catalog of products and their details</li>
                    <li>✅ View the categories of products</li>
                    <li>✅ Use the product search</li>
                    <li>✅ View the information about the company</li>
                </ul>
            </div>
            <div class="help-section">
                <h3 class="help-section-title">How to get more access:</h3>
                <div class="help-upgrade">
                    <p>To get full access to the system you need to:</p>
                    <ol class="help-steps">
                        <li>Register in the system or login if you already have an account</li>
                        <li>After registration you will get the role <strong>User</strong>, which will allow you to:</li>
                        <ul>
                            <li>Save the search results</li>
                            <li>Execute built-in queries to the database</li>
                            <li>Get access to additional functions</li>
                        </ul>
                    </ol>
                    <div class="help-action">
                        <a href="/auth/" class="btn btn--primary">Register / Login</a>
                    </div>
                </div>
            </div>
        `;
    }

    getUserContent() {
        return `
            <div class="help-section">
                <h3 class="help-section-title">What you can do:</h3>
                <ul class="help-list">
                    <li>✅ View the catalog of products and their details</li>
                    <li>✅ Use the product search</li>
                    <li>✅ View and search data in the system</li>
                    <li>✅ Execute built-in SQL queries and aggregations</li>
                    <li>✅ Save the results of built-in SQL queries</li>
                    <li>✅ View your profile</li>
                </ul>
            </div>
            <div class="help-section">
                <h3 class="help-section-title">Restrictions:</h3>
                <ul class="help-list help-list-restricted">
                    <li>❌ You cannot form new SQL queries</li>
                    <li>❌ You cannot edit or delete data</li>
                    <li>❌ You cannot add new records</li>
                </ul>
            </div>
            <div class="help-section">
                <h3 class="help-section-title">How to get more access:</h3>
                <div class="help-upgrade">
                    <p>To get the rights <strong>Operator</strong> or <strong>Admin</strong> contact the administrator of the system.</p>
                    <p><strong>Operator</strong> can:</p>
                    <ul>
                        <li>Add, edit and delete data</li>
                        <li>Form new SQL queries and aggregations</li>
                        <li>Execute all operations with data</li>
                    </ul>
                </div>
            </div>
        `;
    }

    getOperatorContent() {
        return `
            <div class="help-section">
                <h3 class="help-section-title">What you can do:</h3>
                <ul class="help-list">
                    <li>✅ Add new records to the system</li>
                    <li>✅ View all data</li>
                    <li>✅ Edit existing records</li>
                    <li>✅ Delete records</li>
                    <li>✅ Execute built-in SQL queries and aggregations</li>
                    <li>✅ Form new SQL queries and aggregations</li>
                    <li>✅ Manage suppliers, contracts, deliveries</li>
                    <li>✅ Manage sales, repairs, deliveries</li>
                    <li>✅ Manage products and categories</li>
                </ul>
            </div>
            <div class="help-section">
                <h3 class="help-section-title">Restrictions:</h3>
                <ul class="help-list help-list-restricted">
                    <li>❌ You cannot add operators</li>
                    <li>❌ You cannot register users</li>
                    <li>❌ You cannot change user roles</li>
                </ul>
            </div>
            <div class="help-section">
                <h3 class="help-section-title">How to get more access:</h3>
                <div class="help-upgrade">
                    <p>To get the rights <strong>Admin</strong> contact the administrator of the system.</p>
                    <p><strong>Admin</strong> has all the rights of the operator, plus:</p>
                    <ul>
                        <li>Adding operators</li>
                        <li>Registering users after requests</li>
                        <li>Rejecting registration requests</li>
                        <li>Full control of users and their roles</li>
                    </ul>
                </div>
            </div>
        `;
    }

    getAdminContent() {
        return `
            <div class="help-section">
                <h3 class="help-section-title">What you can do:</h3>
                <ul class="help-list">
                    <li>✅ <strong>All operator rights</strong></li>
                    <li>✅ Adding operators</li>
                    <li>✅ Registering users after requests</li>
                    <li>✅ Rejecting registration requests</li>
                    <li>✅ Forming new SQL queries and aggregations</li>
                    <li>✅ Managing all users and their roles</li>
                    <li>✅ Full access to all system functions</li>
                    <li>✅ Access to analytics and reports</li>
                    <li>✅ Full control of all system entities</li>
                </ul>
            </div>
            <div class="help-section">
                <h3 class="help-section-title">Managing the system:</h3>
                <ul class="help-list">
                    <li>📊 You have access to the CRM panel for managing data</li>
                    <li>👥 You can manage users in the "Users" section</li>
                    <li>📈 You have access to analytics and reports</li>
                    <li>⚙️ You can configure the system and access rights</li>
                </ul>
            </div>
            <div class="help-section">
                <h3 class="help-section-title">Note:</h3>
                <p>You have the highest level of access to the system. Be careful when performing operations, especially when deleting data or changing user roles.</p>
            </div>
        `;
    }

    open() {
        if (this.isOpen) return;
        
        // Оновлюємо роль (на випадок зміни)
        this.userRole = this.getUserRole();
        this.modal.innerHTML = this.getModalContent();
        
        // Додаємо обробник закриття
        const closeBtn = this.modal.querySelector('.help-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Показуємо модальне вікно
        this.overlay.classList.add('active');
        this.modal.classList.add('active');
        this.isOpen = true;
        
        // Блокуємо прокрутку body
        document.body.style.overflow = 'hidden';
    }

    close() {
        if (!this.isOpen) return;
        
        this.overlay.classList.remove('active');
        this.modal.classList.remove('active');
        this.isOpen = false;
        
        // Відновлюємо прокрутку body
        document.body.style.overflow = '';
    }
}

// Ініціалізуємо систему допомоги
document.addEventListener('DOMContentLoaded', () => {
    window.helpSystem = new HelpSystem();
});

export default HelpSystem;

//# sourceMappingURL=help.js.map
