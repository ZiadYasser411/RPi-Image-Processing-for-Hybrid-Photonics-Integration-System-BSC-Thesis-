import cv2
from shapeDetector import ShapeDetector
import argparse
import imutils

def define_roi(x1, y1, x2, y2, frame):
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw blue rectangle

x1 = 120
y1 = 150
x2 = 240
y2 = 250

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to the input image")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])
image = imutils.resize(image, width=600)
ratio = image.shape[0] / float(image.shape[0])
gray = cv2.cvtColor(image[0:500,0:550], cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
canny = cv2.Canny(blurred, threshold1=10, threshold2=20)
thresh = cv2.threshold(canny, 0, 255, cv2.THRESH_BINARY)[1]

ROI_frame = image[y1:y2, x1:x2]
define_roi(x1, y1, x2, y2, image)

cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
sd = ShapeDetector()

for c in cnts:
    M = cv2.moments(c)

    # Check if the area (m00) is non-zero before performing division
    if M["m00"] != 0:
        cX = int((M["m10"] / M["m00"]) * ratio)
        cY = int((M["m01"] / M["m00"]) * ratio)
        
        shape = sd.detect(c)

        c = c.astype("float")
        c *= ratio
        c = c.astype("int")
        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
cv2.imshow("Image", image)
cv2.imshow("Canny", thresh)
cv2.waitKey(0)



def getROI(img, imgContour):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        areaMin = cv2.getTrackbarPos("ROI Area", "Parameters")
        area = cv2.contourArea(cnt)
        epsilon = 0.03 * cv.arcLength(cnt, True)
        approx = cv.approxPolyDP(cnt, epsilon, True)
        num_vertices = len(approx)
        x, y, w, h = cv.boundingRect(approx)
        aspect_ratio = float(w) / h
        cv.rectangle(imgContour, (x , y), (x + w, y + h), (0, 255, 0), 2)
        cv.putText(imgContour, "ROI", (x + w + 20, y + 180), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)  # Only print "ROI"
