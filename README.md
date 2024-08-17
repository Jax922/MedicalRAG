# MedicalRAG

## Download
```bash
cd /path/to/your/directory  # Change this to your desired directory
git clone https://github.com/Jax922/MedicalRAG.git
cd ./MedicalRAG
```

## ChatBot

Please install the NodeJS dependencies by running the following command:

```bash
cd ./chatbot # Change to the chatbot directory

npm install -g pnpm # Install pnpm globally if you haven't already
# for the detail of pnpm, please refer to https://pnpm.io/installation

pnpm install # Install the dependencies

# after installing the dependencies, you can run the chatbot by running the following command
pnpm dev
# when you see the message "Server is running on http://localhost:3000", you can open your browser and go to http://localhost:3000

```

### Test with the real-person chat
If you want to test the doctor real-person chat, you should run the WebSocket server first by running the following command:

```bash
    cd ./websocket # Change to the websocket directory
    node app.js # then you can see the message "Server is listening on port 8080", that means the WebSocket server is running
```

The doctor client will connect to the WebSocket server to receive the real-person chat.
The doctor client is running on the http://localhost:3000/doctor.

You can open the browser and go to http://localhost:8080 to monitor the WebSocket server. In that page, you can see the real-time chat between the doctor and the older adults.

### Settings of RAG
Go to the http://localhost:3000/setting to set the RAG settings.  After you update the settings, you should refresh the page to apply the new settings (http://localhost:3000/older).

