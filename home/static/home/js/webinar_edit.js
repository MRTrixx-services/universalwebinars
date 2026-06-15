let step = 1

function goStep(n) {
document.querySelectorAll(".form-step").forEach(s => s.style.display = "none")
document.getElementById("step" + n).style.display = "block"

document.querySelectorAll(".step-item").forEach((item, index) => {
item.classList.remove("active", "completed")
if (index + 1 < n) item.classList.add("completed")
if (index + 1 === n) item.classList.add("active")
})

step = n

if (n === 3) fillReview()

window.scrollTo({ top: 0, behavior: 'smooth' })
}

function nextStep() { step++; goStep(step) }
function prevStep() { step--; goStep(step) }

function fillReview() {
document.getElementById("reviewTitle").innerText = document.querySelector("input[name='title']").value || "-"
document.getElementById("reviewDuration").innerText = document.querySelector("input[name='duration']").value || "-"

const instructorSelect = document.getElementById("instructorSelect")
document.getElementById("reviewInstructor").innerText = instructorSelect.options[instructorSelect.selectedIndex].text

const categorySelect = document.querySelector("select[name='category']")
document.getElementById("reviewCategory").innerText = categorySelect.options[categorySelect.selectedIndex].text

const dateField = document.querySelector("input[name='start_datetime']")
document.getElementById("reviewDate").innerText = dateField.value || "-"
}

function searchZoomMeetings() {
const title = document.querySelector("input[name='title']").value
fetch("/integrations/zoom/search-meetings/?q=" + title)
.then(res => res.json())
.then(data => {
const container = document.getElementById("zoomResults")
container.innerHTML = ""
data.results.forEach(meeting => {
container.innerHTML += `
<div class="zoom-item">
<div>
<strong>${meeting.topic}</strong>
<small>${meeting.start_time}</small>
</div>
<button type="button" onclick='useMeeting(${JSON.stringify(meeting)})'>Select</button>
</div>`
})
})
}

function useMeeting(meeting) {
document.getElementById("selectedZoomMeeting").value = JSON.stringify(meeting)
document.getElementById("zoomResults").innerHTML = "<b>Selected:</b> " + meeting.topic
}

document.addEventListener("DOMContentLoaded", function () {

const instructor = document.getElementById("instructorSelect")
const instructorCard = document.getElementById("instructorCard")
const instructorPhoto = document.getElementById("instructorPhoto")
const instructorNameDisplay = document.getElementById("instructorNameDisplay")

function updatePreview() {
const selected = instructor.options[instructor.selectedIndex]
const photo = selected.dataset.photo
const name = selected.text
if (photo && instructor.value) {
instructorPhoto.src = photo
instructorNameDisplay.textContent = name
instructorCard.style.display = "flex"
} else {
instructorCard.style.display = "none"
}
}

instructor.addEventListener("change", updatePreview)

const startTime = document.getElementById("startTime")
const preview = document.getElementById("timezonePreview")

startTime.onchange = function () {
if (!this.value) return
const date = new Date(this.value + ":00")
const pdt = date.toLocaleTimeString("en-US", { timeZone: "America/Los_Angeles", hour: "numeric", minute: "2-digit" })
const edt = date.toLocaleTimeString("en-US", { timeZone: "America/New_York", hour: "numeric", minute: "2-digit" })
preview.innerHTML = `<div style="display:flex;gap:10px;font-size:14px"><strong>PST:</strong> ${pdt} <strong>EST:</strong> ${edt}</div>`
}

document.querySelectorAll(".ckeditor").forEach(function (textarea) {
if (typeof CKEDITOR !== "undefined") {
CKEDITOR.replace(textarea)
}
})

})
