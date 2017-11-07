from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from ssh_homework.tictactoe.models import GamesModel, RESPOND_STATUS
from django.http import QueryDict
import json

def player_move(board, status, token):
    respond, game = GamesModel.objects.validate_move(token, board, status)
    if respond != RESPOND_STATUS['ok']:
        return respond, None
    respond, game = game.move( list(board))
    return respond, game

@api_view(['PUT', 'GET', 'DELETE'])
@permission_classes((permissions.AllowAny,))
def games(request, *args, **kwargs):
    if 'id' in kwargs: 
        token = kwargs['id']
        if request.method == 'GET':
            respond, game = GamesModel.objects.find_game(token)
            if respond == RESPOND_STATUS['ok']:
                data = game.get_game()
                return Response({
                    'game': data
                    }, status=status.HTTP_200_OK)
            elif respond == RESPOND_STATUS['game_not_found']:
                return Response({
                    'message': 'Game is not found'
                }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'message': 'Internal server error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if request.method == 'PUT':
            # post data error
            if 'game' not in request.data or 'board' not in request.data['game'] or 'status' not in request.data['game']:
                return Response({'message':'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
            board = request.data['game']['board']
            gameStatus = request.data['game']['status']
            respond, game = player_move(board, gameStatus, token)
            if respond == RESPOND_STATUS['ok']:
                data = game.get_game()
                return Response({
                    'game': data
                    }, status=status.HTTP_200_OK)
            elif respond == RESPOND_STATUS['game_not_found']:
                return Response({
                    'message': 'Game is not found'
                }, status=status.HTTP_404_NOT_FOUND)
            elif respond == RESPOND_STATUS['bad_request']:
                return Response({
                'message':'Bad request'
            }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'message': 'Internal server error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'message':'Set one move'}, status=status.HTTP_200_OK)
        
        if request.method == 'DELETE':
            respond = GamesModel.objects.delete_game(token)
            if respond == RESPOND_STATUS['ok']:
                return Response({
                    'message': 'Game has been deleted'
                    }, status=status.HTTP_200_OK)
            elif respond == RESPOND_STATUS['game_not_found']:
                return Response({
                    'message': 'Game is not found'
                }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'message': 'Internal server error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({'message':'Bad request'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST','GET'])
@permission_classes((permissions.AllowAny,))
def game(request, *args, **kwargs):
    if request.method == 'POST':
        if 'game' not in request.data or 'board' not in request.data['game']:
            return Response({'message':'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
        respond, game = GamesModel.objects.create_game(request.data['game']['board'])
        if respond == RESPOND_STATUS['ok']:
            data = game.get_game()
            return Response({
                'game': data
                }, status=status.HTTP_200_OK)
        elif respond == RESPOND_STATUS['bad_request']:
            return Response({
            'message':'Bad request'
        }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    if request.method == 'GET':
        respond, games = GamesModel.objects.get_games()
        if respond == RESPOND_STATUS['ok']:
            data = []
            for game in games:
                data.append(game.get_game())
            return Response({
                'games': data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
