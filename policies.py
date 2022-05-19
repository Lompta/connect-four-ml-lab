import random

def random_policy(game):
    return random.randrange(game.columns)

def random_policy_without_illegal_moves(game):
    legal_moves_array = []
    for i in range(game.columns):
        if game.check_legality(i):
            legal_moves_array.append(i)

    index_in_legal_moves_array = random.randrange(len(legal_moves_array))
    return legal_moves_array[index_in_legal_moves_array]

def wins_and_blocks_wins_policy(game):
    move_scores_array = []
    candidate_moves = []

    for i in range(game.columns):
        move = game.find_position_for_move(i)
        if not game.check_legality(i):
            move_scores_array.append(-1)
        elif game.check_victory(move, -1):
            move_scores_array.append(2)
        elif game.check_victory(move, 1):
            move_scores_array.append(1)
        else:
            move_scores_array.append(0)

    best_move_category = max(move_scores_array)

    for i in range(game.columns):
        if move_scores_array[i] == best_move_category:
            candidate_moves.append(i)

    index_for_move = random.randrange(len(candidate_moves))
    return candidate_moves[index_for_move]

# this policy currently only works for boards of 7 columns 
def wins_blocks_wins_and_prefers_center_policy(game):
    centrality_weights = [0, 1, 2, 3, 2, 1, 0]
    move_scores_array = []
    candidate_moves = []

    for i in range(game.columns):
        move = game.find_position_for_move(i)
        if not game.check_legality(i):
            move_scores_array.append(-100)
        elif game.check_victory(move, -1):
            move_scores_array.append(200)
        elif game.check_victory(move, 1):
            move_scores_array.append(100 + centrality_weights[i])
        else:
            move_scores_array.append(centrality_weights[i])

    best_move_category = max(move_scores_array)

    for i in range(game.columns):
        if move_scores_array[i] == best_move_category:
            candidate_moves.append(i)

    index_for_move = random.randrange(len(candidate_moves))
    return candidate_moves[index_for_move]

def play_operator_policy(game):
    game.draw_board()
    action = input('What move?')
    # 1 indexed
    return int(action) - 1

def mixed_strategy_policy_factory(policies):
    def mixed_strategy_policy(game):
        chosen_policy_index = random.randrange(len(policies))
        return policies[chosen_policy_index](game)
    return mixed_strategy_policy