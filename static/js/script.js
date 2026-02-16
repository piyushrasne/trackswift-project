// Script
// Handle Dark Mode Toggle
document.getElementById("darkSwitch")?.addEventListener("change", function () {
    document.body.classList.toggle("dark-mode");
});

// Add Ripple Effect to Buttons
document.querySelectorAll('.animated-button').forEach(button => {
    button.addEventListener('click', function (e) {
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        this.appendChild(ripple);

        // Position ripple
        ripple.style.left = `${e.offsetX}px`;
        ripple.style.top = `${e.offsetY}px`;

        // Remove ripple after animation
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});
