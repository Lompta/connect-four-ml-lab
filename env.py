from concurrent.futures import process
import random
from xml.etree.ElementInclude import include
import numpy as np

from gym.core import Env
from gym.spaces import Space, Box

from policies import random_policy_without_illegal_moves
from game import ConnectFourGame

# NOTE - This class does not have render or seed
class ConnectFourEnv(Env):
    def __init__(self, rows, columns, opponent_policy = random_policy_without_illegal_moves, keeping_score = False, include_heuristics = False, anticipate_immediate_wins = False):
        self.active_game = ConnectFourGame(rows, columns)
        self.rows = rows
        self.columns = columns
        self.opponent_policy = opponent_policy
        self.keeping_score = keeping_score
        self.action_space = list(range(columns))
        self.observation_space_length = self.rows * self.columns * 3
        # Add two extra columns of observation for if each move wins for self or opponent, if we enable win detection
        if anticipate_immediate_wins:
            self.observation_space_length = self.observation_space_length + (self.columns * 2)
        self.observation_space = self.describe_embedding()
        self.training_wins = 0
        self.training_losses = 0
        self.training_ties = 0
        self.training_disqualifications = 0
        self.include_heuristics = include_heuristics
        self.anticipate_immediate_wins = anticipate_immediate_wins
        self.reset()

    def reset_records(self):
        self.training_wins = 0
        self.training_losses = 0
        self.training_ties = 0
        self.training_disqualifications = 0

    def reset(self):
        self.active_game = ConnectFourGame(self.rows, self.columns)
        if bool(random.getrandbits(1)):
            raw_observation = self.active_game.make_move(-1, self.opponent_policy(self.active_game))[0]
            processed_observation = []

            for s in range(self.rows * self.columns):
                if raw_observation[s] == -1:
                    processed_observation.append(1)
                else:
                    processed_observation.append(0)

                if raw_observation[s] == 1:
                    processed_observation.append(1)
                else:
                    processed_observation.append(0)

                if raw_observation[s] == 0:
                    processed_observation.append(1)
                else:
                    processed_observation.append(0)
                
            if self.anticipate_immediate_wins:
                observation_to_append = self.add_detected_wins_to_observation()
                processed_observation.extend(observation_to_append)

            return processed_observation
        # the observation is just clear if we go first
        return np.zeros(self.observation_space_length, np.int64)

    def update_reward_with_heuristics(self, reward, weight_for_active_threat=2, weight_for_threat=0.5, weight_for_opponent_active_threat=2, weight_for_opponent_threat=0.5):
        new_reward = reward
        for c in range(self.columns):
            column_array_for_move = self.active_game.board_as_columns[c]
            if self.active_game.board_state[column_array_for_move[0]] == 0:
                move = self.active_game.find_position_for_move(c)
                if self.active_game.check_victory(move, 1):
                    new_reward = new_reward + weight_for_active_threat
                if self.active_game.check_victory(move, -1):
                    new_reward = new_reward - weight_for_opponent_active_threat
            for r in range(self.active_game.rows):
                if self.active_game.board_state[self.active_game.board_as_columns[c][r]] == 0:
                    if self.active_game.check_victory(self.active_game.board_state[self.active_game.board_as_columns[c][r]], 1):
                        new_reward = new_reward + weight_for_threat
                    if self.active_game.check_victory(self.active_game.board_state[self.active_game.board_as_columns[c][r]], -1):
                        new_reward = new_reward - weight_for_opponent_threat
        return new_reward

    def add_detected_wins_to_observation(self):
        observation_array_to_append = []
        for c in range(self.columns):
            column_array_for_move = self.active_game.board_as_columns[c]
            if self.active_game.board_state[column_array_for_move[0]] == 0:
                move = self.active_game.find_position_for_move(c)
                if self.active_game.check_victory(move, 1):
                    observation_array_to_append.append(1)
                else:
                    observation_array_to_append.append(0)
                if self.active_game.check_victory(move, -1):
                    observation_array_to_append.append(1)
                else:
                    observation_array_to_append.append(0)
            else:
                observation_array_to_append.append(0)
                observation_array_to_append.append(0)
        return observation_array_to_append

    def step(self, action):
        reward = 0
        done = False

        move_response = self.active_game.make_move(1, action)
        game_metadata = move_response[1]

        if self.include_heuristics:
            reward = self.update_reward_with_heuristics(reward, weight_for_opponent_active_threat=5)

        # disqualification
        if game_metadata[2] == 1:
            reward = -50
            if (self.keeping_score):
                self.training_losses = self.training_losses + 1
                self.training_disqualifications = self.training_disqualifications + 1
        
        # victory!
        if game_metadata[1] == 1:
            reward = 30
            if (self.keeping_score):
                self.training_wins = self.training_wins + 1

        # game is complete
        if game_metadata[0] == 1:
            done = True

        # if game isn't complete, it's time for opponent to go
        if game_metadata[0] == 0:
            opponent_move = self.opponent_policy(self.active_game)

            move_response = self.active_game.make_move(-1, opponent_move)
            game_metadata = move_response[1]

            if self.include_heuristics:
                reward = self.update_reward_with_heuristics(reward, weight_for_active_threat=5)

            if game_metadata[1] == 1:
                reward = -30
                if (self.keeping_score):
                    self.training_losses = self.training_losses + 1

            if game_metadata[2] == 1:
                # don't give that much reward if the opponent just was disqualified
                reward = 10
                if (self.keeping_score):
                    self.training_losses = self.training_wins + 1

            if game_metadata[0] == 1:
                done = True
        
        raw_observation = move_response[0]
        processed_observation = []

        for s in range(self.rows * self.columns):
            if raw_observation[s] == -1:
                processed_observation.append(1)
            else:
                processed_observation.append(0)

            if raw_observation[s] == 1:
                processed_observation.append(1)
            else:
                processed_observation.append(0)

            if raw_observation[s] == 0:
                processed_observation.append(1)
            else:
                processed_observation.append(0)
        
        if done:
            if self.keeping_score and game_metadata[1] == 0 and game_metadata[2] == 0:
                self.training_ties = self.training_ties + 1
            self.reset()

        if self.anticipate_immediate_wins:
            observation_to_append = self.add_detected_wins_to_observation()
            processed_observation.extend(observation_to_append)
        return processed_observation, reward, done, {}

    def describe_embedding(self) -> Space:
        low = np.zeros(self.observation_space_length, np.int64)
        high = np.ones(self.observation_space_length, np.int64)
        return Box(
            np.array(low, dtype=np.int64),
            np.array(high, dtype=np.int64),
            dtype=np.int64,
        )