let step = 1

function goStep(n) {
document.querySelectorAll(".form-step").forEach(s => s.style.display = "none")
document.getElementById("step" + n).style.display = "block"

document.querySelectorAll(".step-item").forEach((item, index) => {
item.classList.remove("active", "completed")
if (index + 1 < n) item.classList.add("completed")
if (index + 1 === n) item.classList.add("active")
})

document.getElementById("currentStep").textContent = n + "/4"
step = n

if (n === 4) fillReview()

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

const type = document.getElementById("webinarType").value
document.getElementById("reviewType").innerText = type.toUpperCase()

const dateField = document.querySelector("input[name='start_datetime']")
const recordingField = document.querySelector("input[name='recording_link']")

if (type === "live") {
document.getElementById("reviewDate").innerText = dateField.value || "-"
document.getElementById("reviewDateRow").style.display = "block"
document.getElementById("reviewRecordingRow").style.display = "none"
document.getElementById("liveZoomSection").style.display = "block"
} else {
document.getElementById("reviewRecording").innerText = recordingField ? recordingField.value || "-" : "-"
document.getElementById("reviewDateRow").style.display = "none"
document.getElementById("reviewRecordingRow").style.display = "block"
document.getElementById("liveZoomSection").style.display = "none"
}
}

function searchZoomMeetings() {
const title = document.querySelector("input[name='title']").value
fetch(`/integrations/zoom/search-meetings/?q=${encodeURIComponent(title)}`)
.then(res => res.json())
.then(data => {
const container = document.getElementById("zoomResults")
container.innerHTML = ""
data.results.forEach(meeting => {
container.innerHTML += `
<div class="zoom-item">
<div class="zoom-details">
<strong>${meeting.topic}</strong>
<small>${meeting.start_time} • ${meeting.duration} min</small>
</div>
<button type="button" class="btn-select" onclick='useMeeting(${JSON.stringify(meeting)})'>Select</button>
</div>`
})
})
}

function searchZoomRecordings() {
const title = document.querySelector("input[name='title']").value.trim()
if (!title) { alert("Please enter webinar title first"); return }

fetch("/integrations/zoom/search-recordings/?q=" + encodeURIComponent(title))
.then(res => res.json())
.then(data => {
const container = document.getElementById("zoomRecordingResults")
let html = ""
data.results.forEach(rec => {
html += `
<div class="zoom-item">
<div class="zoom-details">
<strong>${rec.topic}</strong>
<small>${rec.start_time}</small>
</div>
<button type="button" onclick='selectRecording(${JSON.stringify(rec)})'>Select</button>
</div>`
})
container.innerHTML = html
})
}

function selectRecording(rec) {
document.getElementById("selectedZoomRecording").value = JSON.stringify(rec)
document.getElementById("zoomRecordingResults").innerHTML = "<div class='zoom-selected'>Selected: " + rec.topic + "</div>"
}

function useMeeting(meeting) {
document.getElementById("selectedZoomMeeting").value = JSON.stringify(meeting)
document.getElementById("zoomResults").innerHTML = "<div class='zoom-selected'><i class='fas fa-check-circle'></i> Selected: " + meeting.topic + "</div>"
}

document.addEventListener("DOMContentLoaded", function () {

// Webinar type toggle
const typeSelect = document.getElementById("webinarType")
const liveFields = document.getElementById("liveFields")
const recordedFields = document.getElementById("recordedFields")
const livePricing = document.getElementById("livePricingFields")
const recordedPricing = document.getElementById("recordedPricingFields")
const liveGlobalPricing = document.getElementById("liveGlobalPricing")
const recordedGlobalPricing = document.getElementById("recordedGlobalPricing")

function toggleWebinarType() {
if (typeSelect.value === "live") {
liveFields.style.display = "block"
recordedFields.style.display = "none"
livePricing.style.display = "grid"
recordedPricing.style.display = "none"
liveGlobalPricing.style.display = "block"
recordedGlobalPricing.style.display = "none"
} else {
liveFields.style.display = "none"
recordedFields.style.display = "block"
livePricing.style.display = "none"
recordedPricing.style.display = "grid"
liveGlobalPricing.style.display = "none"
recordedGlobalPricing.style.display = "block"
}
}

typeSelect.addEventListener("change", toggleWebinarType)
toggleWebinarType()

// Instructor preview
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
updatePreview()

// Timezone preview
const startTime = document.getElementById("startTime")
const preview = document.getElementById("timezonePreview")

startTime.onchange = function () {
if (!this.value) return
const date = new Date(this.value + ":00")
const pdt = date.toLocaleTimeString("en-US", { timeZone: "America/Los_Angeles", hour: "numeric", minute: "2-digit" })
const edt = date.toLocaleTimeString("en-US", { timeZone: "America/New_York", hour: "numeric", minute: "2-digit" })
preview.innerHTML = `<div style="display:flex;gap:10px;font-size:14px"><strong>PST:</strong> ${pdt} <strong>EST:</strong> ${edt}</div>`
}

// CKEditor init
document.querySelectorAll(".ckeditor").forEach(function (textarea) {
if (typeof CKEDITOR !== "undefined") {
CKEDITOR.replace(textarea)
}
})

})
