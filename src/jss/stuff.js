import * as THREE from 'three';

// Set up the renderer, scene, and camera
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 5;

// Create the orb geometry and material
const orbGeometry = new THREE.SphereGeometry(1, 32, 32);
const orbMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
const orb = new THREE.Mesh(orbGeometry, orbMaterial);
scene.add(orb);

// Create the black box
const boxGeometry = new THREE.BoxGeometry(2, 2, 2);
const boxMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
const blackBox = new THREE.Mesh(boxGeometry, boxMaterial);
blackBox.position.x = -5; // Start off-screen or hidden
scene.add(blackBox);

// Animation function to move and scale the orb, and move the black box into view
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

// Button functionality to move and scale the orb and show the black box
document.getElementById('animationButton').addEventListener('click', () => {
    new THREE.VectorKeyframeTrack('.position', [0, 1], [0, 1, 0, 5, 1, 0]);
    new THREE.NumberKeyframeTrack('.scale', [0, 1], [1, 1, 1, 0.5, 0.5, 0.5]);
    
    blackBox.position.x = -3; // Move black box into view
});

// Note: You need to create proper animations using Tween.js or another library to handle the smooth animations.

// Example using Tween.js to smoothly animate properties
new TWEEN.Tween(orb.position)
    .to({ x: 5 }, 1000)
    .start();

new TWEEN.Tween(orb.scale)
    .to({ x: 0.5, y: 0.5, z: 0.5 }, 1000)
    .start();

new TWEEN.Tween(blackBox.position)
    .to({ x: -3 }, 1000)
    .start();

function animate() {
    requestAnimationFrame(animate);
    TWEEN.update();
    renderer.render(scene, camera);
}
