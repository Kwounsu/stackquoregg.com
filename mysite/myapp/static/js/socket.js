$(document).ready(function() {
    $('.send_message').click(function() {
        var msg_val = $('.message_input').val();
        $.ajax({
            type: "POST",
            url: '/',
            data: {
                "msg": msg_val
            },
            success: function(data) {
                $('.message_input').val("");
            }
        });
    });
});
 
Pusher.logToConsole = true;
var pusher = new Pusher('0cf8e17723482e413656', {
    cluster: 'ap1',
    encrypted: true
});
 
var channel = pusher.subscribe('channel1');
channel.bind('chatting', function(data) {
    if (data.username == "{{ user.username}}") {
        var your_msg = '<li class="message right appeared"><div class="avatar" style="background-image: url(http://placehold.it/60/55C1E7/fff&text=' + data.username + ')";></div><div class="text_wrapper"><div class="text">' + data.message + '</div></div></li>'
        $('.messages').append(your_msg);
    } else {
        var your_msg = '<li class="message left appeared"><div class="avatar" style="background-image: url(http://placehold.it/60/55C1E7/fff&text=' + data.username + ')";></div><div class="text_wrapper"><div class="text">' + data.message + '</div></div></li>'
        $('.messages').append(your_msg);
    }
});