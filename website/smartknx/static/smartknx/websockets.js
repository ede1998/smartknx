// Create global web socket
// onmessage:
// call update on each element with group address x

let chatSocket = new WebSocket(
    'ws://' + window.location.host +
    '/ws/update')

chatSocket.onmessage = function (e) {
    const msg = JSON.parse(e.data);
    const addr = msg['address'];
    const data = msg['data'];
    location.reload(true);
//    document.querySelector('#chat-log').value += (message + '\n');
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};