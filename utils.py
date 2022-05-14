import consts

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