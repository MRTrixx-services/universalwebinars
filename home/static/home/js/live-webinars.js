document.addEventListener("DOMContentLoaded", function () {

    const filterPanel = document.getElementById("filterPanel");
    const filterBtn = document.getElementById("filterToggleBtn");
    const filterForm = document.getElementById("filterForm");

    // Toggle filter panel
    if (filterBtn && filterPanel) {
        filterBtn.addEventListener("click", function () {
            filterPanel.classList.toggle("active");
        });
    }

    // Auto-submit on any filter change
    if (filterForm) {
        const allInputs = filterForm.querySelectorAll("input[type='radio'], input[type='checkbox']");

        allInputs.forEach(function (input) {
            input.addEventListener("change", function () {

                // If "All" checkbox clicked for instructor — uncheck others
                if (input.value === "all" && input.name === "instructor") {
                    filterForm.querySelectorAll("input[name='instructor']").forEach(function (cb) {
                        if (cb.value !== "all") cb.checked = false;
                    });
                } else if (input.name === "instructor" && input.value !== "all" && input.checked) {
                    // Uncheck "All" if specific instructor selected
                    const allCb = filterForm.querySelector("input[name='instructor'][value='all']");
                    if (allCb) allCb.checked = false;
                }

                // If "All" checkbox clicked for category — uncheck others
                if (input.value === "all" && input.name === "category") {
                    filterForm.querySelectorAll("input[name='category']").forEach(function (cb) {
                        if (cb.value !== "all") cb.checked = false;
                    });
                } else if (input.name === "category" && input.value !== "all" && input.checked) {
                    const allCb = filterForm.querySelector("input[name='category'][value='all']");
                    if (allCb) allCb.checked = false;
                }

                // Remove "all" value inputs before submit (backend doesn't need them)
                filterForm.querySelectorAll("input[value='all']").forEach(function (cb) {
                    cb.disabled = true;
                });

                filterForm.submit();
            });
        });
    }

});

document.addEventListener("DOMContentLoaded", function () {

    const countdownElements = document.querySelectorAll(".countdown");

    countdownElements.forEach(function (el) {

        const startTime = new Date(el.dataset.start);

        function updateCountdown() {

            const now = new Date();
            const diff = startTime - now;

            if (diff <= 0) {
                el.innerHTML = "<span style='color:white;font-weight:800;'>LIVE NOW</span>";
                // Add live-now class to parent time-left div
                const timeLeftDiv = el.closest('.time-left');
                if (timeLeftDiv) {
                    timeLeftDiv.classList.add('live-now');
                }
                return;
            }

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

            if (days > 1) {
                el.innerHTML = `Starts in ${days} days`;
            } else if (days === 1) {
                el.innerHTML = `Starts in 1 day`;
            } else if (hours > 0) {
                el.innerHTML = `Starts in ${hours}h ${minutes}m`;
            } else {
                el.innerHTML = `Starts in ${minutes}m`;
            }
        }

        updateCountdown();
        setInterval(updateCountdown, 60000);
    });

});
