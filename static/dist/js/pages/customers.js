import Button from"../components/button.js";let customerTable=document.querySelector("#customer-list-table"),pageHeaderActions=(customerTable&&(console.log("Initializing customer list page..."),loadCustomers()),document.querySelector("#page-header-actions"));async function loadCustomers(){var e=document.querySelector("#customer-list-body");if(e){e.innerHTML=`
        <tr>
            <td colspan="5" class="text-center">
                <div class="loading-spinner" style="display: inline-block; vertical-align: middle;">
                    <div class="spinner" style="width: 24px; height: 24px; border-width: 3px;"></div>
                </div>
                <span style="vertical-align: middle; margin-left: 10px;">Завантаження клієнтів...</span>
            </td>
        </tr>
    `;try{renderCustomers((await PCManagement.apiRequest("/customers/")).customers,e)}catch(t){console.error("Failed to load customers:",t),e.innerHTML=`
            <tr>
                <td colspan="5" class="text-center text-error">
                    Не вдалося завантажити список клієнтів. Спробуйте оновити сторінку.
                </td>
            </tr>
        `}}}function renderCustomers(t,e){t&&0!==t.length?(t=t.map(t=>{var e=PCManagement.formatDate(t.created_at);return`
            <tr data-customer-id="${t.id}">
                <td><a href="/customers/${t.id}/" class="font-semibold underline">${t.name} ${t.surname}</a></td>
                <td>${t.email}</td>
                <td>${t.phone}</td>
                <td>${e}</td>
                <td>
                    <a href="/customers/${t.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a>
                    <button class="btn btn--sm btn--error" data-action="delete" data-url="/customers/${t.id}/" data-confirm="Ви впевнені, що хочете видалити клієнта ${t.name} ${t.surname}?">Видалити</button>
                </td>
            </tr>
        `}).join(""),e.innerHTML=t):e.innerHTML=`
            <tr>
                <td colspan="5" class="text-center">Клієнтів не знайдено. <a href="/customers/add/">Додайте першого</a>.</td>
            </tr>
        `}pageHeaderActions&&pageHeaderActions.insertAdjacentHTML("beforeend",Button("Додати клієнта","add","shadow-glow","plus",""));