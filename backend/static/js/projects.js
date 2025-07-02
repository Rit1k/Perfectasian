// Show 5 projects at a time, reveal more on button click

document.addEventListener('DOMContentLoaded', function() {
    const projects = Array.from(document.querySelectorAll('.project-box'));
    const moreBtn = document.getElementById('more-projects-btn');
    const batchSize = 5;
    let currentIndex = 0;

    function updateProjects() {
        projects.forEach((box, idx) => {
            box.style.display = idx < currentIndex ? '' : 'none';
        });
        if (currentIndex < projects.length) {
            moreBtn.style.display = 'inline-block';
        } else {
            moreBtn.style.display = 'none';
        }
    }

    function showNextBatch() {
        currentIndex += batchSize;
        updateProjects();
    }

    // Initial state
    currentIndex = batchSize;
    updateProjects();

    moreBtn.addEventListener('click', showNextBatch);

    // Show button if there are more than batchSize projects
    if (projects.length > batchSize) {
        moreBtn.style.display = 'inline-block';
    }
}); 