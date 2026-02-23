const modal = document.getElementById("videoModal");
const btn = document.getElementById("openVideoBtn");
const closeBtn = document.querySelector(".close");

// Optional: Stop video playback on close
const youtubeIframe = document.getElementById("youtubePlayer");
// const videoPlayer = document.getElementById("videoPlayer");

btn.onclick = () => {
  modal.style.display = "block";
};

closeBtn.onclick = () => {
  modal.style.display = "none";
  stopVideo();
};

window.onclick = (event) => {
  if (event.target == modal) {
    modal.style.display = "none";
    stopVideo();
  }
};

function stopVideo() {
  if (youtubeIframe) {
    youtubeIframe.contentWindow.postMessage('{"event":"command","func":"stopVideo","args":""}', '*');
  }

  // For local video:
  // if (videoPlayer) {
  //   videoPlayer.pause();
  //   videoPlayer.currentTime = 0;
  // }
}
