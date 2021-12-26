BLACK = 0
WHITE = 1

KING = 0
QUEEN = 1
ROOK = 2
BISHOP = 3
KNIGHT = 4
PAWN = 5

BOARD_LENGTH = 5
BOARD_WIDTH = 4

DIAGONAL_DIRECTIONS = [[-1, -1], [1, 1], [1, -1], [-1, 1]]
STRAIGHT_DIRECTIONS = [[0, 1], [1, 0], [-1, 0], [0, -1]]

class Piece():
    def __init__(self, color, pos, piece_type, legal_moves, cant_check_fxn):
        '''
        Initialize our piece
        
        color --- BLACK, WHITE
        pos --- position on board (row, col) starting from upper corner
        type --- piece type
        legal_moves --- function that given a position returns a list of legal moves
        cant_check_fxn(pos, king_pos) --- function that returns True if there is a shortcircuit way to know
            that the piece at pos can't check the opposing king at king_pos
        '''
        self.color = color
        self.pos = pos
        self.original_pos = pos
        self.piece_type = piece_type
        self.legal_moves = legal_moves
        self.cant_check_fxn = cant_check_fxn

    def get_color(self):
        return self.color

    def get_pos(self):
        return self.pos

    def get_legal_moves(self, board):
        '''
        Given a board (6x6) matrix, returns what moves are legal to get to
        '''
        return self.legal_moves(self.pos, board)

    def get_piece_type(self):
        return self.piece_type

    def get_original_pos(self):
        return self.original_pos

    def __str__(self):
        s = "B" if self.color == BLACK else "W"
        str_rep = {
            KING: "K",
            QUEEN: "Q",
            ROOK: "R",
            BISHOP: "B",
            KNIGHT: "N",
            PAWN: "P"
        }
        return s + str_rep.get(self.piece_type)

    def move_to(self, new_pos):
        '''
        Moves piece to new_pos
        First checks to make sure that it is valid
        '''
        self.pos = new_pos

    def cant_check(self, king_pos):
        return self.cant_check_fxn(self.pos, king_pos)

'''
We define positive x-axis as increasing row
We define positive y-axis as increasing column
'''

def continuous_legal_moves(pos, board, directions):
    '''
    Return legal moves for pieces that move continuously ie rook, queen, bishop
    These pieces can move in their respective directions until either out of bounds
    or they hit another piece
    '''
    piece_color = board[pos[0]][pos[1]].get_color()
    ret = []
    for dx, dy in directions:
        x, y = pos[0] + dx, pos[1] + dy
        while 0 <= x < BOARD_LENGTH and 0 <= y < BOARD_WIDTH and (board[x][y] is None or board[x][y].get_color() != piece_color):
            ret.append([x, y])
            # We found another piece so we must not go further
            if board[x][y] is not None:
                break
            x += dx
            y += dy
    return ret

class King(Piece):
    def __init__(self, color, pos):
        def king_legal_moves(pos, board):
            piece_color = board[pos[0]][pos[1]].get_color()
            ret = []
            # All directions as long as they are 1 away
            directions = STRAIGHT_DIRECTIONS + DIAGONAL_DIRECTIONS
            for dx, dy in directions:
                x, y = pos[0] + dx, pos[1] + dy
                # Add check for check
                if 0 <= x < BOARD_LENGTH and 0 <= y < BOARD_WIDTH and (board[x][y] is None or board[x][y].get_color() != piece_color):
                    ret.append([x, y])
            return ret

        def cant_check_fxn(pos, king_pos):
            '''
            Returns if is impossible to check the king at this position
            King can't be more than one radius away
            '''
            return abs(pos[0] - king_pos[0]) > 1 or abs(pos[1] - king_pos[1]) > 1
        super().__init__(color, pos, KING, king_legal_moves, cant_check_fxn)

class Queen(Piece):
    def __init__(self, color, pos):
        def queen_legal_moves(pos, board):
            '''
            Any diagonal/straight direction unimpeded by a piece
            '''
            return continuous_legal_moves(pos, board, STRAIGHT_DIRECTIONS + DIAGONAL_DIRECTIONS)
        super().__init__(color, pos, QUEEN, queen_legal_moves)

class Rook(Piece):
    def __init__(self, color, pos):
        def rook_legal_moves(pos, board):
            '''
            Any straight direction unimpeded by a piece
            '''
            return continuous_legal_moves(pos, board, STRAIGHT_DIRECTIONS)
        def cant_check_fxn(pos, king_pos):
            '''
            Returns if is impossible to check the king at this position
            King must be in the same x or y pos
            '''
            return pos[0] != king_pos[0] and pos[1] != king_pos[1]
        super().__init__(color, pos, ROOK, rook_legal_moves, cant_check_fxn)

class Bishop(Piece):
    def __init__(self, color, pos):
        def bishop_legal_moves(pos, board):
            '''
            Any diagonal direction unimpeded by a piece
            '''
            return continuous_legal_moves(pos, board, DIAGONAL_DIRECTIONS)
        def cant_check_fxn(pos, king_pos):
            '''
            Returns if is impossible to check the king at this position
            '''
            return abs(pos[0] - king_pos[0]) != abs(pos[1] - king_pos[1])
        super().__init__(color, pos, BISHOP, bishop_legal_moves, cant_check_fxn)

class Knight(Piece):
    def __init__(self, color, pos):
        def knight_legal_moves(pos, board):
            piece_color = board[pos[0]][pos[1]].get_color()
            ret = []
            # All directions as long as they are 1 away
            directions = [[-1, 2], [2, -1], [-1, -2], [-2, -1], [2, 1], [1, 2], [-2, 1], [1, -2]]
            for dx, dy in directions:
                x, y = pos[0] + dx, pos[1] + dy
                if 0 <= x < BOARD_LENGTH and 0 <= y < BOARD_WIDTH and (board[x][y] is None or board[x][y].get_color() != piece_color):
                    ret.append([x, y])
            return ret
        def cant_check_fxn(pos, king_pos):
            '''
            Returns if the piece at pos can check the king at king_pos
            '''
            dists = [abs(pos[0] - king_pos[0]), abs(pos[1] - king_pos[1])]
            return dists != [1,2] and dists != [2,1]
        super().__init__(color, pos, KNIGHT, knight_legal_moves, cant_check_fxn)

class Pawn(Piece):
    def __init__(self, color, pos):
        def pawn_legal_moves(pos, board):
            ret = []
            x, y = pos[0], pos[1]
            piece_color = board[x][y].get_color()
            # At the beginning, pawns can possibly move up 2 spaces
            '''
            if pos == self.original_pos:
                if color == BLACK and 0 <= x+2 < BOARD_LENGTH and board[x+2][y] is None:
                    ret.append([x+2, y])
                if color == WHITE and 0 <= x-2 < BOARD_LENGTH and board[x-2][y] is None:
                    ret.append([x-2, y])
            '''
            # Can move forward 1 as long as it's empty
            if color == BLACK and 0 <= x+1 < BOARD_LENGTH and board[x+1][y] is None:
                ret.append([x+1, y])
            if color == WHITE and 0 <= x-1 < BOARD_LENGTH and board[x-1][y] is None:
                ret.append([x-1, y])
            # Can move diagonal while capturing
            capture_directions = [[1, -1], [1, -1]]
            for dx, dy in capture_directions:
                if color == BLACK:
                    dx = -1
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < BOARD_LENGTH and 0 <= new_y < BOARD_WIDTH and board[new_x][new_y] is not None and board[new_x][new_y].get_color() != piece_color:
                    ret.append([new_x, new_y])
            return ret
        def cant_check_fxn(pos, king_pos):
            '''
            Returns if the piece at pos can check the king at king_pos
            '''
            return abs(pos[0] - king_pos[0]) != 1 or abs(pos[1] - king_pos[1]) != 1
        super().__init__(color, pos, PAWN, pawn_legal_moves, cant_check_fxn)
