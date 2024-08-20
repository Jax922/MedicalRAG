const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const { join } = require('node:path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "http://10.37.81.23:3000", 
        methods: ["GET", "POST"]
    }
});

app.use(cors({
    origin: "http://10.37.81.23:3000" 
}));

app.get('/', (req, res) => {
    res.sendFile(join(__dirname, 'index.html'));
});

io.on('connection', (socket) => {
    console.log('A user connected:', socket.id);

    socket.on('message', (message) => {
        console.log('Received message:', message);
        io.emit('message', message);
    });

    socket.on('disconnect', () => {
        console.log('A user disconnected:', socket.id);
    });
});

server.listen(8080, () => {
    console.log('Server is listening on port 8080');
});