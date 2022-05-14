import random
import numpy as np

from gym.core import Env
from gym.spaces import Space, Box

from policies import random_policy_without_illegal_moves
from game import ConnectFourGame

# NOTE - This class does not have render or seed
class ConnectFourEnv(Env):
    def __init__(self, rows, columns, opponent_policy = random_policy_without_illegal_moves, keeping_score = False):
        self.active_game = ConnectFourGame(rows, columns)
        self.rows = rows
        self.columns = columns
        self.opponent_policy = opponent_policy
        self.keeping_score = keeping_score
        self.reset()
        self.action_space = list(range(columns))
        self.observation_space = self.describe_embedding()
        self.training_wins = 0
        self.training_losses = 0
        self.training_ties = 0
        self.training_disqualifications = 0

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

            return processed_observation
        # the observation is just clear if we go first
        return np.zeros(self.rows * self.columns * 3, np.int64)

    def step(self, action):
        reward = 0
        done = False

        move_response = self.active_game.make_move(1, action)
        game_metadata = move_response[1]

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
        return processed_observation, reward, done, {}

    def describe_embedding(self) -> Space:
        low = np.zeros(self.rows * self.columns * 3, np.int64)
        high = np.ones(self.rows * self.columns * 3, np.int64)
        return Box(
            np.array(low, dtype=np.int64),
            np.array(high, dtype=np.int64),
            dtype=np.int64,
        )