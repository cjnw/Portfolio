
document.addEventListener("DOMContentLoaded", function() {
    // White and black key elements
    const whiteKeys = document.querySelectorAll(".white-key");
    const blackKeys = document.querySelectorAll(".black-key");
  
    // The identifiers for all the notes
    const whiteNames = ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"];
    const blackNames = ["W", "E", "T", "Y", "U", "O", "P"];
  
    // Label each white key
    whiteKeys.forEach((key, i) => {
      const label = document.createElement("span");
      label.classList.add("key-label");
      label.textContent = whiteNames[i] || "";
      key.appendChild(label);
    });
  
    // Label each black key
    blackKeys.forEach((key, i) => {
      const label = document.createElement("span");
      label.classList.add("key-label");
      label.textContent = blackNames[i] || "";
      key.appendChild(label);
    });
  });

  document.addEventListener("DOMContentLoaded", function() {
    // Listen for key presses
    document.addEventListener("keydown", (event) => {
        const hitKey = event.code;
          
        // This key in piano.html
        const hitPart = document.querySelector(`[data-key="${hitKey}"]`);

        if (hitPart) {
            hitPart.classList.add("hit");
        }
    });

    document.addEventListener("keyup", (event) => {
        // Listen for released keys
        const clearedKey = event.code;

        // This key in piano.html
        const clearedPart = document.querySelector(`[data-key="${clearedKey}"]`);

        if (clearedPart) {
            clearedPart.classList.remove("hit");
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Sound mapping
    const sound = {
        65: "http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav", 
        87: "http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav", 
        83: "http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav", 
        69: "http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav", 
        68: "http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav", 
        70: "http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav", 
        84: "http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav", 
        71: "http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav", 
        89: "http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav", 
        72: "http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav", 
        85: "http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav", 
        74: "http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav", 
        75: "http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav", 
        79: "http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav", 
        76: "http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav", 
        80: "http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav", 
        186: "http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav" 
    };

    /* The sequence of input keys from user */
    let KeystrokeInput = "";

    /* The string that summons the Great Old One if typed */
    const thePhrase = "weseeyou";

    // Function to play sound
    function playSound(keyCode) {
        if (sound[keyCode]) {
            const audio = new Audio(sound[keyCode]);
            audio.play();
        }
    }

    // Highlight the hit key
    function highlightKey(keyCode) {
        const keyObject = document.querySelector(`[data-key="${keyCode}"]`);
        if (keyObject) {
            keyObject.classList.add("hit");
            setTimeout(() => keyObject.classList.remove("hit"), 200);
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
            // Play audio
            const audio = new Audio("/static/main/images/Creepy-piano-sound-effect.mp3");
            audio.play();
        }, 2000);

        // Remove event listener to disable key input
        document.removeEventListener("keydown", handleKeyPress);
    }

    // Handle the keystrokes
    function handleKeyPress(event) {
        const key = event.key.toLowerCase();
        KeystrokeInput += key;

        // Check if the input sequence matches "weseeyou"
        if (KeystrokeInput.includes(thePhrase)) {
            awakenGreatOldOne();
            return;
        }

        // Limit the stored sequence to the length of "weseeyou" to avoid unnecessary memory usage
        if (KeystrokeInput.length > thePhrase.length) {
            KeystrokeInput = KeystrokeInput.slice(-thePhrase.length);
        }

        // Play sound & highlight keys
        playSound(event.keyCode);
        highlightKey(event.keyCode);
    }

    // Listen for any keystrokes
    document.addEventListener("keydown", handleKeyPress);
});
  