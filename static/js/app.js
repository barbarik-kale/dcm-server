async function loginAndGetTokens() {
    try {
        const email = localStorage.getItem('email');
        const password = localStorage.getItem('password');
        const drone_id = localStorage.getItem('drone_id');
        // Login Request
        const loginResponse = await fetch('/user/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password })
        });

        const loginData = await loginResponse.json();
        const loginToken = loginData.data.token;

        // Fetch Media Token
        const tokenResponse = await fetch('/ws/token/', {
            method: 'POST',
            headers: { Authorization: `${loginToken}` , 'Content-Type': 'application/json'},
            body: JSON.stringify({drone_id: drone_id})
        });

        const tokenData = await tokenResponse.json();
        return tokenData.data.token;
    } catch (error) {
        console.error('Error fetching tokens:', error);
    }
}

function startWebSocketStream(mediaToken) {
    const videoElement = document.getElementById('videoStream');
    const webSocket = new WebSocket(`/ws/media/consumer/?token=${mediaToken}`);

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

