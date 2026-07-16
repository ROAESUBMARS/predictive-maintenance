import { animate } from 'animejs';

let filterAnim = null;
let polyAnim = null;

window.triggerDiagnosticAnimation = function() {
    const modal = document.getElementById('diagnostic-loading-modal');
    if (!modal) return;

    modal.style.display = 'flex';
    setTimeout(() => {
        modal.style.opacity = '1';
    }, 10);

    if (filterAnim) filterAnim.pause();
    if (polyAnim) polyAnim.pause();

    filterAnim = animate(['#liquid-filter feTurbulence', '#liquid-filter feDisplacementMap'], {
      baseFrequency: .05,
      scale: 15,
      alternate: true,
      loop: true
    });

    polyAnim = animate('#diagnostic-loading-modal polygon', {
      points: '64 68.64 8.574 100 63.446 67.68 64 4 64.554 67.68 119.426 100',
      alternate: true,
      loop: true
    });
}

window.stopDiagnosticAnimation = function() {
    const modal = document.getElementById('diagnostic-loading-modal');
    if (!modal) return;

    modal.style.opacity = '0';
    setTimeout(() => {
        modal.style.display = 'none';
        if (filterAnim) {
            filterAnim.pause();
            filterAnim = null;
        }
        if (polyAnim) {
            polyAnim.pause();
            polyAnim = null;
        }
    }, 400);
}
