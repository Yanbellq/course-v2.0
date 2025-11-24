// static/src/js/crm/crm.js

import showNotification from "../user/toast.js";

document.addEventListener("DOMContentLoaded", () => {
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
                    showNotification("Успішно видалено");

                    // Видаляємо HTML-рядок
                    const row = form.closest("tr");
                    if (row) row.remove();
                } else {
                    showNotification("Помилка видалення", "error");
                }
            } catch (err) {
                console.error("Delete error:", err);
                showNotification(`Помилка запиту ${err}`, "error");
            }
        });
    });
});
//# sourceMappingURL=crm.js.map
