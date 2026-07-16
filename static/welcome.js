import { waapi, stagger, splitText } from 'animejs';

window.triggerEngWelcomeAnimation = function() {
    const modal = document.getElementById('eng-welcome-modal');
    if (!modal) return;

    modal.style.display = 'flex';
    setTimeout(() => {
        modal.style.opacity = '1';
    }, 10);

    const { chars } = splitText('#eng-welcome-modal h2', { words: false, chars: true });

    chars.forEach(char => {
        char.style.display = 'inline-block';
        char.style.animation = 'none';
    });

    waapi.animate(chars, {
      translate: `0 -2rem`,
      delay: stagger(100),
      duration: 600,
      loop: true,
      alternate: true,
      ease: 'inOut(2)',
    });

    setTimeout(() => {
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.display = 'none';
        }, 400);
    }, 4000);
}
