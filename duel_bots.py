#!/usr/bin/python

# duel bots: an arena for a programming faceoff 
# author: Yun Chang 
# date: 12/31/2017
# yunchang@mit.edu 

import Tkinter, time, random, sys
from PIL import Image, ImageTk
import numpy as np 
import player_controls

#### Parameters 
ship_size = 200
bullet_size = 3
bullet_speed = 8
ship_speed = 3

class Ship(object):
	# ship object stores information of spaceship 
	def __init__(self, x, y, controller, goal):
		# initialize with state 
		self.x = x
		self.y = y 
		self.health = 100 # start with 100 health 
		# location of ship always referenced by top right corner 
		self.shooting = False
		self.gun_aim = goal # the coordinate gun is aiming at 
		# gun range is infinite 
		self.controller = controller
		self.goalx = goal[0]
		self.goaly = goal[1]

	def arena_location(self):
		return [self.x + ship_size/2, self.y + ship_size/2]

	def start_firing(self):
		self.shooting = True 

	def stop_firing(self): 
		self.shooting = False

	def damage(self, n):
		if n > 0:
			self.health -= n

	def update(self, enemy_loc, obstacle_info, maxx, maxy):
		if self.controller == None: 
			return True 
		[dx, dy, fire, gun_aimx, gun_aimy] = self.controller(self.x, \
			self.y, enemy_loc, obstacle_info, self.goalx, self.goaly)
		theta = np.arctan2(dy, dx)
		d_x = ship_speed*np.cos(theta)
		d_y = ship_speed*np.sin(theta)
		self.gun_aim = [gun_aimx, gun_aimy]
		if fire: 
			self.start_firing()
		else:
			self.stop_firing()
		if self.x + d_x >= 0 and self.x + d_x <= maxx and \
			self.y + d_y >= 0 and self.y + d_y <= maxy: 
			self.x += d_x
			self.y += d_y 
		return True 

class Arena(Tkinter.Canvas):
	def __init__(self, *args, **kwargs):
		# init superclass (tkinter canvas)
		Tkinter.Canvas.__init__(self, *args, **kwargs)

		# initialize background 
		h = self.winfo_screenheight() - 100
		w = self.winfo_screenwidth() - 100
		img = Image.open('sky.jpg')
		img = img.resize([w,h])
		img = ImageTk.PhotoImage(img)
		self.background_img = img
		self.create_image(w/2,h/2,image=img)
		self.XDIM = w
		self.YDIM = h 

		# initialize camp
		goal1 = [w-ship_size, h-ship_size] # goal location for player 1
		goal2 = [0,0] # goal location for player 2
		self.camp1x = ship_size*3
		self.camp1y = ship_size*3
		self.camp2x = w-3*ship_size
		self.camp2y = h-3*ship_size

		# initialize players 
		# say None for controller if using manuel 
		self.player1 = Ship(0,0,player_controls.player1, goal1) # at top corner 
		self.player2 = Ship(w-ship_size, h-ship_size, None, goal2) # at bottom right 
		self.manuel = 2
		# if nothing using manuel, self.manuel = 0

		# # for testing 
		# self.player1.gun_aim= [w-ship_size, h-ship_size]
		# self.player1.start_firing()

		p1_img = Image.open('spaceship.png')
		p1_img = p1_img.resize([ship_size, ship_size])
		p1_img = ImageTk.PhotoImage(p1_img)
		self.p1_img = p1_img
		[p1x, p1y] = self.player1.arena_location()
		self.p1 = self.create_image(p1x,p1y,image=p1_img)

		p2_img = Image.open('spaceship1.png')
		p2_img = p2_img.resize([ship_size,ship_size])
		p2_img = ImageTk.PhotoImage(p2_img)
		self.p2_img = p2_img
		[p2x, p2y] = self.player2.arena_location()
		self.p2 = self.create_image(p2x,p2y,image=p2_img)

		# bullets as dictionary {rectangle_obj: direction}
		self.bullets = {}

		# health display 
		self.health1 = self.create_text(100,100,text=str(self.player1.health),\
			font=('arial 20 bold'), fill='white')
		self.health2 = self.create_text(w-ship_size, h-ship_size,text=str(self.player2.health),\
			font=('arial 20 bold'), fill='white')

		# obstacles 
		self.obstacles = None 

		# for manuel control 
		for seq in ['<Key-Right>','<Key-Left>','<Key-Up>','<Key-Down>'\
			'w', 'a', 's', 'd', 'x']:
			self.master.bind(seq, self.manuel_control)
		return

	def check_bullet_hit(self):
		h = self.winfo_height()
		w = self.winfo_width()
		# check hit for player 1
		a,b,c,d = self.bbox(self.p1)
		k = len(self.find_overlapping(a,b,c,d)) -3 
		self.player1.damage(k)
		# check hit for player 1
		a,b,c,d = self.bbox(self.p2)
		l = len(self.find_overlapping(a,b,c,d)) - 3
		self.player2.damage(l)
		return True

	def fire_bullets(self, player):
		if player == 1:
			pl = self.player1
		if player == 2:
			pl = self.player2

		x1, y1 = pl.arena_location()
		[xt, yt] = pl.gun_aim
		theta = np.arctan2(yt-y1, xt-x1)
		x1 += ship_size*np.cos(theta)
		y1 += ship_size*np.sin(theta)
		x2 = x1 + bullet_size*np.cos(theta)
		y2 = y1 + bullet_size*np.sin(theta)
		bullet = self.create_line(x1,y1,x2,y2, fill='red', width=2)
		self.bullets[bullet] = theta
		return True
	
	def update_bullets(self):
		for bullet in self.bullets:
			try:
				a,b,c,d = self.bbox(bullet)
				x1,y1,x2,y2=self.coords(bullet)
				overlap = self.find_overlapping(a,b,c,d)
				if self.p1 in overlap or self.p2 in overlap:
					self.delete(bullet)
				elif x2< 0 or y2 < 0:
					self.delete(bullet)
				elif x1 > self.XDIM or y1 > self.YDIM:
					self.delete(bullet)
				else:
					theta = self.bullets[bullet]
					dx = bullet_speed*np.cos(theta)
					dy = bullet_speed*np.sin(theta)
					self.coords(bullet,(x1+dx, y1+dy, x2+dx, y2+dy))
			except:
				pass
		return True

	def update_players(self):
		# for player1
		# if player 2 is shooting, player 1 knows location 
		player2_loc = None
		if self.player2.shooting: 
			player2_loc = [self.player2.x, self.player2.y] 
		self.player1.update(player2_loc, self.obstacles, \
			self.XDIM-ship_size, self.YDIM-ship_size)
		# for player 2 
		player1_loc = None
		if self.player1.shooting:
			player1_loc = [self.player1.x, self.player1.y]
		self.player2.update(player2_loc, self.obstacles, \
			self.XDIM-ship_size, self.YDIM-ship_size)

		# update gui of the two players 
		[p1x, p1y] = self.player1.arena_location()
		self.coords(self.p1, p1x,p1y)
		[p2x, p2y] = self.player2.arena_location()
		self.coords(self.p2, p2x,p2y)

	def check_terminal(self):
		terminal = False
		if self.player1.health <= 0:
			self.create_text(self.XDIM/2,self.YDIM/2, \
				text='Player Two Victory', font=('arial 45 bold'), fill='red')
			terminal = True 
		elif self.player2.health <= 0:
			self.create_text(self.XDIM/2, self.YDIM/2, \
				text='Player One Victory', font=('arial 45 bold'), fill='red')
			terminal = True
		elif self.player1.x > self.camp2x and self.player1.y > self.camp2y:
			self.create_text(self.XDIM/2, self.YDIM/2, \
				text='Player One Victory', font=('arial 45 bold'), fill='red')
			terminal = True
		elif self.player2.x < self.camp1x and self.player2.y < self.camp1y:
			self.create_text(self.XDIM/2,self.YDIM/2, \
				text='Player Two Victory', font=('arial 45 bold'), fill='red')
			terminal = True 
		if terminal:
			self.master.update()
			time.sleep(3)
			self.master.destroy()
			sys.exit(0)
		return True 

	def update(self):
		self.check_bullet_hit()
		self.update_bullets()

		# fire if shooting 
		if self.player1.shooting:
			self.fire_bullets(1)
		if self.player2.shooting:
			self.fire_bullets(2)

		# update health display
		self.delete(self.health1)
		self.delete(self.health2)
		self.health1 = self.create_text(100,100,text=str(self.player1.health),\
			font=('arial 20 bold'), fill='white')
		self.health2 = self.create_text(self.XDIM-ship_size, \
			self.YDIM-ship_size,text=str(self.player2.health),\
			font=('arial 20 bold'), fill='white')

		self.update_players()

		# check terminal 
		self.check_terminal()
		return True 

	def manuel_control(self, event):
		if self.manuel == 1:
			pl = self.player1
		elif self.manuel == 2:
			pl = self.player2
		else:
			return True  
		dx = 0
		dy = 0
		if event.keysym=='Right':
			dx = 1
		elif event.keysym=='Left':
			dx = -1
		elif event.keysym=='Up':
			dy = -1
		elif event.keysym=='Down':
			dy = 1
		if event.keysym=='w':
			pl.gun_aim[1] -= 10
		elif event.keysym=='a':
			pl.gun_aim[0] -= 10
		elif event.keysym=='s':
			pl.gun_aim[1] += 10
		elif event.keysym=='d':
			pl.gun_aim[1] += 10
		if event.keysym == 'x':
			pl.start_firing()
		theta = np.arctan2(dy, dx)
		maxx = self.XDIM-ship_size
		maxy = self.YDIM-ship_size
		d_x = ship_speed*np.cos(theta)
		d_y = ship_speed*np.sin(theta)
		# print(pl.x+d_x, pl.y+d_y) 
		if pl.x + d_x > 0 and pl.x + d_x <= maxx and \
			pl.y + d_y > 0 and pl.y + d_y <= maxy:

			pl.x += d_x
			pl.y += d_y 
		return True 


if __name__=='__main__':
	root=Tkinter.Tk(className='Duel Bots')
	game = Arena(root, background='black')
	game.pack(expand='yes', fill='both')
	root.attributes('-fullscreen','true')

	while True:
		root.update()
		root.update_idletasks()
		game.update()

time.sleep(0.5)
