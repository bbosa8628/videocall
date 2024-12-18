from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import random
from typing import Dict, Set

# Initialize FastAPI app
app = FastAPI()

# Store connected users
waiting_users: Set[WebSocket] = set()
active_pairs: Dict[WebSocket, WebSocket] = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global waiting_users, active_pairs
    user = websocket

    print("New user connected")
    await user.accept()

    try:
        # Add the user to the waiting pool
        waiting_users.add(user)
        await find_pair(user)

        while True:
            data = await user.receive_text()

            if user in active_pairs:
                # Send the message to the paired user
                paired_user = active_pairs[user]
                if data == '{"type": "stop", "message": "Stop the call for this user"}':
                    await stop_call(user, paired_user)
                else:
                    await send_message(paired_user, data)

    except WebSocketDisconnect:
        print("User disconnected")
        # Clean up after disconnection
        if user in waiting_users:
            waiting_users.remove(user)
        if user in active_pairs:
            paired_user = active_pairs.pop(user)
            active_pairs.pop(paired_user, None)
            # Notify the paired user that the connection has ended
            if paired_user:
                await send_message(paired_user, '{"type": "end"}')
    finally:
        print("Cleanup complete")


async def find_pair(user: WebSocket):
    global waiting_users, active_pairs

    # Check for other waiting users
    if len(waiting_users) > 1:
        waiting_users.remove(user)
        partner = random.choice(list(waiting_users))
        waiting_users.remove(partner)

        # Pair users
        active_pairs[user] = partner
        active_pairs[partner] = user

        # Notify both users
        await user.send_text('{"type": "pair", "message": "Connected to a stranger"}')
        await partner.send_text('{"type": "pair", "message": "Connected to a stranger"}')
    else:
        await user.send_text('{"type": "wait", "message": "Waiting for a stranger..."}')


async def stop_call(user: WebSocket, paired_user: WebSocket):
    global active_pairs
    # Close the current connection for the user who clicked stop call
    if user in active_pairs:
        active_pairs.pop(user)

    # Send end call message to the paired user
    await send_message(paired_user, '{"type": "end", "message": "Call ended by the other user."}')

    # Optionally close the WebSocket connection for the user who clicked stop call
    await user.close()
    print("Call stopped for one user.")


async def send_message(user: WebSocket, message: str):
    try:
        await user.send_text(message)
    except WebSocketDisconnect:
        pass
