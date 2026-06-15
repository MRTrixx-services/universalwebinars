// Search Results Filter Functionality
document.addEventListener('DOMContentLoaded', function() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const sections = document.querySelectorAll('.results-section');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const filter = this.getAttribute('data-filter');

      // Update active button
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      // Filter sections
      sections.forEach(section => {
        const type = section.getAttribute('data-type');

        if (filter === 'all') {
          section.style.display = 'block';
        } else if (filter === type) {
          section.style.display = 'block';
        } else {
          section.style.display = 'none';
        }
      });
    });
  });
});
