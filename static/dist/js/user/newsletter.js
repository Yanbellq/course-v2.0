import showNotification from './toast.js';

// ============ NEWSLETTER SUBSCRIPTION ============
const newsletterForm = document.getElementById('newsletterForm');

if (newsletterForm) {
    newsletterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const emailInput = newsletterForm.querySelector('input[type="email"]');
        const submitButton = newsletterForm.querySelector('button[type="submit"]');
        const email = emailInput.value.trim();

        if (!email) {
            showNotification('Please enter your email address', 'error');
            return;
        }

        // Валідація email на клієнті
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(email)) {
            showNotification('Please enter a valid email address', 'error');
            return;
        }

        // Блокуємо кнопку під час відправки
        const originalButtonText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Subscribing...';

        try {
            console.log('Sending newsletter subscription request for:', email);
            const response = await fetch('/api/newsletter/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            console.log('Newsletter subscription response status:', response.status);

            let data;
            try {
                data = await response.json();
            } catch (jsonError) {
                console.error('Failed to parse JSON response:', jsonError);
                const text = await response.text();
                console.error('Response text:', text);
                showNotification('Server error. Please try again later.', 'error');
                return;
            }

            console.log('Newsletter subscription response data:', data);

            if (data.success) {
                showNotification(data.message || 'Thank you for subscribing!', 'success');
                newsletterForm.reset();
            } else {
                showNotification(data.message || 'An error occurred. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Newsletter subscription error:', error);
            showNotification('Network error. Please check your connection and try again.', 'error');
        } finally {
            // Розблоковуємо кнопку
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });
}

//# sourceMappingURL=newsletter.js.map
