$(document).ready(() => {
    $.ajax({
        type: 'GET',
        url: '/api/user',
        success: (req) => {
            console.log(req);
            document.documentElement.style.setProperty('--light', req.color);
            document.documentElement.style.setProperty('--light-darker', tinycolor(req.color).darken(2).toString());
            for (let [row, rowvals] of req.state.entries()) {
                for (let [col, value] of rowvals.entries()) {
                    $('#hundred').append(`
                        <input type="checkbox" id="btn-${row}-${col}" style="display: none;"${value ? ' checked' : ''}>
                        <label for="btn-${row}-${col}" id="lbl-${row}-${col}" class="btn"></label>
                    `);
                }
            }
        }
    });
});

$(document).on('click', '.btn', (e) => {
    $.ajax({
        type: 'POST',
        url: '/api/user',
        data: {change: 'state', id: e.target.id},
        mimeType: 'json',
        success: (req) => {
            console.log(req);
        }
    });
    navigator.vibrate(100);
});