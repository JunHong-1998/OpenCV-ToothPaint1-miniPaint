import numpy as np
import cv2
import math

class Paint_CV:
    def __init__(self):
        pass

    def CropImage(self, image, coords):
        return image[min(coords[1], coords[3]):max(coords[1], coords[3])+1, min(coords[0], coords[2]):max(coords[0], coords[2])+1]

    def SaveImage(self, filename, image):
        return cv2.imwrite(filename, image)

    def LoadImage(self, filepath):
        return cv2.imread(filepath)

    def ResizeImage(self, image, dim):
        return cv2.resize(image, (dim[0], dim[1]),cv2.INTER_AREA)

    def ConvertColor(self, type, image):
        if type==0:
            return image
        elif type==1:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif type==2:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        elif type==3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:,:,0]
        elif type==4:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:,:,1]
        elif type==5:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:,:,2]
        elif type==6:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
        elif type==7:
            return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)[:,:,1]
        elif type == 8:
            return cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        elif type == 9:
            return cv2.cvtColor(image, cv2.COLOR_RGB2LUV)
        elif type == 10:
            return cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        elif type == 11:
            return cv2.cvtColor(image, cv2.COLOR_RGB2XYZ)

    def OverlayImage(self, image, background, coords):
        top, bottom, left, right = coords[1], coords[1] + image.shape[0], coords[0], coords[0] + image.shape[1]
        if left>background.shape[1] or right<0 or top>background.shape[0] or bottom<0:
            return background
        if left<0:
            image = self.CropImage(image, (abs(left), 0, image.shape[1], image.shape[0]))
            left = 0
        if right>background.shape[1]:
            image = self.CropImage(image, (0, 0, image.shape[1]-(right-background.shape[1])-1, image.shape[0]))
            right = background.shape[1]
        if top<0:
            image = self.CropImage(image, (0, abs(top), image.shape[1], image.shape[0]))
            top = 0
        if bottom>background.shape[0]:
            image = self.CropImage(image, (0, 0, image.shape[1], image.shape[0]-(bottom-background.shape[0])-1))
            bottom = background.shape[0]
        background[top:bottom, left:right] = image
        return background

    def RotateImage(self, image, coords, index):
        # new_coord = (coords[0], coords[1])
        if index < 4:
            ang = 0
            lst = []
            center = (coords[0] + image.shape[1] / 2, coords[1] + image.shape[0] / 2)
            if index == 1:
                ang = -90, 3
            elif index == 2:
                ang = 90, 1
            elif index == 3:
                ang = 180, 2
            M = cv2.getRotationMatrix2D(center, ang[0], 1)
            coordes = np.array([[coords[0], coords[1], 1], [coords[0] + image.shape[1], coords[1], 1], [coords[0] + image.shape[1], coords[1] + image.shape[0], 1], [coords[0], coords[1] + image.shape[0], 1]])
            for coord in coordes:
                lst.append(np.array(np.round(M.dot(coord), 0)).astype(int).tolist())
            coords = (min(lst)[0], min(lst)[1], max(lst)[0],max(lst)[1])
            image = np.rot90(image, ang[1]).copy()
        else:
            if index == 4:
                image = cv2.flip(image, 0)  # flip vertical
            elif index == 5:
                image = cv2.flip(image, 1)  # flip horizontal
        return image, coords

    def drawPrimitive(self, image, coords, type, color=(255,255,255), thick=None):      # dotted square, line, filled-square, square,
        if type == 1:
            color = (150,150,150)
            width = 5
            thick = 1
            LR, UD, dst = self.calcRegion(coords)
            if sum(dst) == 0:
                return
            gap = dst[0] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0] + width * 2 * LR * i, coords[1]), (coords[0] + width * 2 * LR * i + width * LR, coords[1]), color, thick, cv2.LINE_AA)
                cv2.line(image, (coords[2] + width * 2 * LR * i * -1, coords[3]), (coords[2] + width * 2 * LR * i * -1 + width * LR * -1, coords[3]), color, thick, cv2.LINE_AA)
            gap = dst[1] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0], coords[1] + width * 2 * UD * i), (coords[0], coords[1] + width * 2 * UD * i + width * UD), color, thick, cv2.LINE_AA)
                cv2.line(image, (coords[2], coords[3] + width * 2 * UD * i * -1), (coords[2], coords[3] + width * 2 * UD * i * -1 + width * UD * -1), color, thick, cv2.LINE_AA)
        elif type==2:
            color = (150, 150, 150)
            width = 2
            LR, UD, dst = self.calcRegion(coords)
            gap = dst[0] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0] + width * 2 * LR * i, coords[1]), (coords[0] + width * 2 * LR * i + width * LR, coords[1]), color, 1, cv2.LINE_AA)
            gap = dst[1] / width
            for i in range(math.ceil(gap / 2)):
                cv2.line(image, (coords[0], coords[1] + width * 2 * UD * i), (coords[0], coords[1] + width * 2 * UD * i + width * UD), color, 1, cv2.LINE_AA)
        elif type == 3:
            cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), color, thick, cv2.LINE_AA)
        elif type == 5:
            cv2.rectangle(image, (coords[0], coords[1]), (coords[2], coords[3]), color, thick, cv2.LINE_AA)
        elif type == 4:
            center, radius = self.recalc_Center_Radius(coords)
            cv2.circle(image, center, max(radius), color, thick, cv2.LINE_AA)
        elif type == 6:
            cv2.polylines(image, [self.Triangle(coords)], True, color, thick, cv2.LINE_AA)
        elif type == 8:
            cv2.fillPoly(image, [self.Triangle(coords)], color)
        elif type == 7:
            cv2.polylines(image, [self.Diamond(coords)], True, color, thick, cv2.LINE_AA)
        elif type == 9:
            cv2.fillPoly(image, [self.Diamond(coords)], color)


    def drawText(self, image, text, coords, fontstyle, scale, color, thick):
        font = None
        if fontstyle == 0:
            font = cv2.FONT_HERSHEY_COMPLEX
        elif fontstyle == 1:
            font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        elif fontstyle == 2:
            font = cv2.FONT_HERSHEY_DUPLEX
        elif fontstyle == 3:
            font = cv2.FONT_HERSHEY_PLAIN
        elif fontstyle == 4:
            font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        elif fontstyle == 5:
            font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        elif fontstyle == 6:
            font = cv2.FONT_HERSHEY_TRIPLEX
        elif fontstyle == 7:
            font = cv2.FONT_ITALIC
        cv2.putText(image, text, coords, font, scale, color, thick)

    def recalc_Center_Radius(self, coords):
        LR, UD, dst = self.calcRegion(coords)
        radius = [dst[0]//2, dst[1]//2]
        center = (int(coords[0]+radius[0]*LR), int(coords[1]+radius[1]*UD))
        return center, radius

    def Triangle(self, coords):
        center, radius = self.recalc_Center_Radius(coords)
        c = [center[0], center[1]-radius[1]]
        b = [center[0] +radius[0], center[1]+radius[1]]
        a = [center[0] -radius[0], center[1]+radius[1]]
        return np.array([a,b,c], np.int32)

    def Diamond(self, coords):
        center, radius = self.recalc_Center_Radius(coords)
        return np.array([[center[0]-radius[0], center[1]], [center[0], center[1]-radius[1]], [center[0]+radius[0], center[1]], [center[0], center[1]+radius[1]]], np.int32)


    def ReLocateCoords(self, coords):
        LR, UD, dst = self.calcRegion(coords)
        if LR==-1:
            coords[0] -= dst[0]
            coords[2] += dst[0]
        if UD == -1:
            coords[1] -= dst[1]
            coords[3] += dst[1]
        return coords


    def calcRegion(self, coords):
        LR = UD = 0
        dst = [0, 0]
        x1 = coords[0]
        y1 = coords[1]
        x2 = coords[2]
        y2 = coords[3]
        if x2 < x1:
            LR = -1
            dst[0] = x1 - x2
        elif x2 > x1:
            LR = 1
            dst[0] = x2 - x1
        if y2 < y1:
            UD = -1
            dst[1] = y1 - y2
        elif y2 > y1:
            UD = 1
            dst[1] = y2 - y1
        return LR, UD, dst

    def Color_picker(self, color):
        image = np.zeros((300, 300, 3), np.uint8)
        image[:] = color
        self.drawPrimitive(image, (int(300*.01), int(300*.01), int(300*.99), int(300*.99)), 5, (0,0,0), 10)
        self.drawPrimitive(image, (int(300*.1), int(300*.1), int(300*.9), int(300*.9)), 5, (255,255,255), 20)
        self.SaveImage("TP_assets/color.png", image)
