import cv2
from picamera2 import Picamera2
import numpy as np
import time
import RPi.GPIO as GPIO



LED_RED=17
LED_GREEN=27
LED_BLUE=22
LED_BLACK=10

LED_INV=18
Button=4
Red=5
Blue=6
Green=13
Black=19

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_RED,GPIO.OUT)
GPIO.setup(LED_GREEN,GPIO.OUT)
GPIO.setup(LED_BLUE,GPIO.OUT)
GPIO.setup(LED_BLACK,GPIO.OUT)

GPIO.setup(LED_INV,GPIO.OUT)
GPIO.setup(Button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Red, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Blue, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Green, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Black, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

piCam2 = Picamera2()
piCam2.preview_configuration.main.size = (640, 480)
piCam2.preview_configuration.main.format = "RGB888"
piCam2.preview_configuration.align()
piCam2.configure("preview")
piCam2.start()





print('test1')
def detect_dominant_color(frame):
    # Convert BGR to HSV
    
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define ranges for red, blue, and green in HSV
    lower_red = np.array([1, 75, 50])
    upper_red = np.array([9, 255, 255])
    
    lower_red2 = np.array([150, 75,50])
    upper_red2 = np.array([179, 255, 255])
    
    lower_blue = np.array([90, 75, 75])
    upper_blue = np.array([125, 255, 255])

    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])
    
    
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 30, 200])
    
    lower_yl = np.array([20, 50, 50])
    upper_yl = np.array([40, 255, 255])

    # Threshold the HSV image to get only specified colors
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_red2= cv2.inRange(hsv, lower_red2, upper_red2)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_yl = cv2.inRange(hsv, lower_yl, upper_yl)

    # Count the number of non-zero pixels for each color
    inver=cv2.bitwise_not(mask_yl)
    fred=cv2.bitwise_and(mask_red,inver)
    fred2=cv2.bitwise_and(mask_red2,inver)
    fgreen=cv2.bitwise_and(mask_green,inver)
    fblue=cv2.bitwise_and(mask_blue,inver)
    fblack=cv2.bitwise_and(mask_black,inver)
    
    red_pixels = np.count_nonzero(fred) + np.count_nonzero(fred2)
    blue_pixels = np.count_nonzero(fblue)
    green_pixels = np.count_nonzero(fgreen)
    black_pixels = np.count_nonzero(fblack)
    print(red_pixels,blue_pixels,green_pixels,black_pixels)
    # Determine the dominant color
    dominant_color = None
    if red_pixels > blue_pixels and red_pixels > green_pixels and red_pixels > black_pixels:
        dominant_color = "Rouge"
        GPIO.output(LED_RED,GPIO.HIGH)
        GPIO.output(LED_GREEN,GPIO.LOW)
        GPIO.output(LED_BLUE,GPIO.LOW)
        GPIO.output(LED_BLACK,GPIO.LOW)

    elif blue_pixels > red_pixels and blue_pixels > green_pixels and blue_pixels > black_pixels:
        dominant_color = "Blue"
        GPIO.output(LED_RED,GPIO.LOW)
        GPIO.output(LED_GREEN,GPIO.LOW)
        GPIO.output(LED_BLUE,GPIO.HIGH)
        GPIO.output(LED_BLACK,GPIO.LOW)
        
    elif green_pixels > red_pixels and green_pixels > blue_pixels and green_pixels > black_pixels:
        dominant_color = "Vert"
        GPIO.output(LED_RED,GPIO.LOW)
        GPIO.output(LED_GREEN,GPIO.HIGH)
        GPIO.output(LED_BLUE,GPIO.LOW)
        GPIO.output(LED_BLACK,GPIO.LOW)
        
        
    elif black_pixels > red_pixels and black_pixels > blue_pixels and black_pixels > green_pixels:
        dominant_color = "Noir"
        GPIO.output(LED_RED,GPIO.LOW)
        GPIO.output(LED_GREEN,GPIO.LOW)
        GPIO.output(LED_BLUE,GPIO.LOW)
        GPIO.output(LED_BLACK,GPIO.HIGH)
    else:
        dominant_color = "None"
        GPIO.output(LED_RED,GPIO.LOW)
        GPIO.output(LED_GREEN,GPIO.LOW)
        GPIO.output(LED_BLUE,GPIO.LOW)
        GPIO.output(LED_BLACK,GPIO.LOW)
    return dominant_color


def insignal():
	
	if GPIO.input(Red)==GPIO.HIGH:
		color="Rouge"
	elif GPIO.input(Blue)==GPIO.HIGH:
		color="Blue"
	elif GPIO.input(Green)==GPIO.HIGH:
		color="Vert"
	elif GPIO.input(Black)==GPIO.HIGH:
		color="Noir"
	else:
		color='None'
	return color
roi_size=100
height = 480
width = 640
center_x = width // 2
center_y = height // 2
x1=max(0,center_x-roi_size // 2)
y1=max(0,center_y-roi_size // 2)
x2=min(width,center_x+roi_size // 2)
y2=min(height,center_y+roi_size // 2)

while True:
    frame = piCam2.capture_array()
    cv2.rectangle(frame,(x1-1,y1-1),(x2+1,y2+1),(0,0,0),1)
    frame2=frame[y1:y2,x1:x2]
    if GPIO.input(Button)==GPIO.HIGH:
    #if True:
        print(f'{detect_dominant_color(frame2)},{insignal()}')
        if detect_dominant_color(frame2)==insignal() and insignal()!="None":
            GPIO.output(LED_INV,GPIO.HIGH)

        else:
            GPIO.output(LED_INV,GPIO.LOW)

        
    cv2.imshow("piCam", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        GPIO.cleanup()
        break
    time.sleep(0.1)
    
piCam2.stop()
cv2.destroyAllWindows()
