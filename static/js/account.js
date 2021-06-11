$(document).ready(() => {
    $.ajax({
        type: 'GET',
        url: '/api/user',
        success: (req) => {
            $('#color-pref').attr("value", req.color);
        }
    });
});

$('#color-pref').on('change', (e) => {
    $.ajax({
        type: 'POST',
        url: '/api/user',
        data: {change: 'color', color: e.target.value},
        mimeType: 'json'
    });
});