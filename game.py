import cv2
import numpy as np
from objects import Object, ObjectManager
from processing import ImageProcessor
from interactions import InteractionManager


class Game:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.object_manager = ObjectManager()
        self.interaction_manager = InteractionManager()
        self.cap = cv2.VideoCapture(0)

    def run(self):
        self.object_manager.add(Object(1,1,10,10))

        while( self.cap.isOpened() ) :
            ret, img = self.cap.read()
            drawing = np.zeros(img.shape,np.uint8)

            # Update
            try:
                self.image_processor.update(img, drawing)
                self.object_manager.update()
                self.interaction_manager.update(self.image_processor, self.object_manager)
            except Exception as e:
                print e

            # Render
            self.image_processor.render(drawing)
            self.object_manager.render(drawing)

            cv2.imshow('output',drawing)
            #cv2.imshow('input',img)
                        
            k = cv2.waitKey(10)
            if k == 27:
                break

if __name__ == "__main__":
    game = Game()
    game.run()