# Multiplayer Pong Game

## About

This is a client-server multiplayer game. A maximum of 4 players and a minimum of 2 players shall play this game on their own Python instance or physical machine. It requires a server to track game events and maintain connections with the player clients.

## Requirements
- Server machine running Python
- At least 2 client machines (max 4) running Python with Pygame-ce installed.
- A Keyboard for the movement of the paddle.
- Network connection (LAN or Internet)
- Port-forwarding may be required when you want to connect over the internet.

## How to install and run the Client and the Server:

Assuming Python and GIT are installed, clone this repository into a folder of your choosing:
```
git clone git@github.com:stsang36/cmpt-371-project.git 
```

OR Download as ZIP and extract.

After cloning or extracting, open a new terminal window and enter the main folder and install the required libraries:
```
Windows:

pip install -r requirements.txt

OR

Linux:
pip3 install -r requirements.txt <Linux>
```


### Server:
1. Enter the server directory
   ```cd server```
2. Open the config.json file with your text editor and assign an IP and PORT. The default is set to listen to 0.0.0.0 with PORT 8000.
3. Run the server ```python .\main.py``` or ```python3 .\main.py```.

The server will now start listening to new connections on the assigned IP and Port.

### Client (2-4 players):
1. Enter the client directory
   ```cd client```
2. Open the config.json file with your text editor and replace the IP and PORT fields of the target server.
3. Run the client ```python .\main.py``` or ```python3 .\main.py```.

A client window will now appear and you can connect to the server and begin playing.

# How to play:

Placeholder.

# Author(s):





