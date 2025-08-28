import Button from"../components/button.js";document.addEventListener("DOMContentLoaded",function(){document.querySelector("#product-list-table")&&(console.log("Initializing product list page..."),loadProducts())});let pageHeaderActions=document.querySelector("#page-header-actions");async function loadProducts(){var e=document.querySelector("#product-list-body");document.querySelector("#product-list-table");if(e){e.innerHTML=`
        <tr>
            <td colspan="6" class="text-center">
                <div class="loading-spinner" style="display: inline-block; vertical-align: middle;">
                    <div class="spinner" style="width: 24px; height: 24px; border-width: 3px;"></div>
                </div>
                <span style="vertical-align: middle; margin-left: 10px;">Завантаження товарів...</span>
            </td>
        </tr>
    `;try{renderProducts((await PCManagement.apiRequest("/products/")).products,e),PCManagement.initDataTable("#product-list-table",{pageSize:15})}catch(t){console.error("Failed to load products:",t),e.innerHTML=`
            <tr>
                <td colspan="6" class="text-center text-error">
                    Не вдалося завантажити список товарів.
                </td>
            </tr>
        `}}}function renderProducts(t,e){t&&0!==t.length?(t=t.map(t=>{var e=PCManagement.formatCurrency(t.price),n=t.quantity_in_stock<=t.min_stock_level?"text-error font-bold":"";return`
            <tr data-product-id="${t.id}">
                <td><a href="/products/${t.id}/" class="font-semibold underline">${t.name}</a></td>
                <td>${t.category}</td>
                <td>${t.manufacturer||"—"}</td>
                <td>${e}</td>
                <td class="${n}">${t.quantity_in_stock}</td>
                <td>
                    <a href="/products/${t.id}/edit/" class="btn btn--sm btn--secondary">Редагувати</a>
                    <button class="btn btn--sm btn--error" data-action="delete" data-url="/products/${t.id}/" data-confirm="Ви впевнені, що хочете видалити товар ${t.name}?">Видалити</button>
                </td>
            </tr>
        `}).join(""),e.innerHTML=t):e.innerHTML=`
            <tr>
                <td colspan="6" class="text-center">Товарів не знайдено. <a href="/products/add/" class="text-primary underline">Додайте перший</a>.</td>
            </tr>
        `}pageHeaderActions&&pageHeaderActions.insertAdjacentHTML("beforeend",Button("Додати товар","add","shadow-glow","plus",""));