// Функція створення кнопки
export default function Button(text, link, styles, icon, icon_styles) {
    return `
        <a href="${link}/" class="btn btn--primary shadow-glow ${styles}">
            <i data-lucide="${icon}" class="w-4 h-4 ${icon_styles}"></i>
            <span>${text}</span>
        </a>
    `;
}
//# sourceMappingURL=button.js.map
