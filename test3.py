import cv2 as cv
import numpy as np 
import imutils
from pypylon import pylon

# Function to convert pixels to centimeters
def pixels_to_cm(pixels):
    factor1 = 0.0090
    factor2 = 0.0087
    average_factor = (factor1 + factor2) / 2
    return round(pixels * average_factor, 1)

# Empty callback function for trackbars
def empty(a):
    pass

# Create a named window and trackbars
cv.namedWindow("Parameters")
cv.resizeWindow("Parameters", 600, 230)
cv.createTrackbar("threshold 1", "Parameters", 26, 255, empty)
cv.createTrackbar("threshold 2", "Parameters", 43, 255, empty)
cv.createTrackbar("Shapes area", "Parameters", 31000, 50000, empty)
cv.createTrackbar("threshold 3", "Parameters", 90, 255, empty)
cv.createTrackbar("threshold 4", "Parameters", 140, 255, empty)
cv.createTrackbar("ROI Area", "Parameters", 47700, 50000, empty)

# Function to get the center of a contour
def get_center(contour):
    rect = cv.minAreaRect(contour)
    center = (int(rect[0][0]), int(rect[0][1]))
    return center

def getROI(img, imgContour):
    contours, hierarchy = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    for cnt in contours:
        areaMin = cv.getTrackbarPos("ROI Area", "Parameters")
        area = cv.contourArea(cnt)
        if area > areaMin:
            epsilon = 0.03 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            num_vertices = len(approx)
            x, y, w, h = cv.boundingRect(approx)
            cv.rectangle(imgContour, (x , y), (x + w, y + h), (0, 255, 0), 2)
            cv.putText(imgContour, "ROI", (x + 30, y + 30), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            origin = (int(x), int(y))
            return origin

# Function to process contours and draw shapes
def process_contours(img, imgContour):
    contours, _ = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    for cnt in contours:
        areaMin = cv.getTrackbarPos("Shapes area", "Parameters")
        area = cv.contourArea(cnt)
        if area > areaMin:
            center = get_center(cnt)
            if center is None:
                continue
            height, width, _ = imgContour.shape
            cv.drawContours(imgContour, [cnt], -1, (255, 0, 255), 7)
            epsilon = 0.03 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            num_vertices = len(approx)
            x, y, w, h = cv.boundingRect(approx)
            aspect_ratio = float(w) / h
            
            # Calculate rotation angle
            rect = cv.minAreaRect(cnt)
            _, _, rotation = rect
            rotation_angle = abs(rotation)

            if rotation_angle > 1 and num_vertices < 7:
                # Get the rotated bounding box
                box = cv.boxPoints(rect)
                box = np.intp(box)
                cnt_rotated = cv.boxPoints(rect)
                cnt_rotated = np.intp(cnt_rotated)
                # Get the rotation matrix for negative angle to rotate it back
                M = cv.getRotationMatrix2D(center, -rotation_angle, 1)
                # Apply the rotation to the contour points
                cnt_rotated = cv.transform(np.array([cnt_rotated]), M)[0]
                cnt_rotated = np.intp(cnt_rotated)
                # Compute the bounding box of the rotated contour
                x, y, w, h = cv.boundingRect(cnt_rotated)
    
                # Compute the width and height of the rotated square
                rotated_square_width = w
                rotated_square_height = h

                # Draw bounding rectangle
                cv.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Display shape information
                cv.putText(imgContour, f"Width: {pixels_to_cm(rotated_square_width)} cm", (x + w + 20, y + 60), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                cv.putText(imgContour, f"Height: {pixels_to_cm(rotated_square_height)} cm", (x + w + 20, y + 100), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                cv.putText(imgContour, f"Rotation about horizontal: {round(rotation_angle, 1)}", (x + w + 20, y + 140), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)

            # Draw bounding rectangle
            cv.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Display shape information
            shape_info = ""
            if num_vertices == 3:
                shape_info = "Triangle"
            elif num_vertices == 4:
                if aspect_ratio >= 0.95 and aspect_ratio <= 1.05:
                    shape_info = "Square"
                else:
                    shape_info = "Rectangle"
            elif num_vertices == 5:
                shape_info = "Pentagon"
            elif num_vertices == 6:
                shape_info = "Hexagon"
            else:
                shape_info = "Circle"
                cv.putText(imgContour, f"Radius: {pixels_to_cm(w)/2} cm", (x + w + 20, y + 60), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                cv.putText(imgContour, f"Center: {center[0] - origin[0], center[1] - origin[1]}", (x + w + 20, y + 100), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            if num_vertices < 7:
                if rotation_angle < 1:
                    cv.putText(imgContour, f"Width: {pixels_to_cm(w)} cm", (x + w + 20, y + 60), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                    cv.putText(imgContour, f"Height: {pixels_to_cm(h)} cm", (x + w + 20, y + 100), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                    cv.putText(imgContour, f"Center: {center[0] - origin[0], center[1] - origin[1]}", (x + w + 20, y + 140), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                    cv.putText(imgContour, f"Rotation about horizontal: {round(rotation_angle, 1)}", (x + w + 20, y + 180), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            cv.putText(imgContour, shape_info, (x + w + 20, y + 20), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)

# Main loop
while True:
    img = cv.imread("Roi_shapes2.png")  # Image original resolution is 2880 x 1920
    imgContour = img.copy()
    blurred = cv.GaussianBlur(imgContour, (7, 7), 1)
    gray = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
    threshold1 = cv.getTrackbarPos("threshold 1", "Parameters")
    threshold2 = cv.getTrackbarPos("threshold 2", "Parameters")
    threshold3 = cv.getTrackbarPos("threshold 3", "Parameters")
    threshold4 = cv.getTrackbarPos("threshold 4", "Parameters")
    thresh = cv.threshold(gray, threshold3, threshold4, cv.THRESH_BINARY)[1]
    canny = cv.Canny(gray, threshold1, threshold2)
    kernel = np.ones((3, 3))
    dilated = cv.dilate(canny, kernel, iterations=1)
    origin = getROI(thresh, imgContour)
    process_contours(dilated, imgContour)
    imgContour = imutils.resize(imgContour, width=1000)
    height, width, _ = imgContour.shape
    # Draw x-axis (horizontal line)
    x_axis_color = (0, 0, 255) # Red color
    cv.line(imgContour, (0, height - 50), (200, height - 50), x_axis_color, thickness=2)
    # Draw y-axis (vertical line)
    y_axis_color = (0, 0, 255)  # Red color
    cv.line(imgContour, (50, height), (50, height - 200), y_axis_color, thickness=2)
    cv.imshow("Image with contours", imgContour)
    thresh = imutils.resize(thresh, width=1000)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cv.destroyAllWindows()