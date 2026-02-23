// script.js

// Card files to load from /cards folder
const cardFiles = ['card1.html', 'card2.html', 'card3.html'];

// Container where cards will be injected
const container = document.getElementById('card-container');

// Load and insert each card
cardFiles.forEach(file => {
  fetch(`cards/${file}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Failed to load ${file}`);
      }
      return response.text();
    })
    .then(html => {
      const div = document.createElement('div');
      div.classList.add('card');
      div.innerHTML = html;
      container.appendChild(div);
    })
    .catch(error => {
      console.error(error);
    });
});
