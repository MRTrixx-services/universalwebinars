function removePhoto() {
document.getElementById('photoInput').value = '';
document.getElementById('photoPreview').style.display = 'none';
document.getElementById('photoArea').style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function() {
const photoInput = document.getElementById('photoInput');
const photoArea = document.getElementById('photoArea');
const photoPreview = document.getElementById('photoPreview');
const photoImage = document.getElementById('photoImage');

photoInput.addEventListener('change', function(e) {
handlePhotoChange(e);
});

photoArea.addEventListener('dragover', function(e) {
e.preventDefault();
photoArea.classList.add('drag-over');
});

photoArea.addEventListener('dragleave', function() {
photoArea.classList.remove('drag-over');
});

photoArea.addEventListener('drop', function(e) {
e.preventDefault();
photoArea.classList.remove('drag-over');

const files = e.dataTransfer.files;
if (files.length > 0) {
photoInput.files = files;
handlePhotoChange({target: {files: files}});
}
});
});

function handlePhotoChange(e) {
const file = e.target.files[0];
if (file) {
const reader = new FileReader();
reader.onload = function(event) {
document.getElementById('photoImage').src = event.target.result;
document.getElementById('photoPreview').style.display = 'flex';
document.getElementById('photoArea').style.display = 'none';
};
reader.readAsDataURL(file);
}
}

$(document).ready(function(){

$('#id_country').select2({
placeholder:"Select country",
width:'100%',
containerCss: 'margin-bottom:0'
})

$('#id_country').on('select2:open',function(){
setTimeout(function(){
const searchField = document.querySelector('.select2-search__field');
if(searchField) searchField.setAttribute('placeholder','Search country...')
},0)
})

const input = document.querySelector("#id_phone_number")

const iti = window.intlTelInput(input,{
initialCountry:"us",
separateDialCode:true,
preferredCountries:["us","in","gb"],
utilsScript:"https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js"
})

const instructorCountry = document.getElementById('instructorForm').dataset.country

$('#id_country').val(instructorCountry).trigger('change')

if(instructorCountry){
iti.setCountry(instructorCountry.toLowerCase())
}

input.addEventListener("countrychange",function(){
const countryData = iti.getSelectedCountryData()
$('#id_country')
.val(countryData.iso2.toUpperCase())
.trigger('change.select2')
})

$('#id_country').on('change',function(){
const selectedCountry = $(this).val()
if(selectedCountry){
iti.setCountry(selectedCountry.toLowerCase())
}
})

document.querySelector("#instructorForm")
.addEventListener("submit",function(){
input.value = iti.getNumber()

if (CKEDITOR.instances.id_bio) {
CKEDITOR.instances.id_bio.updateElement()
}
})

})
