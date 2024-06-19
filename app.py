import cv2 as cv
import numpy as np
from ultralytics import YOLO
from pypylon import pylon
from ultralytics.utils.plotting import Annotator
import torch
import math

# Function to convert pixels to microns for calibration
def pixels_to_microns(pixels):
    return math.ceil((pixels * 75.15218318) // 10) * 10

# Function to configure the camera settings
def configure_camera(camera):
    # Set pixel format to BGR
    camera.PixelFormat.SetValue('BGR8')

# Function to set the exposure value of the camera
def set_exposure(camera, exposure_value):
    # Set exposure value in microseconds
    camera.ExposureTime.SetValue(exposure_value)

# Define colors for different classes (chip: blue, laser: red)
class_colors = {
    "Chip": (255, 0, 0),  # Blue
    "Laser": (0, 0, 255)  # Red
}

# Function to load the YOLO model
def load_yolo_model(model_path):
    return YOLO(model_path)

# Function to perform inference using the YOLO model
def perform_inference(model, image):
    results = model.predict(image)
    if results and len(results) > 0:
        return results[0]
    return None

# Function to process the results from the YOLO model
def process_results(result, annotator):
    chip_center_x = None  # Initialize variable to store chip center x-coordinate
    chip_center_y = None  # Initialize variable to store chip center y-coordinate
    laser_center_x = None  # Initialize variable to store laser center x-coordinate
    laser_center_y = None  # Initialize variable to store laser center y-coordinate

    # Check if the result has 'obb' attribute and it contains bounding box coordinates
    if hasattr(result, 'obb') and result.obb.xyxyxyxy is not None:
        obb_data = result.obb  # Get the oriented bounding box data
        xyxyxyxy = obb_data.xyxyxyxy.cpu().numpy()  # Convert bounding box coordinates to numpy array
        confidences = obb_data.conf.cpu().numpy()  # Convert confidence scores to numpy array
        class_ids = obb_data.cls.cpu().numpy()  # Convert class IDs to numpy array
        angles = obb_data.xywhr.cpu().numpy()[:, 4]  # Extract the rotation angles

        # Loop through each bounding box
        for i in range(len(xyxyxyxy)):
            box_points = xyxyxyxy[i].reshape((4, 2))  # Reshape bounding box points

            # Calculate minimum and maximum x and y coordinates of the bounding box
            x_min = np.min(box_points[:, 0])
            y_min = np.min(box_points[:, 1])
            x_max = np.max(box_points[:, 0])
            y_max = np.max(box_points[:, 1])

            conf = confidences[i]  # Get confidence score for the bounding box
            class_id = class_ids[i]  # Get class ID for the bounding box
            angle = angles[i]  # Get rotation angle for the bounding box
            class_name = result.names[class_id]  # Get class name using class ID
            color = class_colors.get(class_name, (0, 255, 0))  # Get color for the class, default to green if not found
            width_pixels = x_max - x_min  # Calculate width of the bounding box in pixels
            height_pixels = y_max - y_min  # Calculate height of the bounding box in pixels

            # Convert width and height from pixels to microns
            width_microns = pixels_to_microns(width_pixels)
            height_microns = pixels_to_microns(height_pixels)

            # Process Chip class
            if class_name == "Chip":
                # Calculate center of the chip in microns
                chip_center_x = pixels_to_microns((x_min + x_max) // 2)
                chip_center_y = pixels_to_microns((y_min + y_max) / 2)
                chipy = (y_min + y_max) / 2  # Calculate center y-coordinate in pixels
                # Create label for chip
                label = f"{class_name} {conf:.2f} A:{angle:.3f} W:{width_microns} H:{height_microns}"
            # Process Laser class
            else:
                # Calculate center of the laser in microns
                laser_center_x = pixels_to_microns((x_min + x_max) // 2)
                laser_center_y = pixels_to_microns(728)
                lasery = 728  # Fixed center y-coordinate for the laser
                # Create label for laser
                label = f"{class_name} {conf:.2f}"

            # Draw bounding box and label with corresponding color
            annotator.box_label([x_min, y_min, x_max, y_max], label, color=color)

        # Print the centers of the chip and laser
        if chip_center_x is not None and chip_center_y is not None:
            print(f"Chip Center: X={chip_center_x}, Y={chip_center_y}")
        if laser_center_x is not None and laser_center_y is not None:
            print(f"Laser Center: X={laser_center_x}, Y={laser_center_y}")

        # Check alignment of chip and laser centers
        if chip_center_y is not None and laser_center_y is not None:  # Check if chip and laser centers are detected
            if abs(chip_center_y - laser_center_y) <= 20:  # Margin of error is 20 microns
                align_message = "Aligned"  # Print aligned on screen
                box_color = (0, 255, 0)  # Green color for aligned
            else:
                # Print not aligned and show how many microns to move in y-axis
                align_message = f"Not Aligned, move the chip {(chip_center_y - laser_center_y)} microns in y-axis"
                box_color = (0, 0, 255)  # Red color for not aligned
            # Draw rectangle behind the text
            if align_message == "Aligned":
                cv.rectangle(annotator.im, (10, 10), (210, 60), box_color, -1)  # Filled rectangle
            else:
                cv.rectangle(annotator.im, (10, 10), (880, 60), box_color, -1)
            # Add aligned or not aligned text
            cv.putText(annotator.im, align_message, (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        print("No OBB data found in the results.")

# Function to capture video, run inference, and display results
def capture_video_with_display(model_path):
    model = load_yolo_model(model_path)
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
        # Create a loop to continuously grab frames, display them, and process them
        while camera.IsGrabbing():
            # Wait for an image to be grabbed
            grab_result = camera.RetrieveResult(10000, pylon.TimeoutHandling_ThrowException)
            # Access the image data
            image = grab_result.Array
            # Resize image for display
            display_image = cv.resize(image, (image.shape[1] // 2, image.shape[0] // 2))
            # Run detection
            img = torch.from_numpy(image).permute(2, 0, 1).float()  # Convert BGR to RGB and from HWC to CHW
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)
            result = perform_inference(model, display_image)
            if result is not None:
                annotator = Annotator(display_image)
                process_results(result, annotator)
                # Show annotated image
                cv.imshow("YOLO", annotator.im)
            else:
                cv.imshow("YOLO", display_image)
            
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
    model_path = 'C:/Users/ziady/OneDrive/Desktop/Edge_detection/YOLOv8OBB/runs/obb/train3/weights/best.onnx'
    capture_video_with_display(model_path)