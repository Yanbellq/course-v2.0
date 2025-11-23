const catalog = document.getElementById("productsCatalog");
const viewButtons = document.querySelectorAll(".view-btn");

viewButtons.forEach(btn => {
    btn.addEventListener("click", () => {

        // видаляємо активний клас з кнопок
        viewButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        const view = btn.dataset.view;

        // перемикаємо класи view
        if (view === "grid") {
            catalog.classList.remove("list-view");
            catalog.classList.add("grid-view");
        } else {
            catalog.classList.remove("grid-view");
            catalog.classList.add("list-view");
        }

        // зберігаємо вибір у localStorage
        localStorage.setItem("catalogView", view);
    });
});

// Відновлення вибору після перезавантаження сторінки
const savedView = localStorage.getItem("catalogView") || "grid";
document.querySelector(`.view-btn[data-view=${savedView}]`)?.click();
//# sourceMappingURL=products_grid.js.map
