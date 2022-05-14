from ml import create_dqn, train_dqn, test_dqn
from env import ConnectFourEnv

train_env = ConnectFourEnv(6, 7)
test_env = ConnectFourEnv(6, 7, keeping_score=True)

dqn = create_dqn(train_env)
train_dqn(dqn, train_env)
train_env.close()

test_dqn(dqn, test_env)
test_env.close()