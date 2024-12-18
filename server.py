from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS setup to allow connections from all origins for testing
origins = [
    "172.66.47.138",  # Replace with your production URL or IP
    "172.66.44.118",
    "https://bbosa8628.pages.dev/video.html",
    "http://bbosa8628.pages.dev/video.html",
    "https://bbosa8628.pages.dev/video",
    "http://bbosa8628.pages.dev/video"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket route to handle WebSocket connections
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Send the received message back to the client
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)  # Listen on port 9000
