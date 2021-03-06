from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from models import League, Game, Score, FreeLeagueGame
from forms import ScoreCreationForm, GameEditForm
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import auth, messages
from datetime import datetime
from notification.models import Notification

@login_required
def join_league(request, league_match_id=1):
	user = request.user.profile
	if user.first_name is None or user.first_name == ''\
		or user.last_name is None or user.last_name == ''\
		or user.phone is None or user.phone == ''\
		or user.level is None or user.level == '':
		return render_to_response('profile_notify.html')
	league_match = League.objects.get(id=league_match_id)
	if League.objects.filter(id=league_match_id,players=user).count()==0:
		league_match.players.add(user)
		league_match.current_player_number += 1
		league_match.save()
	return HttpResponseRedirect('/account/welcome_user')

@login_required
def join_league_cancel(request, league_match_attended_id=1):
	user = request.user.profile
	league_match_attended = League.objects.get(id=league_match_attended_id)
	if League.objects.filter(id=league_match_attended_id,players=user).count()!=0:
		league_match_attended.current_player_number -= 1
		league_match_attended.save()
		league_match_attended.players.remove(user)
	return HttpResponseRedirect('/account/welcome_user')

@login_required
def list_all_games(request):
	user = request.user.profile
	games_as_player1 = Game.objects.filter(player1 = user)
	games_as_player2 = Game.objects.filter(player2 = user)
	games_played_as_player1 = []
	games_played_as_player2 = []
	for game in games_as_player1:
		if game.is_played:
			games_played_as_player1.append(game)
			games_as_player1 = games_as_player1.exclude(id=game.id)
			print game.id
	for game in games_as_player2:
		if game.is_played:
			games_played_as_player2.append(game)
			games_as_player2 = games_as_player2.exclude(id=game.id)
	print games_as_player1
	print games_as_player2
	print games_played_as_player1
	print games_played_as_player2
	return render_to_response('list_all_games.html',
		{'games_as_player1':games_as_player1,
		 'games_as_player2':games_as_player2,
		 'games_played_as_player1':games_played_as_player1,
		 'games_played_as_player2':games_played_as_player2},)

@login_required
def upload_score(request, game_id=1):
	user = request.user.profile
	game = Game.objects.get(id = game_id)
	if game.player1 != user and game.player2 != user:
		auth.logout(request)
		return HttpResponseRedirect('/account/login')

	score = game.score

	if request.method == 'POST':
		game.is_played = True
		game.player1_confirmed = False
		game.player2_confirmed = False
		game.save()
		score_form = ScoreCreationForm(request.POST,instance=score)
		game_form = GameEditForm(request.POST, instance=game)
		if score_form.is_valid() and game_form.is_valid():
			score_form.save()
			game_form.save()
			confirm_score(request,game_id=game.id)
			if game.player1 == user:
				Notification.objects.create(user = game.player2.user,
											title = 'A game needs to be confirmed',
											message = 'Your game vs %s %s needs your confirmation, go to game page to confirm.' % (game.player1.last_name, game.player1.first_name),
											time = datetime.now())
			else:
				Notification.objects.create(user = game.player1.user,
											title = 'A game needs to be confirmed',
											message = 'Your game vs %s %s needs your confirmation, go to game page to confirm.' % (game.player2.last_name, game.player2.first_name),
											time = datetime.now())

			return HttpResponseRedirect('/game/list_all_games')
	else:
		score_form = ScoreCreationForm(instance=score)
		game_form = GameEditForm(instance=game)

	args = {}
	args.update(csrf(request))

	args['score_form'] = score_form
	args['game_form'] = game_form
	args['player1'] = game.player1
	args['player2'] = game.player2
	args['game_id'] = game.id
	return render_to_response('upload_score.html', args)



@login_required
def confirm_score(request,game_id = 1):
	user = request.user.profile
	game = Game.objects.get(id = game_id)
	if game.player1 != user and game.player2 != user:
		auth.logout(request)
		return HttpResponseRedirect('/account/login')
	if game.player1 == user:
		game.player1_confirmed = True
		if game.player2_confirmed:
			game.winner = get_winner(game)
			Notification.objects.create(user = game.player1.user,
										title = 'A game is completed',
										message = 'Your game against %s %s is completed' % (game.player2.last_name, game.player2.first_name),
										time = datetime.now())
			Notification.objects.create(user = game.player2.user,
										title = 'A game is completed',
										message = 'Your game against %s %s is completed' % (game.player1.last_name, game.player1.first_name),
										time = datetime.now())
		game.save()

		return HttpResponseRedirect('/game/list_all_games')
	else:
		game.player2_confirmed = True
		if game.player1_confirmed:
			game.winner = get_winner(game)
			Notification.objects.create(user = game.player1.user,
										title = 'A game is completed',
										message = 'Your game against %s %s is completed' % (game.player2.last_name, game.player2.first_name),
										time = datetime.now())
			Notification.objects.create(user = game.player2.user,
										title = 'A game is completed',
										message = 'Your game against %s %s is completed' % (game.player1.last_name, game.player1.first_name),
										time = datetime.now())
		game.save()
		return HttpResponseRedirect('/game/list_all_games')

@login_required
def find_game(request):
	user = request.user.profile
	if user.first_name is None or user.first_name == ''\
		or user.last_name is None or user.last_name == ''\
		or user.phone is None or user.phone == ''\
		or user.level is None or user.level == '':
		return render_to_response('profile_notify.html')
	free_game = FreeLeagueGame.objects.get_or_create(player = user)[0]
	free_game.request_time = datetime.now()
	free_game.save()
	messages.success(request,'join success')
	username = user.last_name+user.first_name
	league_match_attended = League.objects.filter(players=request.user.profile)
	return render(request, 'welcome_user.html',
		{'username':username,'league_matches_attended':league_match_attended,'league_matches_remained': League.objects.exclude(players=request.user),})


@login_required
def quit_game(request,game_id = 1):
	user = request.user.profile
	game = Game.objects.get(id = game_id)
	if game.player1 != user and game.player2 != user:
		auth.logout(request)
		return HttpResponseRedirect('/account/login')
	if game.player1 == user:
		Notification.objects.create(user = game.player2.user,
									title = 'One of your opponent has quit a game',
									message = 'Your opponent %s %s quit the game' % (game.player1.last_name, game.player1.first_name),
									time = datetime.now(),)
	else:
		Notification.objects.create(user = game.player1.user,
									title = 'One of your opponent has quit a game',
									message = 'Your opponent %s %s quit the game' % (game.player2.last_name, game.player2.first_name),
									time = datetime.now(),)

	game.delete()
	return HttpResponseRedirect('/game/list_all_games')



def get_winner(game):
	score = Score.objects.get(game = game)
	player1_set_point = 0
	player2_set_point = 0
	if score.score11>score.score12:
		player1_set_point += 1
	elif score.score11<score.score12:
		player2_set_point += 1

	if score.score21>score.score22:
		player1_set_point += 1
	elif score.score11<score.score12:
		player2_set_point += 1

	if score.score31>score.score32:
		player1_set_point += 1
	elif score.score11<score.score12:
		player2_set_point += 1

	if score.score41>score.score42:
		player1_set_point += 1
	elif score.score11<score.score12:
		player2_set_point += 1

	if score.score51>score.score52:
		player1_set_point += 1
	elif score.score11<score.score12:
		player2_set_point += 1

	if player1_set_point>player2_set_point:
		return game.player1
	else:
		return game.player2

