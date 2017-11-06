from django.db import models
from rest_framework import serializers
import uuid
from django.forms import ModelForm

RESPOND_STATUS = {
    'ok': 200,
    'game_not_found': 404,
    'bad_request': 400,
    'internal_server_error': 500
}

# Create your models here.
class GameManager(models.Manager):

    def create_game(self, board):
        if len(board) != 9:
            return RESPOND_STATUS['bad_request'], None
        if len(board.replace('-', '')) == 0:
            game = self.create(token=self.generate_token(), board=board, status='RUNNING',first='C',player='X')
            game.move(board)
            return RESPOND_STATUS['ok'], game
        if len(board.replace('-', '')) == 1:
            game = self.create(token=self.generate_token(), board=board, status='RUNNING',first='P',player=board.replace('-', ''))
            return RESPOND_STATUS['ok'], game
        return RESPOND_STATUS['bad_request'], None


    def get_games(self):
        try:
            games = GamesModel.objects.all()
            return RESPOND_STATUS['ok'], games
        except:
            return RESPOND_STATUS['internal_server_error'], None

    def delete_game(self, token):
        try:
            obj = GamesModel.objects.filter(token=token)
            if obj.count() != 0:
                obj.delete()
                return RESPOND_STATUS['ok']
            return RESPOND_STATUS['game_not_found']
        except:
            return RESPOND_STATUS['internal_server_error']

    def find_game(self, token):
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
        try:
            if len(board) != 9:
                return RESPOND_STATUS['bad_request'], None
            obj = GamesModel.objects.filter(token=token)
            print(token, board, status)
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
                print(player_steps, computer_steps)
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

    GAME_STATUS_CHOICES = (
        ('RUNNING','Game is running'),
        ('X_WON','X won the game'),
        ('O_WON','O won the game'),
        ('DRAW','Nobody won the game'),
    )

    first = models.CharField(max_length=4)
    player = models.CharField(max_length=4)
    board = models.CharField(max_length=30)
    token = models.CharField(max_length=32)
    status = models.CharField(choices=GAME_STATUS_CHOICES, null=True, max_length=32)

    def update_board(self, board):
        self.board = board
        self.save()

    def get_game(self):
        data = {
            'board': self.board,
            'token': self.token,
            'status': self.status,
        }
        return data

    def move(self, board):
        # do some magic here to implement AI
        # base on the existing board, judge win(update status)
        # base on existing board, computer move
        # base on existing board, judge win(update status)
        pass