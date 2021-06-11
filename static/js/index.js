$(document).ready(() => {
    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            $('#hundred').append(`
                <input type="checkbox" id="btn-${row}-${col}" style="display: none;">
                <label for="btn-${row}-${col}" id="lbl-${row}-${col}" class="btn"></label>
            `);
        }
    }
    $.ajax({
        type: 'GET',
        url: '/api/user',
        success: (req) => {
            if (req != "401") {
                document.documentElement.style.setProperty('--light', req.color);
                for (let [row, rowvals] of req.state.entries()) {
                    for (let [col, value] of rowvals.entries()) {
                        $(`#btn-${row}-${col}`).attr('checked', value);
                    }
                }
            }
            document.documentElement.style.setProperty('--light-darker', tinycolor(getComputedStyle(document.documentElement).getPropertyValue('--light')).darken(3).toString());
        }
    });
});

$(document).on('click', '.btn', (e) => {
    $.ajax({
        type: 'POST',
        url: '/api/user',
        data: {change: 'state', id: e.target.id},
        mimeType: 'json'
    });
    navigator.vibrate(100);
});