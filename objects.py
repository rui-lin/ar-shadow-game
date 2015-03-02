# Object/collision manager

import cv2

class Object:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = 20
        self.popped = False

    def render(self, drawing):
        cv2.circle(drawing, (int(self.x),int(self.y)), self.r, (120,120,120),-1)

class Circle:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.popping = False
        self.popped = False
        self.r = 50
        self.pop_rate = 100

    def pop_bubble(self):
        self.popping = True
        self.vx = 0
        self.vy = 0

    def render(self, drawing):
        if self.popping:
            cv2.circle(drawing, (int(self.x),int(self.y)), 50, (0+self.pop_rate, 0 + self.pop_rate, 0 + self.pop_rate),-1)
            self.pop_rate += 100
            if self.pop_rate > 255:
                self.pop_rate = 255
                self.popped = True
        else:
            cv2.circle(drawing, (int(self.x),int(self.y)), 50, (240,180,180),-1)

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
            if o.popped:
                self.objects.remove(o)
            o.render(drawing)
