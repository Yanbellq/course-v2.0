// ============ CART FUNCTIONALITY ============
import showNotification from "./toast.js";

class ShoppingCart {
    constructor() {
        this.items = this.loadCart();
        this.cartSidebar = document.getElementById('cartSidebar');
        this.cartToggle = document.getElementById('cartToggle');
        this.cartClose = document.getElementById('cartClose');
        this.continueShopping = document.getElementById('continueShopping');
        this.overlay = document.getElementById('overlay');
        this.cartCount = document.getElementById('cartCount');
        this.cartItems = document.getElementById('cartItems');
        this.cartSubtotal = document.getElementById('cartSubtotal');
        this.cartTotal = document.getElementById('cartTotal');

        this.init();
    }

    init() {
        // Load cart from localStorage
        this.updateUI();

        // Event listeners
        if (this.cartToggle) {
            this.cartToggle.addEventListener('click', () => this.openCart());
        }

        if (this.cartClose) {
            this.cartClose.addEventListener('click', () => this.closeCart());
        }

        if (this.continueShopping) {
            this.continueShopping.addEventListener('click', () => this.closeCart());
        }

        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.closeCart());
        }

        // Add to cart buttons
        this.setupAddToCartButtons();
    }

    setupAddToCartButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn--add-cart')) {
                const btn = e.target;

                // ✅ Безпечний пошук інпуту з кількістю
                const container = btn.closest('.product-actions');
                let quantity = 1; // значення за замовчуванням

                if (container) {
                    const qtyInput = container.querySelector('#quantity');
                    if (qtyInput && qtyInput.value) {
                        quantity = parseInt(qtyInput.value) || 1;
                    }
                }

                const product = {
                    id: btn.dataset.id,
                    name: btn.dataset.name,
                    price: parseFloat(btn.dataset.price),
                    image: btn.dataset.image,
                    quantity: quantity
                };

                this.addItem(product);
                showNotification('Product added to cart!');
            }
        });
    }



    addItem(product) {
        const existingItem = this.items.find(item => item.id === product.id);

        if (existingItem) {
            existingItem.quantity += product.quantity; // ✅ тепер коректно додає кількість
        } else {
            this.items.push(product);
        }

        this.saveCart();
        this.updateUI();
    }


    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.saveCart();
        this.updateUI();
    }

    updateQuantity(productId, newQuantity) {
        const item = this.items.find(item => item.id === productId);

        if (item) {
            if (newQuantity <= 0) {
                this.removeItem(productId);
            } else {
                item.quantity = newQuantity;
                this.saveCart();
                this.updateUI();
            }
        }
    }

    getTotal() {
        return this.items.reduce((total, item) => {
            return total + (item.price * item.quantity);
        }, 0);
    }

    updateUI() {
        // Update cart count
        const totalItems = this.items.reduce((sum, item) => sum + item.quantity, 0);
        if (this.cartCount) {
            this.cartCount.textContent = totalItems;
            this.cartCount.style.display = totalItems > 0 ? 'flex' : 'none';
        }

        // Update cart items
        if (this.cartItems) {
            if (this.items.length === 0) {
                this.cartItems.innerHTML = `
                    <div class="cart-empty">
                        <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
                            <circle cx="40" cy="40" r="38" stroke="#e0e0e0" stroke-width="4"/>
                            <path d="M30 50L50 30M50 50L30 30" stroke="#e0e0e0" stroke-width="4" stroke-linecap="round"/>
                        </svg>
                        <p style='font-size: 15px;'>Your cart is empty</p>
                    </div>
                `;
            } else {
                this.cartItems.innerHTML = this.items.map(item => `
                    <div class="cart-item" data-id="${item.id}">
                        <div class="cart-item-image">
                            <img src="${item.image}" alt="${item.name}">
                        </div>
                        <div class="cart-item-info">
                            <h4>${item.name}</h4>
                            <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                            <div class="cart-item-quantity">
                                <button class="qty-btn qty-minus" data-id="${item.id}">-</button>
                                <span class="qty-value">${item.quantity}</span>
                                <button class="qty-btn qty-plus" data-id="${item.id}">+</button>
                            </div>
                        </div>
                        <button class="cart-item-remove" data-id="${item.id}">×</button>
                    </div>
                `).join('');

                // Add event listeners for quantity buttons
                this.setupCartItemButtons();
            }
        }

        // Update totals
        const total = this.getTotal();
        if (this.cartSubtotal) {
            this.cartSubtotal.textContent = `$${total.toFixed(2)}`;
        }
        if (this.cartTotal) {
            this.cartTotal.textContent = `$${total.toFixed(2)}`;
        }
    }

    setupCartItemButtons() {
        // Remove buttons
        document.querySelectorAll('.cart-item-remove').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                this.removeItem(id);
                showNotification('Product removed from cart');
            });
        });

        // Quantity buttons
        document.querySelectorAll('.qty-minus').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const item = this.items.find(item => item.id === id);
                if (item) {
                    this.updateQuantity(id, item.quantity - 1);
                }
            });
        });

        document.querySelectorAll('.qty-plus').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = btn.dataset.id;
                const item = this.items.find(item => item.id === id);
                if (item) {
                    this.updateQuantity(id, item.quantity + 1);
                }
            });
        });
    }

    openCart() {
        if (this.cartSidebar) {
            this.cartSidebar.classList.add('active');
        }
        if (this.overlay) {
            this.overlay.classList.add('active');
        }
        document.body.style.overflow = 'hidden';
    }

    closeCart() {
        if (this.cartSidebar) {
            this.cartSidebar.classList.remove('active');
        }
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }
        document.body.style.overflow = '';
    }

    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    }

    loadCart() {
        const saved = localStorage.getItem('cart');
        return saved ? JSON.parse(saved) : [];
    }

    clearCart() {
        this.items = [];
        this.saveCart();
        this.updateUI();
    }

    async checkout(paymentMethod = 'card', deliveryAddress = '', notes = '') {
        // Перевірка авторизації
        const user = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (!user) {
            showNotification('Please login to the system to place an order', 'error');
            // Перенаправлення на сторінку входу
            setTimeout(() => {
                window.location.href = '/auth/?next=' + encodeURIComponent(window.location.pathname);
            }, 1500);
            return;
        }

        if (this.items.length === 0) {
            showNotification('Your cart is empty!', 'error');
            return;
        }

        // Підготовка даних для API
        const products = this.items.map(item => ({
            product_id: item.id,
            quantity: item.quantity,
            unit_price: item.price
        }));

        const orderData = {
            products: products,
            payment_method: paymentMethod,
            delivery_address: deliveryAddress,
            notes: notes
        };

        // Показуємо індикатор завантаження
        const checkoutBtn = document.querySelector('.btn--checkout');
        const originalText = checkoutBtn ? checkoutBtn.textContent : 'Proceed to Checkout';
        
        try {
            if (checkoutBtn) {
                checkoutBtn.disabled = true;
                checkoutBtn.textContent = 'Processing...';
            }

            const response = await fetch('/api/order/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Важливо для cookies з access_token
                body: JSON.stringify(orderData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.detail || 'Error creating order');
            }

            if (data.success) {
                showNotification('Order successfully created!', 'success');
                
                // Очищаємо корзину
                this.clearCart();
                
                // Закриваємо корзину
                this.closeCart();
                
                // Опціонально: перенаправлення на сторінку профілю або підтвердження
                setTimeout(() => {
                    window.location.href = '/profile/';
                }, 2000);
            } else {
                throw new Error(data.error || 'Error creating order');
            }

        } catch (error) {
            console.error('Checkout error:', error);
            showNotification(error.message || 'Error creating order. Please try again.', 'error');
        } finally {
            // Відновлюємо кнопку
            if (checkoutBtn) {
                checkoutBtn.disabled = false;
                checkoutBtn.textContent = originalText;
            }
        }
    }
}

// Initialize cart
const cart = new ShoppingCart();

// Checkout button
document.addEventListener('click', async (e) => {
    if (e.target.classList.contains('btn--checkout')) {
        e.preventDefault();
        
        if (cart.items.length === 0) {
            showNotification('Your cart is empty!', 'error');
            return;
        }

        // Простий спосіб: використовуємо модальне вікно для введення даних
        const deliveryAddress = prompt('Enter delivery address (or leave empty):') || '';
        const paymentMethod = prompt('Select payment method:\n1 - Card\n2 - Cash\n3 - Transfer\n\nEnter number (1-3):', '1');
        
        let paymentMethodValue = 'card';
        if (paymentMethod === '2') {
            paymentMethodValue = 'cash';
        } else if (paymentMethod === '3') {
            paymentMethodValue = 'transfer';
        }

        await cart.checkout(paymentMethodValue, deliveryAddress);
    }
});
//# sourceMappingURL=cart.js.map
