document.addEventListener("DOMContentLoaded", () => {
  const openButtons = document.querySelectorAll(".openVideoBtn");

  openButtons.forEach(button => {
    const targetModalId = button.getAttribute("data-target");
    const modal = document.getElementById(targetModalId);
    const closeBtn = modal.querySelector(".close");
    const youtubeIframe = modal.querySelector("iframe");

    button.addEventListener("click", () => {
      modal.style.display = "block";
    });

    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
      stopVideo(youtubeIframe);
    });

    window.addEventListener("click", (event) => {
      if (event.target === modal) {
        modal.style.display = "none";
        stopVideo(youtubeIframe);
      }
    });
  });
});

function stopVideo(iframe) {
  if (iframe) {
    iframe.contentWindow.postMessage('{"event":"command","func":"stopVideo","args":""}', '*');
  }
}

function stopVideo(videoElement) {
  if (videoElement) {
    videoElement.pause();
    videoElement.currentTime = 0;
  }
}
