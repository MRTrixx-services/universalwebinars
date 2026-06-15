// SELECT ALL CHECKBOX
document.getElementById("selectAll").onclick = function () {
const checkboxes = document.querySelectorAll(".row-checkbox")
checkboxes.forEach(cb => cb.checked = this.checked)
updateSelectedCount()
}

// UPDATE SELECTED COUNT
function updateSelectedCount() {
const checked = document.querySelectorAll(".row-checkbox:checked").length
document.getElementById("selectedCount").textContent = checked + " selected"
}

document.querySelectorAll(".row-checkbox").forEach(cb => {
cb.addEventListener("change", updateSelectedCount)
})

// AUTO UPDATE STATUS
function updateWebinarStatus() {
fetch("/admin-panel/api/webinar-status/")
.then(res => res.json())
.then(data => {
data.webinars.forEach(function (w) {
let el = document.getElementById("status-" + w.id)
if (!el) return

if (w.status === "LIVE") {
el.innerHTML = '<span class="status-badge live"><i class="fas fa-circle"></i> LIVE</span>'
} else if (w.status === "UPCOMING") {
el.innerHTML = '<span class="status-badge upcoming"><i class="fas fa-clock"></i> Scheduled</span>'
} else {
el.innerHTML = '<span class="status-badge ended"><i class="fas fa-check"></i> Completed</span>'
}
})
})
}

setInterval(updateWebinarStatus, 10000)
