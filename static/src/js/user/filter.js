'use strict'
// Автосабміт фільтрів при зміні
const filterForm = document.getElementById('filter-form');
const categoryInputs = document.querySelectorAll('input[name="category"]');
const brandInputs = document.querySelectorAll('input[name="brand"]');
const productTypeInputs = document.querySelectorAll('input[name="product_type"]');
const sortSelect = document.getElementById('sortSelect');

// Двійний range-слайдер для ціни
const minRange = document.getElementById('min-range');
const maxRange = document.getElementById('max-range');
const minPriceVal = document.getElementById('price-min-val');
const maxPriceVal = document.getElementById('price-max-val');
const minGap = 5; // мінімальна різниця між значеннями

var thumbLeft = document.querySelector(".filter__range-slider-thumb.left");
var thumbRight = document.querySelector(".filter__range-slider-thumb.right");
var range = document.querySelector(".filter__range-slider-range");

const resetFiltersBtn = document.getElementById('reset-filters');
const resetPriceRangeBtn = document.getElementById('reset-price-range');

// Скидання фільтрів при кліку на кнопку
resetFiltersBtn.addEventListener('click', function () {
    if (location.search !== '') location.search = '';
});

// Автоматичний submit при зміні категорії
categoryInputs.forEach(input => {
    input.addEventListener('change', function () {
        filterForm.submit();
    });
});

// Автоматичний submit при зміні бренду
brandInputs.forEach(input => {
    input.addEventListener('change', function () {
        filterForm.submit();
    });
});

// Автоматичний submit при зміні типу продукту
productTypeInputs.forEach(input => {
    input.addEventListener('change', function () {
        filterForm.submit();
    });
});

// Автоматичний submit при зміні сортування
if (sortSelect) {
    sortSelect.addEventListener('change', function () {
        filterForm.submit();
    });
}

function setLeftValue() {
    var _this = minRange,
        min = parseInt(_this.min),
        max = parseInt(_this.max);

    _this.value = Math.min(parseInt(_this.value), parseInt(maxRange.value) - 1);

    var percent = ((_this.value - min) / (max - min)) * 100;

    thumbLeft.style.left = percent + "%";
    range.style.left = percent + "%";
}
setLeftValue();

function setRightValue() {
    var _this = maxRange,
        min = parseInt(_this.min),
        max = parseInt(_this.max);

    _this.value = Math.max(parseInt(_this.value), parseInt(minRange.value) + 1);

    var percent = ((_this.value - min) / (max - min)) * 100;

    thumbRight.style.right = (100 - percent) + "%";
    range.style.right = (100 - percent) + "%";
}
setRightValue();

minRange.addEventListener("input", setLeftValue);
maxRange.addEventListener("input", setRightValue);

minRange.addEventListener("mouseover", function () {
    thumbLeft.classList.add("hover");
});
minRange.addEventListener("mouseout", function () {
    thumbLeft.classList.remove("hover");
});
minRange.addEventListener("mousedown", function () {
    thumbLeft.classList.add("active");
});
minRange.addEventListener("mouseup", function () {
    thumbLeft.classList.remove("active");
});

maxRange.addEventListener("mouseover", function () {
    thumbRight.classList.add("hover");
});
maxRange.addEventListener("mouseout", function () {
    thumbRight.classList.remove("hover");
});
maxRange.addEventListener("mousedown", function () {
    thumbRight.classList.add("active");
});
maxRange.addEventListener("mouseup", function () {
    thumbRight.classList.remove("active");
});

if (minRange && maxRange) {
    const updateSlider = (event) => {
        let minVal = parseFloat(minRange.value);
        let maxVal = parseFloat(maxRange.value);

        if (maxVal - minVal <= minGap) {
            if (event.target === minRange) {
                minRange.value = maxVal - minGap;
            } else {
                maxRange.value = minVal + minGap;
            }
        }

        minPriceVal.textContent = minRange.value;
        maxPriceVal.textContent = maxRange.value;
    };

    minRange.addEventListener('input', updateSlider);
    maxRange.addEventListener('input', updateSlider);

    // Автосабміт при відпусканні повзунка
    [minRange, maxRange].forEach(slider => {
        slider.addEventListener('change', () => filterForm.submit());
    });
}

// Скидання цінового діапазону при кліку на кнопку
resetPriceRangeBtn.addEventListener('click', function () {
    minRange.value = 0;
    maxRange.value = 2000;
    minPriceVal.textContent = minRange.value;
    maxPriceVal.textContent = maxRange.value;
    setLeftValue();
    setRightValue();
    filterForm.submit();
});