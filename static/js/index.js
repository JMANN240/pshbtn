$(document).ready(() => {
    $.ajax({
        type: 'GET',
        url: '/api/checks',
        success: (req) => {
            console.log(req.state);
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
        url: '/api/checks',
        data: {id: e.target.id},
        mimeType: 'json',
        success: (req) => {
            console.log(req);
        }
    });
    navigator.vibrate(100);
});