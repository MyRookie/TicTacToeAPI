
from django.contrib import admin

from ssh_homework.tictactoe.models import GamesModel



class GamesModelAdmin(admin.ModelAdmin):
    pass
admin.site.register(GamesModel, GamesModelAdmin)