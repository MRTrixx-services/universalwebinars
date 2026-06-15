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

const allOptions = document.querySelectorAll('.pricing-option');
const totalAmountEl = document.getElementById('totalAmount');

const pricingCard = document.querySelector('.pricing-card');
const webinarId = pricingCard.dataset.webinarId;
const isAuthenticated = pricingCard.dataset.isAuthenticated === 'true';
const loginUrl = pricingCard.dataset.loginUrl;

function updateTotal() {
    let total = 0;
    allOptions.forEach(option => {
        if (option.checked) {
            total += parseFloat(option.dataset.price) || 0;
        }
    });
    totalAmountEl.innerText = total.toFixed(2);
}

allOptions.forEach(option => {
    option.addEventListener('change', updateTotal);
});

window.addEventListener('DOMContentLoaded', () => {
    const first = document.querySelector('.pricing-option');
    if (first) { first.checked = true; }
    updateTotal();
});

document.getElementById('cartBtn').addEventListener('click', async () => {
    const checked = document.querySelector('.pricing-option:checked');
    if (!checked) { alert('Please select a plan'); return; }
    const csrftoken = getCookie('csrftoken');
    await fetch(`/cart/add/recorded/${webinarId}/${checked.dataset.variant}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    });
    window.location.href = '/cart/';
});

document.getElementById('buyBtn').addEventListener('click', async () => {
    if (!isAuthenticated) { window.location.href = loginUrl; return; }
    const checked = document.querySelector('.pricing-option:checked');
    if (!checked) { alert('Please select a plan'); return; }
    const csrftoken = getCookie('csrftoken');
    await fetch(`/cart/add/recorded/${webinarId}/${checked.dataset.variant}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    });
    window.location.href = '/orders/checkout/';
});
