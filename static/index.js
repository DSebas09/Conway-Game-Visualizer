const canvas = document.getElementById("game-canvas");
const ctx = canvas.getContext("2d");
const cellSize = 10;

const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = event => {
    const grid = JSON.parse(event.data);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let y = 0; y < grid.length; y++) {
        for (let x = 0; x < grid[0].length; x++) {
            if (grid[y][x] === 1) {
                ctx.fillStyle = "purple";
                ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
    }
};

ws.onclose = () => {
    console.log("WebSocket connection closed");
};