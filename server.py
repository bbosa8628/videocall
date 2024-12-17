import asyncio
import websockets
import os

# Your WebSocket handler code remains the same

# Get the PORT environment variable for deployment
PORT = int(os.environ.get("PORT", 6789))

async def asgi_app(scope, receive, send):
    """
    ASGI app entry point for Uvicorn. Used for hosting the WebSocket server.
    """
    if scope["type"] == "lifespan":
        # Handle app startup/shutdown
        await send({"type": "lifespan.startup.complete"})
        await receive()
        await send({"type": "lifespan.shutdown.complete"})
    elif scope["type"] == "http":
        # Reject HTTP requests
        await send({"type": "http.response.start", "status": 404, "headers": []})
        await send({"type": "http.response.body", "body": b"Not Found"})
    elif scope["type"] == "websocket":
        # Handle WebSocket connections
        websocket = websockets.WebSocketServerProtocol()
        await websocket.handshake(scope, receive, send)
        await handler(websocket, None)

# Start the WebSocket server
start_server = websockets.serve(handler, "0.0.0.0", PORT)

print(f"Signaling server started on ws://0.0.0.0:{PORT}")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
