# Object/collision manager

import cv2

class Object:
	def __init__(self, x, y, vx, vy):
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy

	def render(self, drawing):
		cv2.circle(drawing, (self.x,self.y), 10, (120,120,120))

class ObjectManager:
	def __init__(self):
		self.objects = []

	def add(self, obj):
		self.objects += [obj]

	def update(self):
		for o in self.objects:
			o.x += o.vx
			o.y += o.vy
		# todo: collision

	def render(self, drawing):
		for o in self.objects:
			o.render(drawing)


