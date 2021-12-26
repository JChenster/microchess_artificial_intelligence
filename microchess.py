from piece import Piece, King, Queen, Rook, Bishop, Knight, Pawn, WHITE, BLACK, KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN, BOARD_LENGTH, BOARD_WIDTH

DRAW = 2

class MicroChess:
    '''
    We have made several simplifications to make coding this game easier
        --- No pawn promotions
        --- No pawn en passant
    '''

    def __init__(self):
        '''
        Initialize the game board
        '''
        board = [[None] * BOARD_WIDTH for _ in range(BOARD_LENGTH)]

        board[0][0] = King(BLACK, [0,0])
        board[0][1] = Knight(BLACK, [0,1])
        board[0][2] = Bishop(BLACK, [0,2])
        board[0][3] = Rook(BLACK, [0,3])
        board[1][0] = Pawn(BLACK, [1,0])

        board[4][0] = Rook(WHITE, [4,0])
        board[4][1] = Bishop(WHITE, [4,1])
        board[4][2] = Knight(WHITE, [4,2])
        board[4][3] = King(WHITE, [4,3])
        board[3][3] = Pawn(WHITE, [3,3])

        self.board = board
        # White always goes first
        self.turn = WHITE
        # Add pieces to stored list
        self.black_pieces = []
        self.white_pieces = []
        self.king_pos = [None, None]
        
        for i in range(BOARD_LENGTH):
            for j in range(BOARD_WIDTH):
                curr = self.board[i][j]
                if curr is not None: 
                    if curr.get_color() == BLACK:
                        self.black_pieces.append(curr)
                    else:
                        self.white_pieces.append(curr)
                    if curr.get_piece_type() == KING:
                        self.king_pos[curr.get_color()] = [i,j]

        self.parent_pos = MicroChess.Position(self.board, self.turn, self.black_pieces, self.white_pieces, self.king_pos)

    def initial_pos(self):
        '''
        Returns a Position object representing the initial position at the beginning
        of a game of Mallett Chess
        '''
        # We need to make a copy of our variables to pass into pos
        return self.parent_pos.create_copy()

    class Position:
        def __init__(self, board, turn, black_pieces, white_pieces, king_pos):
            '''
            Initializes a position given all the attributes

            All parameters are passed in after initialized MicroChess object
            '''
            self._board = board
            self._turn = turn
            self._black_pieces = black_pieces
            self._white_pieces = white_pieces
            self._king_pos = king_pos

        def create_copy(self) -> 'Position':
            '''
            Creates and returns a deep copy of itself
            '''
            board_copy = [[None] * BOARD_WIDTH for _ in range(BOARD_LENGTH)]
            black_pieces_copy, white_pieces_copy = [], []
            for row in range(BOARD_LENGTH):
                for col in range(BOARD_WIDTH):
                    curr = self._board[row][col]
                    if curr is None:
                        board_copy[row][col] = None
                        continue
                    
                    if curr.get_piece_type() == KING:
                        board_copy[row][col] = King(curr.get_color(), curr.get_pos())
                    elif curr.get_piece_type() == QUEEN:
                        board_copy[row][col] = Queen(curr.get_color(), curr.get_pos())
                    elif curr.get_piece_type() == ROOK:
                        board_copy[row][col] = Rook(curr.get_color(), curr.get_pos())
                    elif curr.get_piece_type() == BISHOP:
                        board_copy[row][col] = Bishop(curr.get_color(), curr.get_pos())
                    elif curr.get_piece_type() == KNIGHT:
                        board_copy[row][col] = Knight(curr.get_color(), curr.get_pos())
                    elif curr.get_piece_type() == PAWN:
                        board_copy[row][col] = Pawn(curr.get_color(), curr.get_pos())

                    if curr.get_color() == BLACK:
                        black_pieces_copy.append(board_copy[row][col])
                    else:
                        white_pieces_copy.append(board_copy[row][col])

            return MicroChess.Position(board_copy, self._turn, black_pieces_copy, white_pieces_copy, list(self._king_pos))

        def print_board(self) -> None:
            print("Current Board:")
            for row in range(BOARD_LENGTH):
                for col in range(BOARD_WIDTH):
                    s = "()" if self._board[row][col] is None else str(self._board[row][col])
                    print(f" {s} ", end = "")
                print()

        def get_board(self) -> 'Mat(Piece)':
            return self._board

        def get_turn(self) -> int:
            return self._turn
        
        def get_black_pieces(self) -> 'List':
            return self._black_pieces

        def get_white_pieces(self) -> 'List':
            return self._white_pieces

        def player_legal_moves(self) -> 'List':
            '''
            Returns a list of the legal moves that the player can make
            The list is 2 elements: the old position and new position
            '''
            pieces = self._black_pieces if self._turn == BLACK else self._white_pieces

            ret = []
            for piece in pieces:
                dests = piece.get_legal_moves(self._board)
                for dest in dests:
                    move = [piece.get_pos(), dest]
                    if not self.would_be_check(move):
                        ret.append(move)
            return ret

        def print_player_legal_moves(self, moves) -> None:
            p = list(map(lambda m: [str(self._board[m[0][0]][m[0][1]]), m[1]], moves))
            print(p)

        def is_check(self) -> bool:
            '''
            Returns if the color player is under check
            Finds the position of the king and then checks to see if any of the opponent's pieces can move there
            '''
            color = self._turn
            if color != WHITE and color != BLACK:
                raise ValueError("is_check: invalid color")
            king_pos = self._king_pos[color]

            op_pieces = self._black_pieces if color == WHITE else self._white_pieces
            for piece in op_pieces:
                if piece.cant_check(king_pos):
                    continue
                if king_pos in piece.get_legal_moves(self._board):
                    return True
            return False

        def would_be_check(self, move) -> bool:
            '''
            Returns if making move would lead to check for the moving player
            This is used to check that a move is legal
            
            Algorithm:
            We save the record of the old configurations of the two changed squares
            We conduct the change
            Check if there is a check
            Then revert the change
            ''' 
            old_x, old_y = move[0][0], move[0][1]
            new_x, new_y = move[1][0], move[1][1]
            moving_player = self._board[old_x][old_y].get_color()
            save_old = self._board[old_x][old_y]
            save_new = self._board[new_x][new_y]

            if save_old.get_piece_type() == KING:
                self._king_pos[moving_player] = [new_x, new_y]
            save_old.move_to([new_x, new_y])
            self._board[new_x][new_y] = self._board[old_x][old_y]
            self._board[old_x][old_y] = None
            ret = self.is_check()

            self._board[old_x][old_y] = save_old
            if save_old.get_piece_type() == KING:
                self._king_pos[moving_player] = [old_x, old_y]
            self._board[old_x][old_y].move_to([old_x, old_y])
            self._board[new_x][new_y] = save_new

            return ret

        def is_checkmate(self) -> bool:
            '''
            Checks to see if there is a checkmate ie. the current player can't make a move
            that is not a check position
            '''
            possible_moves = self.player_legal_moves()
            if len(possible_moves) == 0:
                return True
            for move in possible_moves:
                if not self.would_be_check(move):
                    return False
            return True

        def winner(self) -> int:
            '''
            Returns if the game is over
            If it is, it either returns BLACK, WHITE, or DRAW
            Otherwise, -1
            '''
            if self.is_checkmate():
                return BLACK if self._turn == WHITE else WHITE
            # Check for draw positions
            # Two pieces must be kings
            if len(self._black_pieces) == 1 and len(self._white_pieces) == 1:
                return DRAW
            return -1

        def result(self, move) -> 'Position':
            '''
            Conducts the move but edits our Position object without creating an entirely new object
            Also returns the Position object
            '''
            old_x, old_y = move[0][0], move[0][1]
            new_x, new_y = move[1][0], move[1][1]
            move_color = self._board[old_x][old_y].get_color()

            if self._board[old_x][old_y] is None:
                raise ValueError("result: invalid move --- no piece in origin pos")
            if self._turn != move_color:
                raise ValueError("result: invalid move --- trying to move piece of opposite color")
            '''
            if move not in self.player_legal_moves():
                raise ValueError("result: invalid move --- you can't move there")
            '''

            # Remove captured players from game
            captured = self._board[new_x][new_y]
            if captured is not None:
                if move_color == BLACK:
                    self._white_pieces.remove(captured)
                else:
                    self._black_pieces.remove(captured)
            # Conduct the move
            self._board[old_x][old_y].move_to([new_x, new_y])
            if self._board[old_x][old_y].get_piece_type() == KING:
                self._king_pos[self._board[old_x][old_y].get_color()] = [new_x, new_y]
            self._board[new_x][new_y] = self._board[old_x][old_y]
            self._board[old_x][old_y] = None

            self._turn = 1 - self._turn

            for i in range(BOARD_LENGTH):
                for j in range(BOARD_WIDTH):
                    curr = self._board[i][j]
                    if curr is not None and [i, j] != curr.get_pos():
                        raise ValueError("Pos do not match")
                    if curr is not None and curr.get_piece_type() == KING and [i, j] != self._king_pos[curr.get_color()]:
                        print(f"i,j: {[i, j]}, king_pos: {self._king_pos[curr.get_color()]}")
                        raise ValueError("King_pos doesn't match")
            return self

        def result_copy(self, move) -> 'Position':
            '''
            Returns a Position object representing the outcome of conducting move

            Given a move, it moves the piece to that position. 
            It removes the captured piece (if applicable)
            '''
            old_x, old_y = move[0][0], move[0][1]
            new_x, new_y = move[1][0], move[1][1]
            move_color = self._board[old_x][old_y].get_color()
            
            if self._board[old_x][old_y] is None:
                raise ValueError("result: invalid move --- no piece in origin pos")
            if self._turn != move_color:
                raise ValueError("result: invalid move --- trying to move piece of opposite color")
            '''
            if move not in self.player_legal_moves():
                raise ValueError("result: invalid move --- you can't move there")
            '''

            new_pos = self.create_copy()
            # Remove captured players from game
            captured = new_pos._board[new_x][new_y]
            if captured is not None:
                if move_color == BLACK:
                    new_pos._white_pieces.remove(captured)
                else:
                    new_pos._black_pieces.remove(captured)
            # Conduct the move
            new_pos._board[old_x][old_y].move_to([new_x, new_y])
            new_pos._board[new_x][new_y] = new_pos._board[old_x][old_y]
            new_pos._board[old_x][old_y] = None

            new_pos._turn = 1 - new_pos._turn
            return new_pos