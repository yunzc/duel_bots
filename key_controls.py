class Key_Controller():
	def __init__(self, startpos=[5, 5], port=1024, p_gain=0.15, d_gain=3.2, i_gain=0., unit_test=False):
		self.host = 'localhost'
		if unit_test:
			self.waypts = pathfinding(self.host, port, startpos, unit_test=unit_test)[0]
		else:
			self.waypts = pathfinding(self.host, port, startpos)
		# print(self.waypts)
		self.port = port
		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clientSocket.connect((self.host, self.port))
		self.prevError = 0 # for the derivative control 
		self.culError = 0 # for the integral control 
		# parameters to navigate path 
		self.p_gain = p_gain
		self.d_gain = d_gain
		self.i_gain = i_gain
		self.mindex = 0 # keep track of where vehicle is along path 
		self.quit = False

	def getControl(self, pose): # PID controller
		seg_start = self.waypts[self.mindex]
		seg_end = self.waypts[(self.mindex+1)]
		s_vector = [seg_end[0]-seg_start[0], seg_end[1]-seg_start[1]] # segment vector 
		d_vector = [pose[0]-seg_start[0], pose[1]-seg_start[1]]
		s_mag = math.sqrt(s_vector[0]**2 + s_vector[1]**2)
		dprod = (d_vector[0]*s_vector[0] + d_vector[1]*s_vector[1])/(s_mag*s_mag)
		if dprod > 1: # move on to next seg 
			self.mindex = (self.mindex + 1)
			seg_start = self.waypts[self.mindex]
			seg_end = self.waypts[(self.mindex+1)]
			if seg_end == len(self.waypts):
				return None
			s_vector = [seg_end[0]-seg_start[0], seg_end[1]-seg_start[1]] # segment vector 
			d_vector = [pose[0]-seg_start[0], pose[1]-seg_start[1]]
			s_mag = math.sqrt(s_vector[0]**2 + s_vector[1]**2)
			dprod = (d_vector[0]*s_vector[0] + d_vector[1]*s_vector[1])/(s_mag*s_mag)
			self.culError = 0
		# cross product for error |s||d|sin(x)/|s||d|
		err = (s_vector[0]*d_vector[1] - s_vector[1]*d_vector[0])/(s_mag*s_mag)
		d_err = err - self.prevError
		omega = -(self.p_gain*err + self.d_gain*d_err + self.i_gain*self.culError)
		self.prevError = err
		return (5.0, omega) 

	def run(self):
		start_time = time.time()
		while not self.quit: # here might have to add in tic-toc stuff 
			t = time.time()
			try:
				data = self.clientSocket.recv(1024)
				value = data.split()
				if value == []: # disconnected 
					print('disconnected')
					break
				vehPos = [float(value[0]), float(value[1]), float(value[2])]
				control = self.getControl(vehPos)
				# send back  data 
				if control == None: 
					contData = 'None'
					self.quit = True
				else:
					contData = str(control[0]) + ' ' + str(control[1])
				self.clientSocket.sendall(contData)
			except:
				continue
			elapsed = time.time() - t
			if elapsed < 0.15:
				time.sleep(0.15 - elapsed) # cycle of 10 milli-secs 
		total_time = time.time() - start_time
		print('total time to find beacon: ', total_time)
		self.clientSocket.close()


if __name__ == '__main__':
	# one vehicel 
	nc = Controller()
nc.run()