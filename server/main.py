import collections, pickle, socket, time, _thread

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

class ServerRoot(BoxLayout):
	match_number = ObjectProperty()
	category_name = ObjectProperty()

	chung_name = ObjectProperty()
	chung_score = ObjectProperty()
	chung_penalty = ObjectProperty()

	hong_name = ObjectProperty()
	hong_score = ObjectProperty()
	hong_penalty = ObjectProperty()

	time_counter = ObjectProperty()

	"""docstring for ServerRoot"""
	def __init__(self, **kwargs):
		super(ServerRoot, self).__init__(**kwargs)
		self.chung_temp_score, self.hong_temp_score = [], []
		
		with open("server.txt") as f:
			server = f.read().split()

		self.t = _thread.start_new_thread(self.start_socket_connection, (server[0], int(server[1])))
		self.t2 = _thread.start_new_thread(self.score_tracker, ())
		self.t3 = _thread.start_new_thread(self.chung_temp_score_resetter, ())
		self.t4 = _thread.start_new_thread(self.hong_temp_score_resetter, ())

	def start_socket_connection(self, host, port):
		print("Starting up socket connection...")
		self.s = socket.socket()
		self.s.bind((host, port))
		self.s.listen(4)

		while True:
			c, addr = self.s.accept()
			_thread.start_new_thread(self.on_new_client, (c,addr))
		c.close()
			
	def on_new_client(self, c, addr):
		print("New client connected. " + str(addr))
		while True:
			data = c.recv(1024)
			if not data:
				break
			d = pickle.loads(data)
			print("Received: " + str(d))

			for key in d:
				if key == 'update_match_number':
					self.match_number.text='Match ' + d[key]

				elif key == 'update_category_name':
					self.category_name.text = 'Category ' + d[key]

				elif key == 'update_chung_name':
					self.chung_name.text = d[key]

				elif key == 'update_chung_team':
					pass

				elif key == 'add_chung_score' or key =='minus_chung_score':
					self.chung_score.text = str(d[key])

				elif key == 'add_chung_penalty' or key =='minus_chung_penalty':
					self.chung_penalty.text = str(d[key])

				elif key == 'update_hong_name':
					self.hong_name.text = d[key]

				elif key == 'add_hong_score' or key == 'minus_hong_score':
					self.hong_score.text = str(d[key])

				elif key == 'add_hong_penalty' or key == 'minus_hong_penalty':
					self.hong_penalty.text = str(d[key])

				elif key == 'update_time_counter':
					self.time_counter.text = str(d[key])

				elif key == 'chung_score':
					self.chung_temp_score.append(d[key])

				elif key == 'hong_score':
					self.hong_temp_score.append(d[key])

		c.close()

	def score_tracker(self):
		while True:
			c_s = [item for item, count in collections.Counter(self.chung_temp_score).items() if count > 1]
			h_s = [item for item, count in collections.Counter(self.hong_temp_score).items() if count > 1]
			if len(c_s) > 0:
				print('Chung scores ', c_s[0])
				del self.chung_temp_score[:]
			if len(h_s) > 0:
				print('Hong scores ', h_s[0])
				del self.hong_temp_score[:]

	def chung_temp_score_resetter(self):
		counter = 0
		while True:
			if len(self.chung_temp_score) > 0:
				time.sleep(1)
				counter += 1
			if counter >= 3:
				print('3 seconds passed. Clear Chung temp scores.')
				del self.chung_temp_score[:]
				counter = 0

	def hong_temp_score_resetter(self):
		counter = 0
		while True:
			if len(self.hong_temp_score) > 0:
				time.sleep(1)
				counter += 1
			if counter >= 3:
				print('3 seconds passed. Clear Hong temp scores.')
				del self.hong_temp_score[:]
				counter = 0

class EssServer(App):

	def build(self):
		self.root = ServerRoot()
		return self.root


if __name__ == '__main__':

	EssServer().run()
