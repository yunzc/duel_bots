#!/usr/bin/python

# duel bots: programmed controllers 
# author: Yun Chang 
# date: 12/31/2017
# yunchang@mit.edu 

import numpy as np 

# enemy_loc is given as [x, y]
def player1(x, y, enemy_loc, obstacle_info, goalx, goaly):
	# return [dx, dy, fire, gun_aimx, gun_aimy]
	if np.random.sample() > 0.5: 
		[dx, dy] = [goalx-x, goaly-y]
	else:
		[dx, dy] = [np.random.sample(), np.random.sample()]
	[gun_aimx, gun_aimy] = [0,0]
	fire = False
	if enemy_loc != None:
		[gun_aimx, gun_aimy] = enemy_loc
		fire = True 
	return [dx, dy, fire, gun_aimx, gun_aimy]

def player2(x, y, enemy_loc, obstacle_info, goalx, goaly):
	return [0, 0, False, 100, 100]