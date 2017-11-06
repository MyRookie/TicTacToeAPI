from django.conf.urls import url
from ssh_homework.tictactoe import views


urlpatterns = [
    url(r'^games/(?P<id>[a-zA-Z0-9]{8,128})$', views.games, name='game'),
    url(r'^games/', views.game, name='games'),
]