// Bold & Modern Search Bar
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.search-input');
  const searchClear = document.querySelector('.search-clear');

  if (searchInput && searchClear) {
    searchInput.addEventListener('input', function() {
      if (this.value) {
        searchClear.classList.add('show');
      } else {
        searchClear.classList.remove('show');
      }
    });

    searchClear.addEventListener('click', function() {
      searchInput.value = '';
      searchClear.classList.remove('show');
      searchInput.focus();
    });
  }
});
