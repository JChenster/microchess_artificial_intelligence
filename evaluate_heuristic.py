import random
import time

from piece import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN, BLACK, WHITE
from microchess import MicroChess, DRAW
from mini_max_agent import MiniMaxAgent

def value_based_heuristic(pos, weights: 'List[int]'):
    '''
    Given a position, returns an estimate of the value of the position for BLACK
    by assigning each alive player with a value as defined in weights

    pos --- Position in game
    weights --- List[int] representing the value of each piece 
        where the index corresponds to our enumeration of the pieces
    '''
    weights = [0, 0] + weights
    black_pieces_value, white_pieces_value = 0, 0
    for piece in pos.get_black_pieces():
        black_pieces_value += weights[piece.get_piece_type()]
    for piece in pos.get_white_pieces():
        white_pieces_value += weights[piece.get_piece_type()]
    return black_pieces_value - white_pieces_value

def simple_heuristic(pos):
    '''
    Heuristic where different pieces have different values
    '''
    weights = [6, 3, 3, 1]
    return value_based_heuristic(pos, weights)

def uniform_heuristic(pos):
    '''
    Heuristic where all pieces have the same value
    '''
    return len(pos.get_black_pieces()) - len(pos.get_white_pieces())

def random_heuristic(pos):
    '''
    Play randomly, used more as a placeholder than anything
    '''
    return random.random()

def compare_heuristic(heuristic_fxn_1, heuristic_fxn_2, num_games, prob, depth) -> float:
    '''
    Compares two heuristic functions against each other by creating 2 minimax agents
    Then battle them against each other in num_games 
    Return the win percentage of heuristic_fxn_1

    heuristic_fxn_1 --- function that given Position returns a value
    heuristic_fxn_2 --- function that given Position returns a value
    num_games --- the number of games each individual should play to determine 
        their fitness, int
    prob --- Probability that the agents will not play randomly
    depth --- Depth of minimax search
    '''
    start = time.time()
    p1 = MiniMaxAgent(heuristic_fxn_1, depth)
    if heuristic_fxn_2 != random_heuristic:
        p2 = MiniMaxAgent(heuristic_fxn_2, depth)
    p1_wins, p2_wins, draws = 0, 0, 0

    mc = MicroChess()
    for i in range(num_games):
        pos = mc.initial_pos()
        while pos.winner() == -1:
            # Play with our strategy
            if random.random() < prob:
                # We have p1 and p2 alternate being BLACK/WHITE
                # When is even, p1 acts as BLACK
                if pos.get_turn() == i % 2:
                    move = p1.choose_next_move(pos)
                else:
                    if heuristic_fxn_2 != random_heuristic:
                        move = p2.choose_next_move(pos)
                    else:
                        move = random.choice(pos.player_legal_moves())
            # Play randomly
            else:
                move = random.choice(pos.player_legal_moves())
            pos = pos.result(move)
        if pos.winner() == DRAW:
            draws += 1
        elif (pos.winner() == BLACK and i % 2 == BLACK) or (pos.winner() == WHITE and i % 2 == WHITE):
            p1_wins += 1
        else:
            p2_wins += 1
        #print(f"Finished running iter {i}")
    #print(f"Simulation took {round(time.time() - start, 2)}s")
    #print(f"p1_wins: {p1_wins}, p2_wins: {p2_wins}, draws: {draws}")
    return (p1_wins + draws / 2) / num_games
