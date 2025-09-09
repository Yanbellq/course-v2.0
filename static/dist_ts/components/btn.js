// static/src/ts/components/btn.ts
export default function Button(props) {
    return `
        <a href="${props.link}/" class="btn btn--primary shadow-glow ${props.styles}">
            <i data-lucide="${props.icon}" class="w-4 h-4 ${props.icon_styles}"></i>
            <span>${props.text}</span>
        </a>
    `;
}
