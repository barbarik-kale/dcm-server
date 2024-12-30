async function loginAndGetTokens() {
    try {
        // Login Request
        const loginResponse = await fetch('http://localhost:8000/user/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: 'hrushi@mail.com', password: 'hrushi' })
        });

        const loginData = await loginResponse.json();
        const loginToken = loginData.data.token;

        // Fetch Media Token
        const tokenResponse = await fetch('http://localhost:8000/ws/token/', {
            method: 'POST',
            headers: { Authorization: `${loginToken}` , 'Content-Type': 'application/json'},
            body: JSON.stringify({drone_id: "1ce9ecb9-65b1-4e29-ae00-f48f4255bed4"})
        });

        const tokenData = await tokenResponse.json();
        return tokenData.data.token;
    } catch (error) {
        console.error('Error fetching tokens:', error);
    }
}

function startWebSocketStream(mediaToken) {
    const videoElement = document.getElementById('videoStream');
    const webSocket = new WebSocket(`ws://localhost:8000/ws/media/consumer/?token=${mediaToken}`);

    webSocket.binaryType = 'arraybuffer'; // Ensure binary data is handled correctly

    webSocket.onmessage = (event) => {
        const frameData = new Uint8Array(event.data); // Binary frame data
        const blob = new Blob([frameData], { type: 'image/jpeg' }); // Adjust MIME type as per server
        const objectURL = URL.createObjectURL(blob);
        videoElement.src = objectURL; // Update video stream
    };

    webSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    webSocket.onclose = () => {
        console.log('WebSocket closed.');
    };
}

async function main() {
    const mediaToken = await loginAndGetTokens();
    if (mediaToken) {
        await startWebSocketStream(mediaToken);
    }
}

