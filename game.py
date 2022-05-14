import numpy as np
from requests import get
import consts

from utils import get_space_in_direction, print_friendly_character

class ConnectFourGame():
    def __init__(self, rows, columns, board_state = None, is_disqualified = 0, is_won = 0, is_over = 0):
        self.rows = rows
        self.columns = columns
        self.is_disqualified = is_disqualified
        self.is_over = is_over
        self.is_won = is_won

        starting_state = np.zeros(rows * columns, np.int64)

        if board_state:
            self.board_state = board_state
        else:
            self.board_state = starting_state

        self.board_as_columns = []
        for c in range(columns):
            self.board_as_columns.append([])

        for x in range(rows * columns):
            self.board_as_columns[x % columns].append(x)

    def compute_streak(self, player, direction, space, current_tally):
        if space == -1:
            return current_tally
        if self.board_state[space] == player:
            next_space = get_space_in_direction(self.rows, self.columns, space, direction)
            return self.compute_streak(player, direction, next_space, current_tally + 1)
        return current_tally

    def check_legality(self, move):
        column_array_for_move = self.board_as_columns[move]
        
        if self.board_state[column_array_for_move[0]] != 0:
            return False
        return True
    
    def find_position_for_move(self, column):
        column_array_for_move = self.board_as_columns[column]
        position_for_move = column_array_for_move[0]
        for x in range(self.rows - 1):
            if self.board_state[column_array_for_move[x + 1]] == 0:
                position_for_move = column_array_for_move[x + 1]
            else:
                break
        return position_for_move

    # returns an array - first of board state, then three bools for: game is over, game was won, player was disqualified
    def make_move(self, player, move):
        column_array_for_move = self.board_as_columns[move]
        
        # if illegal move, disqualify
        if self.board_state[column_array_for_move[0]] != 0:
            self.is_disqualified = 1
            self.is_over = 1

        # make the move
        else:
            # figure out where piece goes
            position_for_move = self.find_position_for_move(move)
            # actually place the piece
            self.board_state[position_for_move] = player

            if self.check_victory(position_for_move, player):
                self.is_over = 1
                self.is_won = 1

            if self.is_over == 0 and self.check_tie():
                self.is_over = 1

        return [self.board_state, [self.is_over, self.is_won, self.is_disqualified]]

    def check_victory(self, played_piece_position, played_piece_player):
        space_to_left = get_space_in_direction(self.rows, self.columns, played_piece_position, consts.LEFT)
        space_to_right = get_space_in_direction(self.rows, self.columns, played_piece_position, consts.RIGHT)
        streak_to_left = self.compute_streak(played_piece_player, consts.LEFT, space_to_left, 0)
        streak_to_right = self.compute_streak(played_piece_player, consts.RIGHT, space_to_right, 0)
        if streak_to_left + streak_to_right + 1 >= 4:
            return True

        space_above_and_left = get_space_in_direction(self.rows, self.columns, played_piece_position, consts.UP_LEFT)
        space_below_and_right = get_space_in_direction(self.rows, self.columns, played_piece_position, consts.DOWN_RIGHT)
        streak_upper_left = self.compute_streak(played_piece_player, consts.UP_LEFT, space_above_and_left, 0)
        streak_lower_right = self.compute_streak(played_piece_player, consts.DOWN_RIGHT, space_below_and_right, 0)
        if streak_upper_left + streak_lower_right + 1 >= 4:
            return True

        space_above_and_right = get_space_in_direction(self.rows, self.columns, played_piece_position, consts.UP_RIGHT)
        space_below_and_left = get_space_in_direction(self.rows, self.columns, played_piece_position, consts.DOWN_LEFT)
        streak_upper_right = self.compute_streak(played_piece_player, consts.UP_RIGHT, space_above_and_right, 0)
        streak_lower_left = self.compute_streak(played_piece_player, consts.DOWN_LEFT, space_below_and_left, 0)
        if streak_upper_right + streak_lower_left + 1 >= 4:
            return True

        space_below = get_space_in_direction(self.rows, self.columns, played_piece_position, consts.DOWN)
        streak_below = self.compute_streak(played_piece_player, consts.DOWN, space_below, 0)
        if streak_below + 1 >= 4:
            return True

        return False

    # Only run this after checking for victory
    def check_tie(self):
        for s in range(self.rows * self.columns):
            if self.board_state[s] == 0:
                return False
        return True

    def draw_board(self):
        for r in range(self.rows):
            current_row = []
            for c in range(self.columns):
                current_row.append(print_friendly_character(self.board_state[(r * self.columns) + c]))
            print(*current_row)

