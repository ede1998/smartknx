// Create global web socket
// onmessage:
// call update on each element with group address x

let chatSocket = new WebSocket(
    'ws://' + window.location.hostname + ":8765")

chatSocket.onmessage = function (e) {
    const msg = JSON.parse(e.data);
    const addr = msg['group_address'];
    const data = msg['data'];
    const tag = "#address" + addr.replace(/\//g, "-")
    let elem = document.querySelector(tag);
    if (elem != null)
    {
        elem.update(data);
    }
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};
