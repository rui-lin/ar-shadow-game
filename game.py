import cv2
import numpy as np
from objects import Object, ObjectManager
from processing import ImageProcessor


class Game:
	def __init__(self):
		self.image_processor = ImageProcessor()
		self.object_manager = ObjectManager()
		self.cap = cv2.VideoCapture(0)

	def run(self):
		self.object_manager.add(Object(1,1,10,10))

		while( self.cap.isOpened() ) :
			# Update
		    ret, img = self.cap.read()
		    cnt, hand = self.image_processor.getContours(img)
		    self.object_manager.update()

		    # Render
		    drawing = np.zeros(img.shape,np.uint8)
		    cv2.drawContours(drawing,[cnt],0,(0,255,0),2) 
		    cv2.drawContours(drawing,[hand],0,(0,0,255),2) 
		    self.object_manager.render(drawing)

		    cv2.imshow('output',drawing)
		    cv2.imshow('input',img)
		                
		    k = cv2.waitKey(10)
		    if k == 27:
		        break

if __name__ == "__main__":
	game = Game()
	game.run()