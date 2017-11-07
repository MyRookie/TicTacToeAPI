# TicTacToeAPI
RESTful API for tic-tac-toe game

## Start the server
run command:

pip install -r requirements.txt

to install packages.

run command:

./manage.py makemigrations && ./manage.py migrate

to create tables in database

run command:
./manage.py runserver

## API Documentation

 http://localhost:8000/api/v1/games/
 
 POST:
 {  
   "game":{  
      "board":"---------"
   }
 }
 
 or
 {  
   "game":{  
      "board":"---X-----"
   }
 }
 
 to start a game.
 
 GET request to get a list of games
 
 http://localhost:8000/api/v1/games/{game-id}
 
 PUT:
 {
    "game": {
        "token": "1dc95b0b", //this is game id
        "status": "RUNNING",
        "board": "X-------O"
    }
 }
 user send the board including the move
 
 DELETE:
 Delete the game
 
 GET:
 Get current game information
