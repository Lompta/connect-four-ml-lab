## Connect Four ML Lab
Dependencies:
- rl
- gym
- keras

Once you have these, just run main.py.
Ml.py has various commented out options for things like training for more/less time, testing vs. different opponents/strategies, playing a game against the DQN yourself, etc. I plan to make this more straightforwardly customizable in future releases.

The DQN only receives reward at the end of each episode - ie. once per game. This causes it not to do very well against stronger strategies. It can do very well against deterministic strategies it's trained on, or against random strategies if trained against random strategies.

A few possible ways to improve performance:
- Give the DQN reward based on straightforward Connect 4 heuristics - ie. give it some reward if it has a threat to win, or negative reward if the opponent has the same.
- Give the DQN observations other than the pure, unfiltered game state - ie. give it an observation bool for each column for each of "I can win by playing this column" or "opponent can win by playing this column".
- Try using self-play, maybe with something like a lightweight AlphaZero style implementation.

The third option would be pure improvement, though it'd be a pretty different project - I may add some extra, different files that explore this. The first two options are more like tradeoffs: the DQN would surely do better if it had Connect 4 heuristics "baked in", but to some degree that defeats the purpose; part of the point of the project is for the agent to learn how Connect 4 works in the first place!

Other potential enhancements:
- Saving/loading trained models - this is really easy, but the models aren't really good enough to justify it yet. If I make them perform better, this could be used for...
- A hosted GUI for people to play against Connect 4 bots of various levels. Probably the heuristics I use for testing, plus some trained agents of varying strength.