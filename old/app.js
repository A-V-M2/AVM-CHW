const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const WIDTH = canvas.width = window.innerWidth;
const HEIGHT = canvas.height = window.innerHeight;

function simulateSoundWave() {
    let searchInput = document.getElementById('searchInput').value;
    if (!searchInput) return; // No input, no animation

    // Reset canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    ctx.beginPath();
    ctx.moveTo(0, HEIGHT / 2);
    // Draw a simple sine wave
    for (let i = 0; i < WIDTH; i++) {
        ctx.lineTo(i, HEIGHT / 2 + 20 * Math.sin(i * 0.02));
    }
    ctx.strokeStyle = '#FFF';
    ctx.stroke();
}

// Optionally resize canvas on window resize
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});
