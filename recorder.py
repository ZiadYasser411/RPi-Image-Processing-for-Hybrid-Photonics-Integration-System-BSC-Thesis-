from pypylon import pylon
import cv2

def main():
  # Connect to the first available camera
  camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

  # Set camera parameters
  camera.Open()
  camera.PixelFormat.SetValue('BGR8')
  camera.ExposureTime.SetValue(10000)  # in microseconds

  # Create and configure the grab result writer
  converter = pylon.ImageFormatConverter()
  converter.OutputPixelFormat = pylon.PixelType_BGR8packed

  # Start the grabbing of images
  camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

  # Define the path to save images (modify "path/to/images" as needed)
  image_path = r"C:/Users/ziady/OneDrive/Desktop/Edge_detection/Dataset_images"

  # Define image counter
  image_count = 0

  # Retrieve and process images
  while camera.IsGrabbing():
    # Wait for an image and retrieve it
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grab_result.GrabSucceeded():
      # Convert the grabbed image to BGR8 format
      image = converter.Convert(grab_result)
      img = image.GetArray()

      # Resize the image to half of its original size (optional)
      # resized_img = cv2.resize(img, None, fx=0.5, fy=0.5)

      # Save the image with a sequential filename within the path
      filename = f"{image_path}/image_{image_count:04d}.jpg"
      cv2.imwrite(filename, img)

      # Increment image counter
      image_count += 1

      # Optional: Display the frame (might slow down capture)
      # cv2.imshow('Frame', img)
      # if cv2.waitKey(1) & 0xFF == ord('q'):
      #   break

    grab_result.Release()

  # Release the camera
  camera.StopGrabbing()
  camera.Close()

if __name__ == "__main__":
  main()
