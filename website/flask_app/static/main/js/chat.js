$(document).ready(function(){
    // Connect to Socket.IO with the '/chat' namespace
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/chat');
    console.log("Connected to chat namespace");
    // When connected, signal that the user has joined the room
    socket.on('connect', function() {
        socket.emit('joined', {});
        console.log("Connected to chat namespace")
    });
    
    // Process status messages (e.g., when users join/leave)
    socket.on('status', function(data) {
        var p = $('<p></p>')
                    .addClass('chat-message guest')
                    .attr('style',data.style)
                    .text(data.msg);
        $('#chat').append(p);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    
    // Process normal chat messages
    socket.on('message', function(data) {
        var p = $('<p></p>')
                    .addClass('chat-message')
                    .attr('style',data.style)
                    .text(data.msg);
        $('#chat').append(p);
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    
    // When the send form is submitted, send the message to the server
    $('#sendForm').submit(function(e) {
        e.preventDefault();
        var msg = $('#messageInput').val().trim();
        if(msg !== ""){
            socket.emit('send_message', { msg: msg });
            $('#messageInput').val('');
        }
    });
    
    // When clicking the Leave Chat button, emit the left event and redirect
    $('#leaveChat').click(function(){
        socket.emit('left', {});
        window.location.href = '/home';
    });
});