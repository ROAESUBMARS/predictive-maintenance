import { waapi, utils } from 'animejs';

window.triggerFulfillmentAnimation = function() {
    const modal = document.getElementById('tech-completion-modal');
    if (!modal) return;

    modal.style.display = 'flex';
    setTimeout(() => {
        modal.style.opacity = '1';
    }, 10);

    const [ $value ] = utils.$('.value', modal);
    if ($value) {
        $value.textContent = 'initiating';
    }

    const animation = waapi.animate('.circle', {
      translate: '16rem',
      loop: 2,
      alternate: true,
    });

    animation.then(() => {
        if ($value) {
            $value.textContent = 'fulfilled';
        }
        setTimeout(() => {
            modal.style.opacity = '0';
            setTimeout(() => {
                modal.style.display = 'none';
            }, 400);
        }, 1500);
    });
}
