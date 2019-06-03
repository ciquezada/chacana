import cv2
import numpy as np
import os


# Carpeta con las imagenes de circulos
PATH = "circles_detector"+os.sep+"circles"
# Rango del centro aproximado
Y_CENTER = (467, 487)
X_CENTER = (718,738)

cwd = os.getcwd()

class circle_detector():

    def __init__(self):
        print("\nIniciando Detector de Circulos...")
        self.detections = self.detect()
        self.detections_mean = self.detections.mean(axis=0)
        self.error = np.sqrt(np.mean((self.detections -
                                            self.detections_mean)**2, axis=0))

        print("...centro promedio en")
        print("\tx={}, y={}".format(self.detections_mean[1],
                                            self.detections_mean[0]))
        print("...con desviacion estandar:")
        print("\tx_err={}, y_err={}".format(self.error[1], self.error[0]))

    def detect(self):
        print("buscando en imagenes en:\n \"{}\"".format(cwd+os.sep+PATH+os.sep))
        files = self.get_dir_files(cwd+os.sep+PATH+os.sep)
        detections = []
        for path in files:
            for xy in self.detect_circles_from(PATH+os.sep+path):
                detections.append(xy)
        detections = np.array(detections)
        return detections

    def get_dir_files(self, path):
        files = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if '.png' in file:
                    files.append(os.path.join(r, file))
        return(f)

    def detect_circles_from(self, path):
        img = cv2.imread(path,0)
        img = cv2.medianBlur(img,5)
        cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,
                                    param1=50,param2=30,minRadius=0,maxRadius=0)

        try:
            circles = np.uint16(np.around(circles))
        except:
            return []

        out = []
        for i in circles[0,:]:
            if (X_CENTER[0]<=i[0]<=X_CENTER[1]
                                    and Y_CENTER[0]<=i[1]<=Y_CENTER[1]):
                out.append((i[1], i[0]))
        # ######### mostrar circulos
        #         # draw the outer circle
        #         print("detection: y = {}, x = {}".format(i[1],i[0]))
        #         cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
        #         # draw the center of the circle
        #         cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
        # cv2.imshow('detected circles',cimg)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # ######################################################################
        return out
