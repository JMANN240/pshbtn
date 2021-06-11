const color_input = document.querySelector('#color-input');

if (window.matchMedia('prefers-color-scheme: light').matches) {
    color_input.value = '#ffff00'
} else {
    color_input.value = '#00ffff'
}