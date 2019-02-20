// Create global web socket
// onmessage:
// call update on each element with group address x

"use strict";

let group_states = {}

let knxSocket = new WebSocket(
    'ws://' + window.location.hostname + ":8765")

knxSocket.onmessage = function (e) {
    const msg = JSON.parse(e.data);
    const addr = msg['group_address'];
    const data = msg['data'];
    const tag = "address" + addr.replace(/\//g, "-")
    let elem = document.querySelector("#"+tag);
    if (elem != null)
    {
        elem.update(data);
    }
    group_states[tag] = data;
};

knxSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};
