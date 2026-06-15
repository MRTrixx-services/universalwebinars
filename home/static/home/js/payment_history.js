// Initialize date pickers
const fromDatePicker = flatpickr("#fromDate", {
    format: "d-m-Y",
    dateFormat: "d-m-Y",
    static: true
});

const toDatePicker = flatpickr("#toDate", {
    format: "d-m-Y",
    dateFormat: "d-m-Y",
    static: true
});

// Calendar button handlers
document.getElementById('fromDateBtn').addEventListener('click', function(e) {
    e.preventDefault();
    fromDatePicker.open();
});

document.getElementById('toDateBtn').addEventListener('click', function(e) {
    e.preventDefault();
    toDatePicker.open();
});

// Make input fields clickable to open calendar
document.getElementById('fromDate').addEventListener('click', function() {
    fromDatePicker.open();
});

document.getElementById('toDate').addEventListener('click', function() {
    toDatePicker.open();
});

// Clear filters functionality
document.querySelector('.btn-clear-filters').addEventListener('click', function() {
    document.getElementById('filterForm').reset();
    window.location.href = window.location.pathname;
});

// Export CSV functionality
document.querySelector('.btn-export-csv').addEventListener('click', function(e) {
    e.preventDefault();
    const formData = new FormData(document.getElementById('filterForm'));
    const params = new URLSearchParams(formData);
    const exportUrl = document.getElementById('filterForm').dataset.csvUrl;
    window.location.href = exportUrl + "?" + params.toString();
});

// Export Excel functionality
document.querySelector('.btn-export-excel').addEventListener('click', function(e) {
    e.preventDefault();
    const formData = new FormData(document.getElementById('filterForm'));
    const params = new URLSearchParams(formData);
    const exportUrl = document.getElementById('filterForm').dataset.excelUrl;
    window.location.href = exportUrl + "?" + params.toString();
});
