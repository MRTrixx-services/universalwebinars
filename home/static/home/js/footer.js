document.getElementById('newsletterForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const email = document.getElementById('newsletterEmail').value;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = document.getElementById('newsletterForm').dataset.url;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: 'email=' + encodeURIComponent(email)
    })
    .then(response => response.json())
    .then(data => {
        showToast(data.message, data.success ? 'success' : 'error');
        if (data.success) {
            document.getElementById('newsletterEmail').value = '';
        }
    })
    .catch(error => {
        showToast('An error occurred. Please try again.', 'error');
    });
});

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle-fill' : 'exclamation-circle-fill'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
