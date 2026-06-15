function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const liveOptions = document.querySelectorAll(".live-option");
const recordedOptions = document.querySelectorAll(".recorded-option");
const comboOptions = document.querySelectorAll(".combo-option");
const allOptions = document.querySelectorAll(".pricing-option");
const totalAmountEl = document.getElementById("totalAmount");

const pricingForm = document.querySelector(".pricing-form");
const webinarId = pricingForm.dataset.webinarId;
const recentlyEnded = pricingForm.dataset.recentlyEnded === "true";
const isAuthenticated = pricingForm.dataset.isAuthenticated === "true";
const loginUrl = pricingForm.dataset.loginUrl;

function uncheck(elements) {
    elements.forEach(el => el.checked = false);
}

function updateTotal() {
    let total = 0;
    allOptions.forEach(option => {
        if (option.classList.contains("option-disabled")) return;
        if (option.checked) {
            total += parseFloat(option.dataset.price);
        }
    });
    totalAmountEl.innerText = total.toFixed(2);
}

liveOptions.forEach(option => {
    option.addEventListener("change", () => {
        if (option.checked) {
            uncheck(liveOptions);
            option.checked = true;
            uncheck(comboOptions);
        }
        updateTotal();
    });
});

recordedOptions.forEach(option => {
    option.addEventListener("change", () => {
        if (option.checked) {
            uncheck(recordedOptions);
            option.checked = true;
            uncheck(comboOptions);
        }
        updateTotal();
    });
});

comboOptions.forEach(option => {
    option.addEventListener("change", () => {
        if (option.checked) {
            uncheck(comboOptions);
            option.checked = true;
            uncheck(liveOptions);
            uncheck(recordedOptions);
        }
        updateTotal();
    });
});

window.addEventListener("DOMContentLoaded", () => {
    uncheck(allOptions);

    if (recentlyEnded) {
        const recordedDefault = document.querySelector(".recorded-option");
        if (recordedDefault) recordedDefault.checked = true;
    } else {
        const defaultOption = document.getElementById("defaultLiveSingle");
        if (defaultOption) defaultOption.checked = true;
    }

    updateTotal();
});

document.querySelector(".btn-outline")?.addEventListener("click", async () => {
    const selectedOptions = document.querySelectorAll(".pricing-option:checked");
    if (!selectedOptions.length) { alert("Select plan"); return; }

    const csrftoken = getCookie('csrftoken');
    for (const option of selectedOptions) {
        const variant = option.dataset.variant;
        await fetch(`/cart/add/live/${webinarId}/${variant}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' },
        });
    }
    window.location.href = "/cart/";
});

document.querySelector(".buy-now")?.addEventListener("click", async () => {
    if (!isAuthenticated) {
        window.location.href = loginUrl;
        return;
    }

    const selectedOptions = document.querySelectorAll(".pricing-option:checked");
    if (!selectedOptions.length) { alert("Select plan"); return; }

    const csrftoken = getCookie('csrftoken');
    for (const option of selectedOptions) {
        const variant = option.dataset.variant;
        await fetch(`/cart/add/live/${webinarId}/${variant}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' },
        });
    }
    window.location.href = "/orders/checkout/";
});

function showWebinarEndedToast() {
    const toast = document.getElementById("webinarEndedToast");
    if (!toast) return;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3000);
}

document.querySelectorAll("input.option-disabled").forEach(option => {
    option.addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        option.checked = false;
        showWebinarEndedToast();
    });
});
