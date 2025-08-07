document.getElementById("darkSwitch")?.addEventListener("change", function () {
    document.body.classList.toggle("dark-mode");
});
document.querySelectorAll('.animated-button').forEach(button => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        this.appendChild(ripple);

        ripple.style.left = `${e.offsetX}px`;
        ripple.style.top = `${e.offsetY}px`;

        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});
