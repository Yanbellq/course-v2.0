// static/src/ts/components/btn.ts

// Функція створення кнопки
// text - текст кнопки
// link - посилання на кнопку
// styles - стилі кнопки
// icon - іконка кнопки
// icon_styles - стилі іконки кнопки

type Props = {
    text: string;
    link: string;
    styles: string;
    icon: string;
    icon_styles: string;
}

export default function Button(props: Props) {
    return `
        <a href="${props.link}/" class="btn btn--primary shadow-glow ${props.styles}">
            <i data-lucide="${props.icon}" class="w-4 h-4 ${props.icon_styles}"></i>
            <span>${props.text}</span>
        </a>
    `;
}
