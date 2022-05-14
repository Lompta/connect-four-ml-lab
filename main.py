from game import ConnectFourGame
from policies import random_policy_without_illegal_moves, wins_and_blocks_wins_policy, wins_blocks_wins_and_prefers_center_policy, mixed_strategy_policy_factory, play_operator_policy
from utils import print_testing_outcomes

from gym.core import Env
import random
import numpy as np

from keras.layers import Dense, Flatten
from keras.models import Sequential
from keras.optimizers import adam_v2

from gym.spaces import Space, Box

from rl.agents.dqn import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy

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

train_env = ConnectFourEnv(6, 7)
test_env = ConnectFourEnv(6, 7, keeping_score=True)

# Compute dimensions
n_action = len(train_env.action_space)
input_shape = (1,) + train_env.observation_space.shape

# Create model
model = Sequential()
model.add(Dense(126, activation="elu", input_shape=input_shape))
model.add(Flatten())
model.add(Dense(42, activation="elu"))
model.add(Dense(42, activation="elu"))
model.add(Dense(n_action, activation="linear"))

# Defining the DQN
memory = SequentialMemory(limit=10000, window_length=1)

policy = LinearAnnealedPolicy(
    EpsGreedyQPolicy(),
    attr="eps",
    value_max=1.0,
    value_min=0.05,
    value_test=0.0,
    nb_steps=1000000,
)

dqn = DQNAgent(
    model=model,
    nb_actions=n_action,
    policy=policy,
    memory=memory,
    nb_steps_warmup=1000,
    gamma=0.5,
    target_model_update=1,
    delta_clip=0.01,
    enable_double_dqn=True,
)
dqn.compile(adam_v2.Adam(learning_rate=0.0002), metrics=["mae"])

# Training the model
dqn.fit(train_env, nb_steps=1000000)

# easy_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, random_policy_without_illegal_moves, random_policy_without_illegal_moves, wins_and_blocks_wins_policy])
# train_env.opponent_policy = easy_mixed_strategy_policy
# dqn.fit(train_env, nb_steps=30000)

# medium_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, random_policy_without_illegal_moves, wins_and_blocks_wins_policy])
# train_env.opponent_policy = medium_mixed_strategy_policy
# dqn.fit(train_env, nb_steps=30000)

# hard_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, wins_and_blocks_wins_policy, wins_blocks_wins_and_prefers_center_policy])
# train_env.opponent_policy = hard_mixed_strategy_policy
# dqn.fit(train_env, nb_steps=30000)

train_env.close()

# Testing the model
dqn.test(test_env, nb_episodes=1000, verbose=False, visualize=False)
print_testing_outcomes('Random', test_env.training_wins, test_env.training_losses, test_env.training_disqualifications, test_env.training_ties)
test_env.reset_records()

test_env.opponent_policy = wins_and_blocks_wins_policy
dqn.test(test_env, nb_episodes=100, verbose=False, visualize=False)
print_testing_outcomes('Wins and Blocks Wins', test_env.training_wins, test_env.training_losses, test_env.training_disqualifications, test_env.training_ties)
test_env.reset_records()

test_env.opponent_policy = wins_blocks_wins_and_prefers_center_policy
dqn.test(test_env, nb_episodes=100, verbose=False, visualize=False)
print_testing_outcomes('Wins, Blocks Wins, and Prefers Center', test_env.training_wins, test_env.training_losses, test_env.training_disqualifications, test_env.training_ties)
test_env.reset_records()

# test_env.opponent_policy = play_operator_policy
# dqn.test(test_env, nb_episodes=2, verbose=False, visualize=False)
# print_testing_outcomes('Operator', train_env.training_wins, train_env.training_losses, train_env.training_disqualifications, train_env.training_ties)
# test_env.reset_records()

test_env.close()