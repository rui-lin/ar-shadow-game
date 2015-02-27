import math
from objects import Object, ObjectManager, Circle
from processing import ImageProcessor
from collections import deque
import cv2
import subprocess

# Need native call to get otherwise
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024

class InteractionManager:
    def __init__(self):
        self.last_angles = deque(maxlen=5)
        self.last_handcx = deque(maxlen=5)
        self.last_handcy = deque(maxlen=5)
        self.delaying = 0

    FIRE_DELAY = 2 # cycles

    bubble_pop_file = "assets/Blop.mp3"

    # radians, smaller angle diff
    def angle_diff(self, a, b):
        return min(abs(b-a), 2*math.pi-abs(b-a))

    # get oldest 3 (movement may take a bit to recognize)
    def get_last_angle(self):
        num = min(len(self.last_angles), 3)
        if num == 0:
            return 0
        elif num == 1:
            return self.last_angles[0]
        else:
            return sum(self.last_angles[i] for i in xrange(0,num))/num

    def get_last_handcx(self):
        return sum(x for x in self.last_handcx)/5
    def get_last_handcy(self):
        return sum(x for x in self.last_handcy)/5


    def update(self, image_processor, object_manager):
        self.calc_gun_trigger(image_processor, object_manager)
        self.update_collisions(image_processor, object_manager)

    def circle_touch(self, ax, ay, ar, bx, by, br):
        return (ax-bx)**2 + (ay-by)**2 <= (ar+br)**2

    def update_collisions(self, image_processor, object_manager):
        for o in object_manager.objects:
            if isinstance(o, Circle):
                if o.x - o.r <= 0:
                    o.x = o.r
                    o.vx = -o.vx
                if o.x + o.r >= SCREEN_WIDTH:
                    o.x = SCREEN_WIDTH - o.r
                    o.vx = -o.vx
                if o.y - o.r <= 0:
                    o.y = o.r
                    o.vy = -o.vy
                if o.y + o.r >= SCREEN_HEIGHT:
                    o.y = SCREEN_HEIGHT - o.r
                    o.vy = -o.vy
                if cv2.pointPolygonTest(image_processor.cnt_hull, (o.x, o.y), True) <= o.r:
                    #o.pop_bubble()
                    pass
                for o2 in object_manager.objects:
                    if isinstance(o2, Object):
                        if self.circle_touch(o.x, o.y, o.r, o2.x, o2.y, o2.r):
                            o.pop_bubble()
                            o2.popped = True
                            proc = subprocess.Popen(["afplay", bubble_pop_file])
                            proc.terminate()
            if isinstance(o, Object):
                if (o.x + o.r <= 0 or o.x - o.r >= SCREEN_WIDTH or o.y + o.r <= 0 or o.y - o.r >= SCREEN_HEIGHT):
                    o.popped = True

        # trigger delete animation. mark object dying

    def calc_gun_trigger(self, image_processor, object_manager):
        last_angle = self.get_last_angle()
        new_angle = image_processor.angle

        print "facing right" if image_processor.faceMinx else "facing left"
        print "last_angle: {0}, new_angle: {1}".format(last_angle, new_angle)

        fire = False
        if self.delaying:
            self.delaying -= 1
        else:
            if image_processor.faceMinx: #towards minx, righthandside
                if new_angle - last_angle > math.pi/8: # shoot up
                    fire = True
            else: # left
                # mirror angle to face other way
                t_new_angle = math.pi - abs(new_angle) if new_angle>=0 else -math.pi - abs(new_angle)
                t_last_angle = math.pi - abs(last_angle) if last_angle>=0 else -math.pi - abs(last_angle)
                if t_new_angle - t_last_angle > math.pi/8:
                    fire = True

        #and self.angle_diff(last_angle, new_angle) > math.pi/8:
            
        if fire:
            print "firing, last_angle: {0}, new_angle: {1}".format(last_angle, new_angle)

            last_handcx = self.get_last_handcx()
            last_handcy = self.get_last_handcy()
            v = 30
            object_manager.add(Object(
                last_handcx,
                last_handcy,
                v*math.cos(last_angle), 
                -v*math.sin(last_angle)
                ))
            self.delaying = self.FIRE_DELAY
            self.last_angles.clear()

        self.last_angles.append(new_angle)
        self.last_handcx.append(image_processor.handcx)
        self.last_handcy.append(image_processor.handcy)



