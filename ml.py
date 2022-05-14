from rl.agents.dqn import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy

from keras.layers import Dense, Flatten
from keras.models import Sequential
from keras.optimizers import adam_v2

from policies import random_policy_without_illegal_moves, wins_and_blocks_wins_policy, wins_blocks_wins_and_prefers_center_policy, mixed_strategy_policy_factory, play_operator_policy
from utils import print_testing_outcomes

def create_dqn(env):
    # Compute dimensions
    n_action = len(env.action_space)
    input_shape = (1,) + env.observation_space.shape

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
        nb_steps=20000,
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

    return dqn

def train_dqn(dqn, env):
    dqn.compile(adam_v2.Adam(learning_rate=0.0002), metrics=["mae"])

    # Training the model
    dqn.fit(env, nb_steps=20000)

    # easy_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, random_policy_without_illegal_moves, random_policy_without_illegal_moves, wins_and_blocks_wins_policy])
    # train_env.opponent_policy = easy_mixed_strategy_policy
    # dqn.fit(train_env, nb_steps=30000)

    # medium_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, random_policy_without_illegal_moves, wins_and_blocks_wins_policy])
    # train_env.opponent_policy = medium_mixed_strategy_policy
    # dqn.fit(train_env, nb_steps=30000)

    # hard_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, wins_and_blocks_wins_policy, wins_blocks_wins_and_prefers_center_policy])
    # train_env.opponent_policy = hard_mixed_strategy_policy
    # dqn.fit(train_env, nb_steps=30000)

def test_dqn(dqn, env):
    # Testing the model
    dqn.test(env, nb_episodes=1000, verbose=False, visualize=False)
    print_testing_outcomes('Random', env.training_wins, env.training_losses, env.training_disqualifications, env.training_ties)
    env.reset_records()

    env.opponent_policy = wins_and_blocks_wins_policy
    dqn.test(env, nb_episodes=100, verbose=False, visualize=False)
    print_testing_outcomes('Wins and Blocks Wins', env.training_wins, env.training_losses, env.training_disqualifications, env.training_ties)
    env.reset_records()

    env.opponent_policy = wins_blocks_wins_and_prefers_center_policy
    dqn.test(env, nb_episodes=100, verbose=False, visualize=False)
    print_testing_outcomes('Wins, Blocks Wins, and Prefers Center', env.training_wins, env.training_losses, env.training_disqualifications, env.training_ties)
    env.reset_records()

    # test_env.opponent_policy = play_operator_policy
    # dqn.test(test_env, nb_episodes=2, verbose=False, visualize=False)
    # print_testing_outcomes('Operator', train_env.training_wins, train_env.training_losses, train_env.training_disqualifications, train_env.training_ties)
    # test_env.reset_records()