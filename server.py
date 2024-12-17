import asyncio
import websockets
import random

# Store connected users
waiting_users = set()
active_pairs = {}

async def handler(websocket, path):
    global waiting_users, active_pairs
    user = websocket

    print("New user connected")
    try:
        # Add the user to the waiting pool
        waiting_users.add(user)
        await find_pair(user)

        async for message in user:
            data = message

            if user in active_pairs:
                # Send the message to the paired user
                paired_user = active_pairs[user]
                # Check if the message is a stop call message
                if data == '{"type": "stop", "message": "Stop the call for this user"}':
                    await stop_call(user, paired_user)
                else:
                    await send_message(paired_user, data)

    except websockets.ConnectionClosed:
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

async def find_pair(user):
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
        await user.send('{"type": "pair", "message": "Connected to a stranger"}')
        await partner.send('{"type": "pair", "message": "Connected to a stranger"}')
    else:
        await user.send('{"type": "wait", "message": "Waiting for a stranger..."}')

async def stop_call(user, paired_user):
    global active_pairs
    # Close the current connection for the user who clicked stop call
    if user in active_pairs:
        active_pairs.pop(user)
    
    # Send end call message to the paired user
    await send_message(paired_user, '{"type": "end", "message": "Call ended by the other user."}')
    
    # Optionally close the WebSocket connection for the user who clicked stop call
    await user.close()
    print("Call stopped for one user.")

async def send_message(user, message):
    try:
        await user.send(message)
    except websockets.ConnectionClosed:
        pass

async def main():
    # Create and start the websocket server
    start_server = websockets.serve(handler, "0.0.0.0", 6789)

    print("Signaling server started on ws://0.0.0.0:6789")
    await start_server

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
