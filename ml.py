from rl.agents.dqn import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy

from keras.layers import Dense, Flatten
from keras.models import Sequential, save_model, load_model
from keras.optimizers import adam_v2

from policies import random_policy_without_illegal_moves, wins_and_blocks_wins_policy, wins_blocks_wins_and_prefers_center_policy, mixed_strategy_policy_factory, play_operator_policy
from utils import print_testing_outcomes
from consts import NO_WIN_DETECTION_PATH, WIN_DETECTION_PATH 

def create_dqn(env, load_from_checkpoint=False):
    # Compute dimensions
    n_action = len(env.action_space)
    input_shape = (1,) + env.observation_space.shape

    if load_from_checkpoint:
        load_path = NO_WIN_DETECTION_PATH
        if env.anticipate_immediate_wins:
            load_path = WIN_DETECTION_PATH
        model = load_model(load_path)
    else:
        # Create model
        model = Sequential()
        model.add(Dense(126, activation="elu", input_shape=input_shape))
        model.add(Flatten())
        model.add(Dense(84, activation="relu"))
        model.add(Dense(84, activation="relu"))
        model.add(Dense(n_action, activation="linear"))

    # Defining the DQN
    memory = SequentialMemory(limit=10000, window_length=1)

    policy = LinearAnnealedPolicy(
        EpsGreedyQPolicy(),
        attr="eps",
        value_max=0.20,
        value_min=0.05,
        value_test=0.0,
        nb_steps=500000
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
        enable_double_dqn=True
    )

    return dqn

def train_dqn(dqn, env, save_checkpoint=False):
    dqn.compile(adam_v2.Adam(learning_rate=0.0001), metrics=["mae"])

    # Training the model
    env.opponent_policy = wins_and_blocks_wins_policy
    dqn.fit(env, nb_steps=500000)

    if save_checkpoint:
        save_path = NO_WIN_DETECTION_PATH
        if env.anticipate_immediate_wins:
            save_path = WIN_DETECTION_PATH
            save_model(dqn.model, save_path, True)

    # easy_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, random_policy_without_illegal_moves, random_policy_without_illegal_moves, wins_and_blocks_wins_policy])
    # env.opponent_policy = easy_mixed_strategy_policy
    # dqn.fit(env, nb_steps=40000)

    # medium_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, random_policy_without_illegal_moves, wins_and_blocks_wins_policy])
    # env.opponent_policy = medium_mixed_strategy_policy
    # dqn.fit(env, nb_steps=40000)

    # hard_mixed_strategy_policy = mixed_strategy_policy_factory([random_policy_without_illegal_moves, wins_and_blocks_wins_policy, wins_blocks_wins_and_prefers_center_policy])
    # env.opponent_policy = hard_mixed_strategy_policy
    # dqn.fit(env, nb_steps=200000)

def test_dqn(dqn, env):
    # Testing the model
    dqn.test(env, nb_episodes=1000, verbose=False, visualize=False)
    print_testing_outcomes('Random', env.training_wins, env.training_losses, env.training_disqualifications, env.training_ties)
    env.reset_records()

    env.opponent_policy = wins_and_blocks_wins_policy
    dqn.test(env, nb_episodes=1000, verbose=False, visualize=False)
    print_testing_outcomes('Wins and Blocks Wins', env.training_wins, env.training_losses, env.training_disqualifications, env.training_ties)
    env.reset_records()

    env.opponent_policy = wins_blocks_wins_and_prefers_center_policy
    dqn.test(env, nb_episodes=1000, verbose=False, visualize=False)
    print_testing_outcomes('Wins, Blocks Wins, and Prefers Center', env.training_wins, env.training_losses, env.training_disqualifications, env.training_ties)
    env.reset_records()

    env.opponent_policy = play_operator_policy
    dqn.test(env, nb_episodes=3, verbose=False, visualize=False)
    print_testing_outcomes('Operator', env.training_wins, env.training_losses, env.training_disqualifications, env.training_ties)
    env.reset_records()