from django.db import models
from rest_framework import serializers
import uuid
from django.forms import ModelForm
import random
RESPOND_STATUS = {
    'ok': 200,
    'game_not_found': 404,
    'bad_request': 400,
    'internal_server_error': 500
}
Computer = 1
Open_token = 0
Player = -1
class GameManager(models.Manager):

    def create_game(self, board):
        '''Create a new game, if it is an empty board, set computer first'''
        if len(board) != 9:
            return RESPOND_STATUS['bad_request'], None
        if len(board.replace('-', '')) == 0:
            game = self.create(token=self.generate_token(), board=board, status='RUNNING',first='C',player='X')
            game.move(list(board))
            return RESPOND_STATUS['ok'], game
        if len(board.replace('-', '')) == 1:
            game = self.create(token=self.generate_token(), board=board, status='RUNNING',first='P',player=board.replace('-', ''))
            return RESPOND_STATUS['ok'], game
        return RESPOND_STATUS['bad_request'], None


    def get_games(self):
        '''Get all games in database'''
        try:
            games = GamesModel.objects.all()
            return RESPOND_STATUS['ok'], games
        except:
            return RESPOND_STATUS['internal_server_error'], None

    def delete_game(self, token):
        '''Delete the game by game token'''
        try:
            obj = GamesModel.objects.filter(token=token)
            if obj.count() != 0:
                obj.delete()
                return RESPOND_STATUS['ok']
            return RESPOND_STATUS['game_not_found']
        except:
            return RESPOND_STATUS['internal_server_error']

    def find_game(self, token):
        '''Find the game by game token'''
        try:
            obj = GamesModel.objects.filter(token=token)
            if obj.count() != 0:
                return RESPOND_STATUS['ok'], obj[0], 
            return RESPOND_STATUS['game_not_found'], None 
        except:
            return RESPOND_STATUS['internal_server_error'], None
    
    def generate_token(self):
        return str(uuid.uuid4())[0:8]

    def validate_move(self, token, board, status):
        '''Validate the player's move, if True return game object'''
        try:
            if len(board) != 9:
                return RESPOND_STATUS['bad_request'], None
            obj = GamesModel.objects.filter(token=token)
            if obj.count() == 0:
                return RESPOND_STATUS['game_not_found'], None
            elif status != obj[0].status:
                return RESPOND_STATUS['bad_request'], None
            else:
                if obj[0].board == board:
                    return RESPOND_STATUS['bad_request'], None
                oldBoard = obj[0].board
                newBoard = board
                if obj[0].first == 'C' and len(newBoard.replace('-','').replace('O','')) != len(newBoard.replace('-','').replace('X','')):
                    return RESPOND_STATUS['bad_request'], None
                computer_steps = len(newBoard.replace('-','').replace(obj[0].player,''))
                player_steps = 9 - len(newBoard.replace('X','').replace('O','')) - computer_steps
                if obj[0].first == 'P' and player_steps - computer_steps != 1:
                    return RESPOND_STATUS['bad_request'], None
                for i in range(0,9):
                    if list(newBoard)[i] != list(oldBoard)[i] and list(oldBoard)[i] != '-':
                        return RESPOND_STATUS['bad_request'], None
                obj[0].update_board( board)

                return RESPOND_STATUS['ok'], obj[0]
        except:
            return RESPOND_STATUS['internal_server_error'], None
    

class GamesModel(models.Model):

    objects = GameManager()

    WINNING_TRIADS = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
        (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
    
    SLOTS = (0, 1, 2, 3, 4, 5, 6, 7, 8)

    GAME_STATUS_CHOICES = (
        ('RUNNING','Game is running'),
        ('X_WON','X won the game'),
        ('O_WON','O won the game'),
        ('DRAW','Nobody won the game'),
    )

    first = models.CharField(max_length=4, null=True)
    player = models.CharField(max_length=4, null=True)
    board = models.CharField(max_length=30, null=True)
    token = models.CharField(max_length=32, null=True)
    status = models.CharField(choices=GAME_STATUS_CHOICES, null=True, max_length=32)


    def update_board(self, board):
        self.board = board
        self.save()

    def board_valuation(self, board, player, next_player, alpha, beta):
        '''Dynamic and static evaluation of board position.'''
        # Static evaluation - value for next_player
        wnnr = self.winner(board)
        if wnnr != Open_token:
            # Not a draw or a move left: someone won
            return wnnr
        elif not self.legal_move_left(board):
            # Draw - no moves left
            return 0 # Cat
        # If flow-of-control gets here, no winner yet, not a draw.
        # Check all legal moves for "player"
        for move in self.SLOTS:
            if board[move] == Open_token:
                board[move] = player
                val = self.board_valuation(board, next_player, player, alpha, beta)
                board[move] = Open_token
                if player == next_player:  # Maximizing player
                    if val > alpha:
                        alpha = val
                    if alpha >= beta:
                        return beta
                else:  # X_token player, minimizing
                    if val < beta:
                        beta = val
                    if beta <= alpha:
                        return alpha
        if player == Computer:
            retval = alpha
        else:
            retval = beta
        return retval

    def determine_move(self, board):
        ''' Determine Os next move. Check that a legal move remains before calling.
            Randomly picks a single move from any group of moves with the same value.
        '''
        best_val = -2  # 1 less than min of O_token, X_token
        my_moves = []
        for move in self.SLOTS:
            if board[move] == Open_token:
                board[move] = Computer
                val = self.board_valuation(board, Player, Computer, -2, 2)
                print(val)
                board[move] = Open_token
                if val > best_val:
                    best_val = val
                    my_moves = [move]
                if val == best_val:
                    my_moves.append(move)
        return random.choice(my_moves)

    def winner(self, board):
        ''' Return the winner of the game, if returned '-' means no winner yet
        '''
        for triad in self.WINNING_TRIADS:
            if board[triad[0]] == board[triad[1]] and board[triad[1]] == board[triad[2]]:
                return board[triad[0]]
        return 0

    def legal_move_left(self, board):
        ''' Returns True if a legal move remains, False if not. '''
        for slot in self.SLOTS:
            if board[slot] == 0:
                return True
        return False

    def get_game(self):
        data = {
            'board': self.board,
            'token': self.token,
            'status': self.status,
        }
        return data
        

    def move(self, board):
        for i in range(0,9):
            if board[i] == '-':
                board[i] = 0
                continue
            if board[i] == self.player[0]:
                board[i] = -1
                continue
            else:
                board[i] = 1
                continue        

        result = self.winner(board)
        if result == 1:
            
            return RESPOND_STATUS['ok'] ,self
            
        if result == -1:
            print('You won')
            return RESPOND_STATUS['ok'] ,self
            
        if result == 0:
            if self.legal_move_left(board):
                mymv = self.determine_move(board)
                newBoard = list(self.board)
                newBoard[mymv] = 'XO'.replace(self.player, '')
                self.update_board("".join(newBoard))
                '''Recheck the board'''
                result = self.winner(board)
                if result == 0 and not self.legal_move_left(board):
                    self.static = 'DRAW'
                    self.save()
                if result == 1:
                    print('Computer won')
                    pass
                if result == -1:
                    print('You won')
                    pass    
        

        return RESPOND_STATUS['ok'] ,self

        # base on the existing board, judge win(update status)
        # base on existing board, computer move
        # base on existing board, judge win(update status)
        pass