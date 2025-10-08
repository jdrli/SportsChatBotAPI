from django.contrib import admin
from .models import PlayerStat

@admin.register(PlayerStat)
class PlayerStatAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'team_name', 'points', 'rebounds', 'assists')

