import cv2 as cv
import numpy as np 
import imutils

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
            cv.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            epsilon = 0.03 * cv.arcLength(cnt, True)
            approx = cv.approxPolyDP(cnt, epsilon, True)
            num_vertices = len(approx)
            x, y, w, h = cv.boundingRect(approx)
            aspect_ratio = float(w) / h
            cv.rectangle(imgContour, (x , y), (x + w, y + h), (0, 255, 0), 2)
            
            # Calculate Fourier descriptors
            contour_complex = np.empty((cnt.shape[:-1]), dtype=complex)
            contour_complex.real = cnt[:, 0, 0].reshape((-1, 1))
            contour_complex.imag = cnt[:, 0, 1].reshape((-1, 1))
            fourier_result = np.fft.fft(contour_complex)
            descriptors = np.fft.fftshift(fourier_result)
            
            # Calculate rotation around x-axis
            phase = np.angle(descriptors)
            rotation_x = np.mean(phase[:, 0])  # Average rotation around x-axis
            
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
            if num_vertices < 7:
                cv.putText(imgContour, f"Width: {pixels_to_cm(w)} cm", (x + w + 20, y + 60), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                cv.putText(imgContour, f"Height: {pixels_to_cm(h)} cm", (x + w + 20, y + 100), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            cv.putText(imgContour, shape_info, (x + w + 20, y + 20), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            cv.putText(imgContour, f"Center: {center}", (x + w + 20, y + 140), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            cv.putText(imgContour, f"Rotation around X-axis: {round(rotation_x, 1)}", (x + w + 20, y + 180), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)


# Main loop
while True:
    img = cv.imread("Roi_shapes.jpg")  # Image original resolution is 2880 x 1920
    imgContour = img.copy()
    blurred = cv.GaussianBlur(imgContour, (7, 7), 1)
    gray = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
    threshold1 = cv.getTrackbarPos("threshold 1", "Parameters")
    threshold2 = cv.getTrackbarPos("threshold 2", "Parameters")
    threshold3 = cv.getTrackbarPos("threshold 3", "Parameters")
    threshold4 = cv.getTrackbarPos("threshold 4", "Parameters")
    thresh = cv.threshold(gray, threshold3, threshold4, cv.THRESH_BINARY)[1]
    canny = cv.Canny(gray, threshold1, threshold2)
    kernel = np.ones((5, 5))
    dilated = cv.dilate(canny, kernel, iterations=1)
    origin = getROI(thresh, imgContour)
    process_contours(dilated, imgContour)
    imgContour = imutils.resize(imgContour, width=1000)
    cv.imshow("Image with contours", imgContour)
    thresh = imutils.resize(thresh, width=1000)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cv.destroyAllWindows()



# Calculate rotation angle
            rect = cv.minAreaRect(cnt)
            _, _, rotation = rect
            rotation_angle = abs(rotation)
            
            # If rotation angle is significant, rotate the contour
            if rotation_angle > 1:  # Adjust the threshold as needed
                box = cv.boxPoints(rect)
                box = np.int0(box)
                cnt_rotated = cv.boxPoints(rect)
                cnt_rotated = np.int0(cnt_rotated)
                # Get the rotation matrix
                M = cv.getRotationMatrix2D(center, -rotation_angle, 1)
                # Apply the rotation to the contour points
                cnt_rotated = cv.transform(np.array([cnt_rotated]), M)[0]
                cnt_rotated = np.int0(cnt_rotated)
                cv.drawContours(imgContour,[cnt_rotated],0,(255,0,0),2)
                # Recalculate the bounding box
                x, y, w, h = cv.boundingRect(cnt_rotated)