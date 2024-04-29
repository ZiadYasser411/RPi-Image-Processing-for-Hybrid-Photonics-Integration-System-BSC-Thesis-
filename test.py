import cv2

def define_roi(x1, y1, x2, y2, frame):
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw blue rectangle

#Read video
vid = cv2.VideoCapture('Road.mp4')

#ROI coordinates
x1 = 120
y1 = 150
x2 = 240
y2 = 250

while True:
    ret, frame = vid.read()

    if not ret:
        print("Error reading frame from video. Exiting.")
        break
    
    #ROI Window Frame
    ROI_frame = frame[y1:y2, x1:x2]
    #Canny edge detection
    canny = cv2.Canny(ROI_frame, threshold1=220, threshold2=260)
    #Showing Frames of ROI and Canny-applied ROI
    cv2.imshow("ROI", ROI_frame)
    cv2.imshow("Canny ROI", canny)
    # Define and visualize ROI
    define_roi(x1, y1, x2, y2, frame)
    # Display Original video with ROI rectangle
    cv2.imshow("Frame", frame)
    cv2.moveWindow("Frame", 100, 100)
    cv2.moveWindow("ROI", 100, 500)
    cv2.moveWindow("Canny ROI", 220, 500)
    # Exit on 'Esc' press
    if cv2.waitKey(20) & 0xFF == 27:
        break

# Release resources
vid.release()
cv2.destroyAllWindows()