// backend/static/js/websocket-client.js

const socket = new WebSocket('ws://localhost:8000/ws/chat/'); // Adjust to your URL

socket.onopen = function(event) {
    console.log('WebSocket is connected.');
    // Sending a message once the connection is open
    socket.send(JSON.stringify({ 'message': 'Hello Server!' }));
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received from server:', data.message);
};

socket.onclose = function(event) {
    console.log('WebSocket is closed now.');
};

socket.onerror = function(error) {
    console.log('WebSocket Error: ', error);
};
