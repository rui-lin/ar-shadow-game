# Object/collision manager

import cv2

class Object:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def render(self, drawing):
        cv2.circle(drawing, (int(self.x),int(self.y)), 10, (120,120,120),-1)

class Circle:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def render(self, drawing):
        cv2.circle(drawing, (int(self.x),int(self.y)), 50, (240,0,0),-1)

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

    def renderDebug(self, drawing):
        for o in self.objects:
            o.render(drawing)

    def renderDisplay(self, drawing):
        for o in self.objects:
            o.render(drawing)
