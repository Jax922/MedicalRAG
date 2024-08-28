// import { useEffect, useRef } from 'react';
// import { io, Socket } from 'socket.io-client';

// const WS_URL = 'ws://localhost:8080';

// const useSocket = (onMessageCallback: (data: any) => void) => {
//     const socketRef = useRef<Socket | null>(null);

//     // useEffect(() => {
//         const socketInstance = io(WS_URL);
//         socketRef.current = socketInstance;

//         socketInstance.on('connect', () => {
//             console.log('Connected to the server');
//         });

//         socketInstance.on('message', (data) => {
//             if (onMessageCallback) {
//                 onMessageCallback(data);
//             }
//         });

//         socketInstance.on('disconnect', () => {
//             console.log('Disconnected from the server');
//         });

//         return () => {
//             socketInstance.disconnect();
//         };
//     // }, [onMessageCallback]);

//     return socketRef.current;
// };

// export default useSocket;


import { io, Socket } from 'socket.io-client';

const WS_URL = 'ws://10.37.81.23:8080';
const socket: Socket = io(WS_URL);

socket.on('connect', () => {
    console.log('Connected to the server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from the server');
});

const useSocket = (onMessageCallback: (data: any) => void) => {
    socket.on('message', (data) => {
        if (onMessageCallback) {
            onMessageCallback(data);
        }
    });

    return socket;
};


export default useSocket;