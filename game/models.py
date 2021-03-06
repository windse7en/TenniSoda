from django.db import models
from account.models import Profile
from city.models import City
from court.models import Court
from datetime import datetime

# Create your models here.
class League(models.Model):
    name = models.CharField(max_length = 200)
    city = models.ForeignKey(City)
    start_date = models.DateField()
    end_date = models.DateField()
    current_player_number = models.IntegerField(default = 0)
    max_player_number = models.IntegerField()
    players = models.ManyToManyField(Profile, blank = True, null = True)
    level_low = models.FloatField()
    level_high = models.FloatField()

    def __unicode__(self):
        return self.name

class Game(models.Model):
    league = models.ForeignKey(League, blank = True, null = True)
    court = models.ForeignKey(Court, blank = True, null = True)
    player1 = models.ForeignKey(Profile, related_name = 'player1')
    player2 = models.ForeignKey(Profile, related_name = 'player2')
    winner = models.ForeignKey(Profile, related_name = 'winnner', blank = True, null = True)
    date = models.DateField(blank = True, null = True)
    is_played = models.BooleanField(default = False)
    player1_confirmed = models.BooleanField(default=False)
    player2_confirmed = models.BooleanField(default=False)

    def __unicode__(self):
        name = u"%s " % self.league+u"%s " % self.player1+u"%s " % self.player2
        return name

class Score(models.Model):
    game = models.OneToOneField(Game, primary_key = True)
    score11 = models.IntegerField(blank = True, null = True)
    score12 = models.IntegerField(blank = True, null = True)
    score21 = models.IntegerField(blank = True, null = True)
    score22 = models.IntegerField(blank = True, null = True)
    score31 = models.IntegerField(blank = True, null = True)
    score32 = models.IntegerField(blank = True, null = True)
    score41 = models.IntegerField(blank = True, null = True)
    score42 = models.IntegerField(blank = True, null = True)
    score51 = models.IntegerField(blank = True, null = True)
    score52 = models.IntegerField(blank = True, null = True)


    def __unicode__(self):
        return u"%s " % self.game

Game.score = property(lambda g: Score.objects.get_or_create(game=g)[0])

class GroupStage(models.Model):
    league = models.ForeignKey(League)
    group_number = models.IntegerField()
    member_number = models.IntegerField()
    player = models.ForeignKey(Profile)
    points = models.IntegerField(blank = True, null = True)

    class Meta:
        unique_together = ('league','group_number','member_number',)

    def __unicode__(self):
        return u"%s %s %s %s" % (self.league, self.group_number, self.member_number, self.player)

class FreeLeagueGame(models.Model):
    player = models.ForeignKey(Profile,primary_key = True)
    request_time = models.DateTimeField(default = datetime.now())

    def __unicode__(self):
        return u'%s' % self.player
