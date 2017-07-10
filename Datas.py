

class Datas(object):

	def __init__(self):
		self.info = []
		self.tp = []
		self.switch = []

	def __getitem__(self, index):
		return self.__getattribute__(index)
