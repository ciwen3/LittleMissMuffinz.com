document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("projectsContainer");

  const cardFiles = [
    "./cards/RobFlemingPark.html",
    "./cards/CourtneyPhotography.html",
    "./cards/Intro.html"
  ];

  // Load cards in order
  for (const file of cardFiles) {
    try {
      const response = await fetch(file);
      const html = await response.text();

      const wrapper = document.createElement("div");
      wrapper.innerHTML = html.trim();
      container.appendChild(wrapper.firstElementChild);
    } catch (err) {
      console.error(`Error loading ${file}`, err);
    }
  }

  initializeModals();
});

/* ============================
   MODAL & VIDEO HANDLING
============================ */

function initializeModals() {
  const buttons = document.querySelectorAll(".openVideoBtn");

  buttons.forEach(button => {
    const modalId = button.dataset.target;
    const modal = document.getElementById(modalId);
    if (!modal) return;

    const closeBtn = modal.querySelector(".close");
    const iframe = modal.querySelector("iframe");
    const video = modal.querySelector("video");

    button.addEventListener("click", () => {
      modal.style.display = "block";
    });

    closeBtn.addEventListener("click", () => {
      closeModal(modal, iframe, video);
    });

    window.addEventListener("click", event => {
      if (event.target === modal) {
        closeModal(modal, iframe, video);
      }
    });
  });
}

function closeModal(modal, iframe, video) {
  modal.style.display = "none";

  // Stop YouTube
  if (iframe) {
    iframe.contentWindow.postMessage(
      '{"event":"command","func":"stopVideo","args":""}',
      "*"
    );
  }

  // Stop HTML5 video
  if (video) {
    video.pause();
    video.currentTime = 0;
  }
}

