from ml import create_dqn, train_dqn, test_dqn
from env import ConnectFourEnv
from keras.optimizers import adam_v2

train_env = ConnectFourEnv(6, 7, include_heuristics=True, anticipate_immediate_wins=True)
test_env = ConnectFourEnv(6, 7, keeping_score=True, anticipate_immediate_wins=True)

dqn = create_dqn(train_env, True)
train_dqn(dqn, train_env, True)
train_env.close()

# dqn.compile(adam_v2.Adam(learning_rate=0.0002), metrics=["mae"])
test_dqn(dqn, test_env)
test_env.close()