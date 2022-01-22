import cv2 as cv
from cv2 import cvtColor
import numpy as np

#accessing camera
source = 1 #0 is native, 1 is external
camera = cv.VideoCapture(source, cv.CAP_DSHOW)
camera.set(cv.CAP_PROP_EXPOSURE, -7)




def isCircle(cnt, contours):
    approx = cv.approxPolyDP(cnt, 0.01 * cv.arcLength(cnt, True), True)
    
    if len(approx) > 8 and (3.14 * cv.minEnclosingCircle(cnt)[1] ** 2 - cv.contourArea(cnt) < (3.14 * cv.minEnclosingCircle(cnt)[1] ** 2) * (1 - 0.65)):
        return True
            
    
    return False

def drawRect(mask, img, color):
    #color dictionary
    colors = {"red": (0, 0, 255), "blue": (255, 0, 0)}
    # mask = cv.bitwise_and(img, img, mask = mask)
    # mask = cv.cvtColor(mask, cv.COLOR_HSV2BGR)
    # mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
    
    colored_box = colors[color]
    
    #Get contours on the mask
    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(contours) == 2:
        contours = contours[0]
        
    else:
        contours = contours[1]
        
    for contour in contours:
        if isCircle(contour, contours):
            x, y, w, h = cv.boundingRect(contour)
            aspect_ratio = w/h
            area = w * h
            if .7 <= aspect_ratio <= 1.3 and area > 350:
                #cv.circle(frame, (x+ (w/2), y+(y/2)), colored_box, 2)
                cv.rectangle(frame, (x, y), (x + w, y + h), colored_box, 2)
                cv.putText(img, color.upper() + " BALL", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, colored_box, 2)
    #Draw rectangle with specific color using aspect ratio and area tests
    
          

def editImage(img):
    #blur, erode, and dilate frame
    
    img = cv.GaussianBlur(img, (11, 11), None)
    img = cv.morphologyEx(img, cv.MORPH_CLOSE, (7,7))
    img = cv.morphologyEx(img, cv.MORPH_OPEN, (3,3))

    #img = cv.erode(img, None, iterations=2)
    #img = cv.dilate(img, None)
    
    return img


def createBlueMask(img):
    global mask_blue
    #blue values 
    #img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    if(source == 1): #for fisheye:
        lower1 = np.array([92,132,67])               # my laptop cam: ([99,90,50]) # (45, 120, 50)
        upper1 = np.array([123,255,255])
    elif(source == 0): # native cam:
        lower1 = np.array([87,71,1]) #([141,99,7])
        upper1 = np.array([123,255,255])# [217, 255, 255]                    # ([132,255,255]) #v (163, 255, 255)
    
    mask_blue = cv.inRange(hsv, lower1, upper1)
    #mask_blue = cv.bitwise_and(img, img, mask = mask_blue)
    #mask_blue = cv.cvtColor(mask_blue, cv.COLOR_HSV2BGR)
   
    
    
    return mask_blue

def createRedMask(img):
    global mask_red
    #img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    #red values
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
    if(source == 0): # integrated webcam
        lower_red_1 = np.array([115,83,0])
        upper_red_1 = np.array([189,255,255])
        #lower_red_1 = np.array([170, 85, 13])         #previous fisheye: ([135,120,31])         for my laptop camera: ([163, 49, 0])
        #upper_red_1 = np.array([229,255,255])                          #fisheye1: ([245,255,255])         ([245, 229, 255])
    elif(source == 1): #fisheye
        lower_red_1 = np.array([135,120,31])   #np.array([0, 127,143])      #
        upper_red_1 = np.array([245,255,255])  #np.array([94,255,255])      #np.array([245,255,255])  
    mask_red = cv.inRange(hsv, lower_red_1, upper_red_1)
    #mask_red = cv.bitwise_and(img, img, mask = mask_red)
    #mask_red = cv.cvtColor(mask_red, cv.COLOR_HSV2BGR)88

    return mask_red

#infinite loop to process live feed
while True:
    ret, frame = camera.read()
    
    #cv.normalize(frame, frame, 0, 255, cv.NORM_MINMAX)
    copy_frame = frame
    
    #call on functions
    
    drawRect(    createRedMask(editImage(frame)), frame, "red")
    drawRect(    createBlueMask(editImage(frame)), frame, "blue")

    #show windows
    cv.imshow("blue mask", mask_blue)
    cv.imshow("red mask", mask_red)
    cv.imshow("frame", frame)
    
    #break loop if key pressed
    if cv.waitKey(1) & 0xFF is ord('q'):
        break

    
camera.release()
cv.destroyAllWindows()