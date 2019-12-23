from flask import Flask, request
import requests
import json
import math
from flask_cors import CORS

app = Flask(__name__)
# CORS allows API to be called from ajax in browser from 3rd party websites
CORS(app)

# Mapping of choices for the game
game_choices = {
    1:"rock",
    2:"paper",
    3:"scissors",
    4:"lizard",
    5:"spock"
    }

# Mapping of game rules, what choice wins againest another choice
winning_combinations = {
    1:[3,4],
    2:[1,5],
    3:[2,4],
    4:[2,5],
    5:[1,3]
    }

running_scoreboard = []

# Creates a json like structure for a requested game choice based on id passed to it
# Input: integer of game choice
# Returns: {"id":id,"name":stringOfId}
def get_choice(id):
    choice_json = {}
    choice_json["id"] = id
    choice_json["name"] = game_choices[id]
    return choice_json

# Takes a value x between range A and scales to range B
# Input: x=value, a=RangeAMin, b=RangeAMax, c=RangeBMin, d=RangeBMax
# Returns: calculated value
def mapFromTo(x,a,b,c,d):
   y=(x-a)/(b-a)*(d-c)+c
   return y

# Round up and down based on decimal
def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)

# Gets an integer from codechallenge random integer endpoint
# Returns: int betwen 1-5
def random_choice():
    url = "http://codechallenge.boohma.com/random"
    response = requests.request("GET", url)
    json_response = json.loads(response.text)
    return normal_round(mapFromTo(json_response["random_number"],1,100,1,5))

# GET /choices returns the mapping of all choices for the game
@app.route("/choices", methods=['GET'])
def choices():
    choices_list = []
    for game_choice in game_choices:
        choices_list.append(get_choice(game_choice))
    response = app.make_response(json.dumps(choices_list))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.mimetype='application/json'
    return response
    
# GET /choice returns a random game choice
@app.route("/choice", methods=['GET'])
def choice():
    response = app.make_response(json.dumps(get_choice(random_choice())))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.mimetype='application/json'
    return response

# GET /scoreboard returns last 10 game scores
@app.route("/scoreboard", methods=['GET'])
def scoreboard():
    response = app.make_response(json.dumps(running_scoreboard))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.mimetype='application/json'
    return response

# Adds outcome of game to running scoreboard, only saves last 10 games played
# Input: JSON like structure of game outcome
def add_to_scoreboard(game_result):
    if len(running_scoreboard) == 10:
        running_scoreboard.pop()
    running_scoreboard.insert(0,game_result)
    return

# POST /play takes the players game choice, generates a random computer player choice and returns who won or a tie
# also saves the outcome to scoreboard
@app.route("/play", methods=['POST'])
def play():
    player_choice = request.get_json()["player"]
    computer_choice = random_choice()
    player_winning_choices = winning_combinations[player_choice]
    computer_winning_choices = winning_combinations[computer_choice]
    if player_choice == computer_choice:
        game_result = {"results":"tie","player":player_choice,"computer":computer_choice}
        add_to_scoreboard(game_result)
        response = app.make_response(json.dumps(game_result))
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.mimetype='application/json'
        return response
    for player_winning_choice in player_winning_choices:
        if player_winning_choice == computer_choice:
            game_result = {"results":"win","player":player_choice,"computer":computer_choice}
            add_to_scoreboard(game_result)
            response = app.make_response(json.dumps(game_result))
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.mimetype='application/json'
            return response
    for computer_winning_choice in computer_winning_choices:
        if player_choice == computer_winning_choice:
            game_result = {"results":"lose","player":player_choice,"computer":computer_choice}
            add_to_scoreboard(game_result)
            response = app.make_response(json.dumps(game_result))
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.mimetype='application/json'
            return response

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')