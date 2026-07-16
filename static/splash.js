import { waapi, utils, stagger } from 'animejs';

// Trigger stagger animation on the squares
waapi.animate('.square', {
  y: {
    to: [0, -30, 0],
    ease: 'out(4)',
    duration: 1000,
  },
  rotate: { from: -180, to: 0, ease: 'out(3)' },
  scale: { to: [.65, 1, .65], ease: 'inOut(3)' },
  duration: 500,
  delay: stagger(75),
  loop: true,
});

// Handle splash layout transition on page load
function initSplash() {
    const logo = document.querySelector('.splash-logo');
    const sub = document.querySelector('.splash-sub');
    
    if (logo) {
        logo.style.opacity = '1';
        logo.style.transform = 'translateY(0)';
    }
    if (sub) {
        sub.style.opacity = '1';
        sub.style.transform = 'translateY(0)';
    }

    // Automatically fade out and hide splash after 4.5 seconds (leaving 5.3s total with transition)
    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if (splash) {
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
            }, 800); // Wait for the transition to finish
        }
    }, 4500);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSplash);
} else {
    initSplash();
}
