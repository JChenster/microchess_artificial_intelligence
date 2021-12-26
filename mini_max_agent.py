from piece import BLACK, WHITE
from microchess import DRAW

class MiniMaxAgent:

    def __init__(self, heuristic_fxn, depth):
        '''
        Initialize a minimax agent that plays games via heuristic_fxn
        heuristic_fxn --- a function that given a Position, returns an value
        '''
        self.heuristic_fxn = heuristic_fxn
        self.depth = depth

    def choose_next_move(self, pos):
        '''
        Given the current position, chooses the next move
        This uses minimax
        pos --- Current position
        '''
        best_val, best_move = self.minimax(pos, self.depth, self.heuristic_fxn)
        return best_move
        
    def minimax(self, pos, depth, heuristic_fxn):
        '''
        We assume the values are relative to BLACK
        ie. BLACK is the maximizing agent and WHITE is the minimizing agent

        Returns [best_val, best_move]
        '''
        if pos.winner() != -1:
            if pos.winner() == DRAW:
                return [0, None]
            elif pos.winner() == BLACK:
                return [float("inf"), None]
            else:
                return [float("-inf"), None]
            
        if depth == 0:
            return [heuristic_fxn(pos), None]
        
        best_move = None
        if pos.get_turn() == BLACK:
            value = float("-inf")
            for move in pos.player_legal_moves():
                child_pos = pos.result_copy(move)
                child_val = self.minimax(child_pos, depth - 1, heuristic_fxn)[0]
                if child_val >= value:
                    value = child_val
                    best_move = move
            return [value, best_move]
        else:
            value = float("inf")
            for move in pos.player_legal_moves():
                child_pos = pos.result_copy(move)
                child_val = self.minimax(child_pos, depth - 1, heuristic_fxn)[0]
                if child_val <= value:
                    value = child_val
                    best_move = move
            return [value, best_move]