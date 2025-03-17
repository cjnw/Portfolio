
// listen for button click
document.addEventListener('DOMContentLoaded', () => {
    const feedbackToggleBtn = document.getElementById('feedbackToggleBtn');
    const feedbackOverlay = document.getElementById('feedbackFormOverlay');
  
    
    feedbackToggleBtn.addEventListener('click', () => {
      if (feedbackOverlay.style.display === 'block') {
        feedbackOverlay.style.display = 'none';
      } else {
        feedbackOverlay.style.display = 'block';
      }
    });
  
    //close the overlay if user clicks outside the form
    feedbackOverlay.addEventListener('click', (e) => {
      // If the click is on the overlay, not on the form itself
      if (e.target === feedbackOverlay) {
        feedbackOverlay.style.display = 'none';
      }
    });
  });
  