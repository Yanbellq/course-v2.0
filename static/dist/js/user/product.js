// Tab functionality
function openTab(evt, tabName) {
    const tabContents = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove('active');
    }
    
    const tabBtns = document.getElementsByClassName('tab-btn');
    for (let i = 0; i < tabBtns.length; i++) {
        tabBtns[i].classList.remove('active');
    }
    
    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active');
}

function changeQty(step) {
    const qtyInput = document.getElementById('quantity');
    const display = document.getElementById('quantity-display');
    const min = parseInt(qtyInput.getAttribute('min')) || 1;
    const max = parseInt(qtyInput.getAttribute('max')) || 99;
    let current = parseInt(qtyInput.value) || 1;

    current += step;

    if (current < min) current = min;
    if (current > max) current = max;

    qtyInput.value = current;
    display.textContent = current;
}
//# sourceMappingURL=product.js.map
