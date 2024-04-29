from pypylon import pylon
import cv2 as cv
import numpy as np
import imutils
import os

def pixels_to_microns(pixels):
    microns_per_pixel = 125 / 6  # 125 microns for every 6 pixels
    microns = pixels * microns_per_pixel
    return microns

def process_image(image, threshold1, threshold2, threshold3, threshold4):
    # For example:
    blurred = cv.GaussianBlur(image, (9, 9), 1)
    gray = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
    canny = cv.Canny(gray, threshold1, threshold2)
    kernel = np.ones((5, 5))
    dilated = cv.dilate(canny, kernel, iterations=1)
    thresh = cv.threshold(gray, threshold3, threshold4, cv.THRESH_BINARY)[1]
    return dilated, thresh

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
            #cv.drawContours(imgContour, [cnt], -1, (255, 0, 255), 7)
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
                cv.putText(imgContour, f"Rotation about horizontal: {round(rotation_angle, 1)}", (x + w + 20, y + 180), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            # Draw bounding rectangle
            cv.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Display shape information
            shape_info = ""
            if aspect_ratio >= 0.95 and aspect_ratio <= 1.05:
                shape_info = "Square"
                cv.putText(imgContour, f"Width: {pixels_to_microns(w)} microns", (x + w + 20, y + 60), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 1)

            else:
                shape_info = "Rectangle"
                cv.putText(imgContour, f"Width: {pixels_to_microns(w)} microns", (x + w + 20, y + 110), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 1)
            cv.putText(imgContour, shape_info, (x + w + 20, y + 50), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 1)

def configure_camera(camera):
    # Set pixel format to BGR
    camera.PixelFormat.SetValue('BGR8')

def set_exposure(camera, exposure_value):
    # Set exposure value in microseconds
    camera.ExposureTime.SetValue(exposure_value)

def capture_video_with_display():
    # Create an instant camera object
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    try:
        # Open the camera
        camera.Open()
        # Configure camera settings
        configure_camera(camera)
        # Set exposure to 10000 microseconds
        set_exposure(camera, 10000)
        # Start grabbing images continuously
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        fps = 60
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        # Create trackbars for threshold values
        cv.namedWindow("Parameters")
        cv.createTrackbar("Threshold 1", "Parameters", 54, 255, lambda x: None)
        cv.createTrackbar("Threshold 2", "Parameters", 54, 255, lambda x: None)
        cv.createTrackbar("Shapes area", "Parameters", 2000, 500000, lambda x: None)
        cv.createTrackbar("Threshold 3", "Parameters", 101, 255, lambda x: None)
        cv.createTrackbar("Threshold 4", "Parameters", 255, 255, lambda x: None)
        cv.createTrackbar("ROI Area", "Parameters", 431000, 500000, lambda x: None)
        cv.resizeWindow("Parameters", 600, 600)
        # Create a loop to continuously grab frames, display them, and process them
        while camera.IsGrabbing():
            # Read the current threshold values
            threshold1 = cv.getTrackbarPos("Threshold 1", "Parameters")
            threshold2 = cv.getTrackbarPos("Threshold 2", "Parameters")
            threshold3 = cv.getTrackbarPos("Threshold 3", "Parameters")
            threshold4 = cv.getTrackbarPos("Threshold 4", "Parameters")
            # Wait for an image to be grabbed
            grab_result = camera.RetrieveResult(10000, pylon.TimeoutHandling_ThrowException)
            # Access the image data
            image = grab_result.Array
            # Process the image with the current threshold values
            dilated, thresh = process_image(image, threshold1, threshold2, threshold3, threshold4)
            #origin = getROI(thresh, image)
            process_contours(thresh, image)
            # Display the original and processed frames
            image = cv.resize(image, (950, 750))  # Resize the original frame
            dilated = cv.resize(dilated, (950, 750))
            thresh = cv.resize(thresh, (950, 750))
            cv.imshow("Original Frame", image)
            cv.imshow("Thresh Frame", thresh)
            key = cv.waitKey(1)
            if key == ord('q'):  # Press 'q' to exit
                break
            # Release the grab result
            grab_result.Release()

    finally:
        # Stop grabbing and close the camera
        camera.StopGrabbing()
        camera.Close()
        cv.destroyAllWindows()

if __name__ == "__main__":
    capture_video_with_display()
