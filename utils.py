import consts
import numpy as np

def get_space_in_direction(rows, columns, position, direction):
    match direction:
        case consts.UP:
            return get_space_above(columns, position)
        case consts.DOWN:
            return get_space_below(columns, rows, position)
        case consts.LEFT:
            return get_space_to_left(columns, position)
        case consts.RIGHT:
            return get_space_to_right(columns, position)
        case consts.UP_RIGHT:
            return get_space_above_and_right(columns, position)
        case consts.UP_LEFT:
            return get_space_above_and_left(columns, position)
        case consts.DOWN_RIGHT:
            return get_space_below_and_right(columns, rows, position)
        case consts.DOWN_LEFT:
            return get_space_below_and_left(columns, rows, position)

def get_space_to_left(columns, position):
        if position % columns == 0:
            return -1
        return position - 1
    
def get_space_to_right(columns, position):
    if position % columns == columns - 1:
        return -1
    return position + 1

def get_space_above(columns, position):
    if position < columns:
        return -1
    return position - columns

def get_space_below(columns, rows, position):
    if position >= columns * (rows - 1):
        return -1
    return position + columns

def get_space_above_and_right(columns, position):
    space_above = get_space_above(columns, position)
    if space_above == -1:
        return -1
    return get_space_to_right(columns, space_above)

def get_space_above_and_left(columns, position):
    space_above = get_space_above(columns, position)
    if space_above == -1:
        return -1
    return get_space_to_left(columns, space_above)

def get_space_below_and_right(columns, rows, position):
    space_below = get_space_below(columns, rows, position)
    if space_below == -1:
        return -1
    return get_space_to_right(columns, space_below)

def get_space_below_and_left(columns, rows, position):
    space_below = get_space_below(columns, rows, position)
    if space_below == -1:
        return -1
    return get_space_to_left(columns, space_below)

def create_observation_from_board_description(game, anticipate_wins_mode):
    result = []
    for s in range(game.rows * game.columns):
            if game.board_state[s] == -1:
                result.append(1)
            else:
                result.append(0)

            if game.board_state[s] == 1:
                result.append(1)
            else:
                result.append(0)

            if game.board_state[s] == 0:
                result.append(1)
            else:
                result.append(0)
    
    if anticipate_wins_mode:
        observation_array_to_append = np.zeros(game.columns * 4)
        for c in range(game.columns):
            column_array_for_move = game.board_as_columns[c]
            if game.board_state[column_array_for_move[0]] == 0:
                move = game.find_position_for_move(c)
                if game.check_victory(move, 1):
                    observation_array_to_append[c * 4] = 1
                if game.check_victory(move, -1):
                    observation_array_to_append[c * 4 + 1] = 1

                if (move - game.columns) >= 0:
                    if game.check_victory(move - game.columns, 1):
                        observation_array_to_append[c * 4 + 2] = 1
                    if game.check_victory(move - game.columns, -1):
                        observation_array_to_append[c * 4 + 3] = 1
        
    result.extend(observation_array_to_append)

    result_numpy = np.array(result)
    # todo - improve hardcoding - right now 154 corresponds exactly to detect wins mode on a 7x6 board, but this isn't necessary
    shaped_result = result_numpy.reshape(1, 1, 154)
    return shaped_result

def print_friendly_character(char):
    if char == -1:
        return 'x'
    if char == 1:
        return 'o'
    return '-'

def print_testing_outcomes(opponent_name, wins, losses, dqs, ties):
    print('Results vs ' + opponent_name)
    print('Training wins: ' + str(wins))
    print('Training losses: ' + str(losses) + ', of which ' + str(dqs) + ' were disqualifications')
    print('Training ties: ' + str(ties))