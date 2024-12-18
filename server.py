from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse

# Create FastAPI instance
app = FastAPI()

# HTTP health check endpoint
@app.get("/")
async def health_check():
    return PlainTextResponse("Service is running")

# WebSocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    try:
        while True:
            # Receive data from the WebSocket
            data = await websocket.receive_text()
            print(f"Received: {data}")

            # Echo the data back to the client
            await websocket.send_text(f"Message: {data}")
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        await websocket.close()
