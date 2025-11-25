// ============ FORM VALIDATION UTILITIES ============

/**
 * Показує помилку валідації під полем
 */
export function showFieldError(field, message) {
    // Видаляємо попередню помилку, якщо є
    clearFieldError(field);
    
    // Створюємо елемент помилки
    const errorElement = document.createElement('p');
    errorElement.className = 'field-error';
    errorElement.textContent = message;
    errorElement.style.cssText = `
        color: #dc3545;
        font-size: 0.875rem;
        margin-top: 0.25rem;
        margin-bottom: 0;
    `;
    
    // Додаємо стиль до поля
    field.style.borderColor = '#dc3545';
    
    // Вставляємо помилку після поля
    field.parentElement.appendChild(errorElement);
}

/**
 * Видаляє помилку валідації з поля
 */
export function clearFieldError(field) {
    const errorElement = field.parentElement.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
    field.style.borderColor = '';
}

/**
 * Перевірка email на унікальність (async)
 */
export async function checkEmailUnique(email, currentEmail = null, checkUrl = null) {
    if (!email || email === currentEmail) {
        return { unique: true };
    }
    
    // Якщо URL не передано, використовуємо стандартний
    if (!checkUrl) {
        // Можна додати API endpoint для перевірки унікальності
        return { unique: true };
    }
    
    try {
        const response = await fetch(checkUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ email }),
        });
        
        const data = await response.json();
        return { unique: data.unique !== false };
    } catch (error) {
        console.error('Error checking email uniqueness:', error);
        return { unique: true }; // У разі помилки дозволяємо продовжити
    }
}

/**
 * Перевірка username на унікальність (async)
 */
export async function checkUsernameUnique(username, currentUsername = null, checkUrl = null) {
    if (!username || username === currentUsername) {
        return { unique: true };
    }
    
    if (!checkUrl) {
        return { unique: true };
    }
    
    try {
        const response = await fetch(checkUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ username }),
        });
        
        const data = await response.json();
        return { unique: data.unique !== false };
    } catch (error) {
        console.error('Error checking username uniqueness:', error);
        return { unique: true };
    }
}

/**
 * Отримує CSRF token з форми
 */
function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return csrfInput ? csrfInput.value : '';
}

/**
 * Валідація email формату
 */
export function validateEmail(email) {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailPattern.test(email);
}

/**
 * Валідація пароля
 */
export function validatePassword(password, minLength = 6) {
    if (!password) {
        return { valid: false, message: 'Password is required' };
    }
    if (password.length < minLength) {
        return { valid: false, message: `Password must be at least ${minLength} characters` };
    }
    return { valid: true };
}

/**
 * Перевірка співпадіння паролів
 */
export function validatePasswordMatch(password, passwordConfirm) {
    if (!passwordConfirm) {
        return { valid: false, message: 'Please confirm your password' };
    }
    if (password !== passwordConfirm) {
        return { valid: false, message: 'Passwords do not match' };
    }
    return { valid: true };
}

/**
 * Валідація username
 */
export function validateUsername(username, minLength = 3) {
    if (!username) {
        return { valid: false, message: 'Username is required' };
    }
    if (username.length < minLength) {
        return { valid: false, message: `Username must be at least ${minLength} characters` };
    }
    // Перевірка на дозволені символи
    const usernamePattern = /^[a-zA-Z0-9_]+$/;
    if (!usernamePattern.test(username)) {
        return { valid: false, message: 'Username can only contain letters, numbers, and underscores' };
    }
    return { valid: true };
}

/**
 * Debounce функція для затримки перевірок
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Форматує номер телефону в формат +380 (00) 000 00-00
 */
export function formatPhoneNumber(value) {
    // Видаляємо всі нецифрові символи
    const numbers = value.replace(/\D/g, '');
    
    // Якщо номер починається з 380, залишаємо як є
    // Якщо починається з 0, замінюємо на 380
    // Якщо починається з інших цифр, додаємо 380
    let formatted = numbers;
    
    if (numbers.length > 0) {
        if (numbers.startsWith('380')) {
            formatted = numbers;
        } else if (numbers.startsWith('0')) {
            formatted = '380' + numbers.substring(1);
        } else if (numbers.length <= 9) {
            formatted = '380' + numbers;
        }
        
        // Обмежуємо до 12 цифр (380 + 9 цифр)
        formatted = formatted.substring(0, 12);
        
        // Форматуємо: +380 (XX) XXX XX-XX
        if (formatted.length >= 3) {
            let result = '+' + formatted.substring(0, 3);
            if (formatted.length > 3) {
                result += ' (' + formatted.substring(3, 5);
                if (formatted.length > 5) {
                    result += ') ' + formatted.substring(5, 8);
                    if (formatted.length > 8) {
                        result += ' ' + formatted.substring(8, 10);
                        if (formatted.length > 10) {
                            result += '-' + formatted.substring(10, 12);
                        }
                    }
                } else {
                    result += ')';
                }
            }
            return result;
        }
    }
    
    return value;
}

/**
 * Валідація номера телефону
 */
export function validatePhone(phone) {
    if (!phone) {
        return { valid: false, message: 'Phone number is required' };
    }
    
    // Видаляємо всі нецифрові символи для перевірки
    const numbers = phone.replace(/\D/g, '');
    
    // Перевіряємо формат +380XXXXXXXXX (12 цифр)
    if (!numbers.startsWith('380') || numbers.length !== 12) {
        return { valid: false, message: 'Phone number must be in format +380 (XX) XXX XX-XX' };
    }
    
    return { valid: true };
}

