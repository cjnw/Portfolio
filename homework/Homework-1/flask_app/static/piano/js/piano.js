
document.addEventListener("DOMContentLoaded", function() {
    // White and black key elements
    const whiteKeys = document.querySelectorAll(".white-key");
    const blackKeys = document.querySelectorAll(".black-key");
  
    // Arrays for the note names
    const whiteKeyNotes = ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"];
    const blackKeyNotes = ["W", "E", "T", "Y", "U", "O", "P"];
  
    // Create labels for each white key
    whiteKeys.forEach((key, i) => {
      const label = document.createElement("span");
      label.classList.add("key-label");
      label.textContent = whiteKeyNotes[i] || "";
      key.appendChild(label);
    });
  
    // Create labels for each black key
    blackKeys.forEach((key, i) => {
      const label = document.createElement("span");
      label.classList.add("key-label");
      label.textContent = blackKeyNotes[i] || "";
      key.appendChild(label);
    });
  });

  document.addEventListener("DOMContentLoaded", function() {
    // Listen for key presses
    document.addEventListener("keydown", (event) => {
        const hitKey = event.code;  
        // This key's element in HTML
        const hitPart = document.querySelector(`[data-key="${hitKey}"]`);

        if (hitPart) {
            hitPart.classList.add("pressed");
        }
    });

    document.addEventListener("keyup", (event) => {
        // Listen for key release
        const liftedKey = event.code;
        const liftedPart = document.querySelector(`[data-key="${key}"]`);

        if (keyElement) {
            keyElement.classList.remove("pressed");
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Sound mapping
    const sound = {
        65: "http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav", // A
        87: "http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav", // W
        83: "http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav", // S
        69: "http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav", // E
        68: "http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav", // D
        70: "http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav", // F
        84: "http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav", // T
        71: "http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav", // G
        89: "http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav", // Y
        72: "http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav", // H
        85: "http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav", // U
        74: "http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav", // J
        75: "http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav", // K
        79: "http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav", // O
        76: "http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav", // L
        80: "http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav", // P
        186: "http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav" // ;
    };

    let inputSequence = "";
    const summonSequence = "weseeyou";

    // Function to play sound
    function playSound(keyCode) {
        if (sound[keyCode]) {
            const audio = new Audio(sound[keyCode]);
            audio.play();
        }
    }

    function highlightKey(keyCode) {
        const keyElement = document.querySelector(`[data-key="${keyCode}"]`);
        if (keyElement) {
            keyElement.classList.add("pressed");
            setTimeout(() => keyElement.classList.remove("pressed"), 200);
        }
    }

    // Awakens the Great Old One
    function awakenGreatOldOne() {
        const piano = document.querySelector(".piano-container");
        const greatOldOne = document.createElement("img");
        greatOldOne.src = "/static/main/images/greatone.jpeg";  // Use the uploaded file
        greatOldOne.classList.add("great-old-one");

        // Replace the piano with the image
        piano.style.transition = "opacity 2s";
        piano.style.opacity = "0";

        setTimeout(() => {
            piano.replaceWith(greatOldOne);
            // Play the creepy audio
            const audio = new Audio("/static/main/images/Creepy-piano-sound-effect.mp3");
            audio.play();
        }, 2000);

        // Remove event listener to disable key input
        document.removeEventListener("keydown", handleKeyPress);
    }

    function handleKeyPress(event) {
        const key = event.key.toLowerCase();
        inputSequence += key;

        // Check if the input sequence matches "weseeyou"
        if (inputSequence.includes(summonSequence)) {
            awakenGreatOldOne();
            return;
        }

        // Limit the stored sequence to the length of "weseeyou" to avoid unnecessary memory usage
        if (inputSequence.length > summonSequence.length) {
            inputSequence = inputSequence.slice(-summonSequence.length);
        }

        // Play sound & highlight keys
        playSound(event.keyCode);
        highlightKey(event.keyCode);
    }

    // Keydown event listener
    document.addEventListener("keydown", handleKeyPress);
});
  