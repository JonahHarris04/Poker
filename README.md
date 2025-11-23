# Poker Game Multiplayer – Client Instructions
## Prerequisites

1. Python 3.10+ installed
2. pip install arcade python-socketio and the other dependencies in app and client
## Running the Project
1. Open app.py in one terminal.
2. Open at least two instances of client.py in two different terminals
5. The client will connect automatically and join the lobby. 
   1. You can toggle ready using the Ready button. 
   2. Once all players are ready, the Start Game button becomes active.

## Notes
- The client will display:
  - Your hand cards 
  - Community cards 
  - Whose turn it is
  - The current bet amount or other actions
  - Your current hand rank
  - Your chips and the total pot 
  - Action buttons: Check, Fold, Bet, Call, Raise, All-in

## Troubleshooting
- If you cannot connect, make sure app.py is running.
- If you need to change the window size, you may do so at the top of client.py