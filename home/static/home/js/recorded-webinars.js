document.addEventListener("DOMContentLoaded", function () {

    const filterPanel = document.getElementById("filterPanel");
    const filterBtn = document.getElementById("filterToggleBtn");

    if (filterBtn && filterPanel) {
        filterBtn.addEventListener("click", function () {
            filterPanel.classList.toggle("active");
        });
    }

});
