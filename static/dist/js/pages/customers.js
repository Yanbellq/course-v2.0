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
                <td class="dropdown-data">
                    <button type="button" class="dropdown-toggle">...</button>
                    <ul class="dropdown-menu">
                        <li>
                            <a href="/customers/${t.id}/edit/" class="btn btn--sm btn--secondary">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="square-pen" class="lucide lucide-square-pen h-4 w-4">
                                    <path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                    <path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path>
                                </svg>
                                Редагувати
                            </a>
                        </li>
                        <li>
                            <button class="btn btn--sm btn--error w-full" data-action="delete" data-url="/customers/${t.id}/" data-confirm="Ви впевнені, що хочете видалити клієнта ${t.name} ${t.surname}?">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trash-2" class="lucide lucide-trash-2 h-4 w-4">
                                    <path d="M10 11v6"></path><path d="M14 11v6"></path>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"></path>
                                    <path d="M3 6h18"></path><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                                Видалити
                            </button>
                        </li>
                    </ul>
                </td>
            </tr>
        `}).join(""),e.innerHTML=t,document.querySelectorAll(".dropdown-data").forEach(t=>{var e=t.querySelector(".dropdown-toggle");let a=t.querySelector(".dropdown-menu");e.addEventListener("click",t=>{document.querySelectorAll(".dropdown-menu.active").forEach(t=>{t!==a&&t.classList.remove("active")}),a.classList.toggle("active")})}),document.addEventListener("click",t=>{t.target.closest(".dropdown-data")||document.querySelectorAll(".dropdown-menu.active").forEach(t=>{t.classList.remove("active")})})):e.innerHTML=`
            <tr>
                <td colspan="5" class="text-center">Клієнтів не знайдено. <a href="/customers/add/">Додайте першого</a>.</td>
            </tr>
        `}pageHeaderActions&&pageHeaderActions.insertAdjacentHTML("beforeend",Button("Додати клієнта","add","shadow-glow","plus",""));