import numpy
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import create_observation_from_board_description
from game import ConnectFourGame
# import subprocess
from consts import NO_WIN_DETECTION_PATH, WIN_DETECTION_PATH
from keras.models import load_model

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

@app.route("/get_api_move", methods=["POST"])
def run_script():
    model = load_model(WIN_DETECTION_PATH)
    
    request_data = request.get_json()
    game_state = request_data["game"]

    print(game_state)

    game = ConnectFourGame(6, 7, game_state)
    input_data = create_observation_from_board_description(game, True)

    result = numpy.argmax(model.predict(input_data))
    wrapped_result = {"move": str(result)};
    return jsonify(wrapped_result);

app.run()