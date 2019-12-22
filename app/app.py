from flask import Flask, request
import requests
import json
import math

app = Flask(__name__)

game_choices = {
    1:"rock",
    2:"paper",
    3:"scissors",
    4:"lizard",
    5:"spock"
    }

winning_combinations = {
    1:[3,4],
    2:[1,5],
    3:[2,4],
    4:[2,5],
    5:[1,3]
    }

def get_choice(id):
    choice_json = {}
    choice_json["id"] = id
    choice_json["name"] = game_choices[id]
    return choice_json

def mapFromTo(x,a,b,c,d):
   y=(x-a)/(b-a)*(d-c)+c
   return y

def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)

def random_choice():
    url = "http://codechallenge.boohma.com/random"
    response = requests.request("GET", url)
    json_response = json.loads(response.text)
    return normal_round(mapFromTo(json_response["random_number"],1,100,1,5))

@app.route("/choices", methods=['GET'])
def choices():
    choices_list = []
    for game_choice in game_choices:
        choices_list.append(get_choice(game_choice))
    return app.response_class(
        response=json.dumps(choices_list),
        status=200,
        mimetype='application/json'
    )

@app.route("/choice", methods=['GET'])
def choice():
    return app.response_class(
        response=json.dumps(get_choice(random_choice())),
        status=200,
        mimetype='application/json'
    )

@app.route("/play", methods=['POST'])
def play():
    player_choice = request.get_json()["player"]
    computer_choice = random_choice()
    player_winning_choices = winning_combinations[player_choice]
    computer_winning_choices = winning_combinations[computer_choice]
    if player_choice == computer_choice:
        return {"tie":computer_choice}
    for player_winning_choice in player_winning_choices:
        if player_winning_choice == computer_choice:
            return {"player wins":computer_choice}
    for computer_winning_choice in computer_winning_choices:
        if player_choice == computer_winning_choice:
            return {"computer":computer_choice}            

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')