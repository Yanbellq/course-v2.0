import Button from"../components/button.js";document.addEventListener("DOMContentLoaded",function(){document.querySelector("#supplier-list-table")&&(console.log("Initializing supplier list page..."),loadSuppliers().then(e=>console.log(e)))});let pageHeaderActions=document.querySelector("#page-header-actions");async function loadSuppliers(){var t=document.querySelector("#supplier-list-body");if(t){t.innerHTML=`
        <tr>
            <td colspan="5" class="text-center">
                <div class="loading-spinner" style="display: inline-block; vertical-align: middle;">
                    <div class="spinner" style="width: 24px; height: 24px; border-width: 3px;"></div>
                </div>
                <span style="vertical-align: middle; margin-left: 10px;">Завантаження постачальників...</span>
            </td>
        </tr>
    `;try{renderSuppliers((await PCManagement.apiRequest("/suppliers/")).suppliers,t)}catch(e){console.error("Failed to load suppliers:",e),t.innerHTML=`
            <tr>
                <td colspan="5" class="text-center text-error">
                    Не вдалося завантажити список постачальників.
                </td>
            </tr>
        `}}}function renderSuppliers(e,t){e&&0!==e.length?t.innerHTML=e.map(e=>`
        <tr data-supplier-id="${e.id}">
            <td><a href="/suppliers/${e.id}/" class="font-semibold underline">${e.name}</a></td>
            <td>${e.contact_person||"—"}</td>
            <td>${e.email}</td>
            <td>${e.phone}</td>
            <td>
                <a href="/suppliers/${e.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a>
                <button class="btn btn--sm btn--error" data-action="delete" data-url="/suppliers/${e.id}/" data-confirm="Ви впевнені, що хочете видалити постачальника ${e.name}?">Видалити</button>
            </td>
        </tr>
    `).join(""):t.innerHTML=`
            <tr>
                <td colspan="5" class="text-center">Постачальників не знайдено. <a href="/suppliers/add/" class="text-primary underline">Додайте першого</a>.</td>
            </tr>
        `}pageHeaderActions&&pageHeaderActions.insertAdjacentHTML("beforeend",Button("Додати постачальника","add","shadow-glow","plus",""));