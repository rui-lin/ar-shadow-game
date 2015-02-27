import cv2
import numpy as np
from objects import Object, ObjectManager
from processing import ImageProcessor
from interactions import InteractionManager
import traceback

# Need native call to get otherwise
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024


class Game:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.object_manager = ObjectManager()
        self.interaction_manager = InteractionManager()
        self.cap = cv2.VideoCapture(0)

    def run(self):
        k = 0
        #cv2.namedWindow("display", cv2.WINDOW_NORMAL)
        while( self.cap.isOpened() ) :
            ret, img = self.cap.read()
            debug_drawing = np.zeros(img.shape,np.uint8)
            display_drawing = np.empty((SCREEN_HEIGHT,SCREEN_WIDTH,3),np.uint8); display_drawing.fill(255)
            #import ipdb; ipdb.set_trace()

            if k == 82: # init, or R
                print "COMMAND REGISTERED. calibrating background"
                #self.image_processor.startCalibration()
                self.image_processor.calibrate_background()

            # Update
            try:
                if self.image_processor.isCalibrationDone():
                    self.image_processor.update(img, debug_drawing)
                    self.object_manager.update()
                    self.interaction_manager.update(self.image_processor, self.object_manager)

                    # Render
                    self.image_processor.renderDebug(debug_drawing)
                    self.image_processor.renderDisplay(display_drawing)
                    self.object_manager.renderDebug(debug_drawing)
                    self.object_manager.renderDisplay(display_drawing)
                else:
                    self.image_processor.calibrationStep(img, debug_drawing)
                    self.image_processor.renderCalibrationDisplay(display_drawing)
        
                #Bug in OpenCV for MacOsX prevents fullscreen: http://code.opencv.org/issues/2846
                #cv2.namedWindow("display", cv2.WND_PROP_FULLSCREEN)        
                #cv2.setWindowProperty("display", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)          
                cv2.imshow('debug',debug_drawing)
                #scaled = cv2.resize(display_drawing, dsize=(SCREEN_WIDTH, SCREEN_HEIGHT) )
                # import ipdb; ipdb.set_trace()
                cv2.imshow('display', display_drawing)
            except Exception as e:
                print traceback.format_exc()

            
            #cv2.imshow('input',img)
                        
            k = cv2.waitKey(10)
            if k == 27:
                break

if __name__ == "__main__":
    game = Game()
    game.run()