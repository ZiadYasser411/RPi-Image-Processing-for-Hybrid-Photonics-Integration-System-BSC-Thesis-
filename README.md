# 📷 RPi Image Processing for Hybrid Photonics Integration System

This repository contains the implementation of a computer vision system for automated optical alignment in hybrid photonics integration, using Raspberry Pi 5 and deep learning. It is based on the Bachelor’s Thesis submitted by Ziad Yasser Fawzi Gafar to the German University in Cairo.

---

## 🎯 Project Summary

The project is part of a broader initiative to develop an AI-assisted Automated Optical Alignment System (AIOAS) that enhances alignment accuracy in hybrid photonic integration systems. It combines embedded hardware, computer vision, and deep learning techniques to align a laser source with a photonic chip.

---

## 🛠️ Technologies Used

- Python 3.11.2  
- Raspberry Pi 5 (64-bit Raspbian OS)  
- Basler ACE 2 R Camera (a2A2600-64umPRO)  
- OpenCV 4.7.0  
- PyPylon  
- Ultralytics YOLOv8  
- ONNX Runtime

---

## 🚀 System Capabilities

- Real-time object detection of photonic chips and laser modules  
- Measurement of misalignment in microns  
- Visualization with bounding boxes and rotation angle  
- Optimized inference using ONNX format  
- System supports ~30 µm/pixel resolution via calibration

---

## 🧪 Software Setup

### Clone the Repository

    git clone https://github.com/ZiadYasser411/RPi-Image-Processing-for-Hybrid-Photonics-Integration-System-BSC-Thesis-.git
    cd RPi-Image-Processing-for-Hybrid-Photonics-Integration-System-BSC-Thesis-

### Install Requirements

    pip install -r requirements.txt

### Dependencies

- opencv-python  
- numpy  
- onnxruntime  
- ultralytics  
- pypylon

---

## 🧠 Model Training Process

### 1. Data Collection

- ~500 high-resolution images captured using the Basler ACE 2 R camera  
- Images include multiple positions and orientations of the chip and laser  
- Exposure settings adjusted for image consistency  

### 2. Annotation

- Labeled using [Roboflow](https://roboflow.com) with two classes:
  - `chip`
  - `laser`
- Over 500 images annotated and labeled manually  
- Data augmentation: brightness, rotation, flipping  

### 3. Model Training

- YOLOv8 pre-trained base model used for transfer learning  
- Training performed on Roboflow-exported YOLOv8 dataset  
- Training configuration:
  - Image size: 640x640  
  - Optimizer: Adam  
  - Loss: box, class, confidence  

### 4. Performance Metrics

- mAP@0.5: 0.995  
- 100% accuracy on confusion matrix  
- Smooth loss convergence  
- Overfitting avoided via data augmentation  

### 5. Model Optimization

- Exported to ONNX format:

        yolo export model=best.pt format=onnx

- Inference time reduced from ~1800 ms to ~600 ms on CPU  
- YOLOv8-OBB model reached ~250 ms with orientation tracking  

---

## ⚙️ Runtime Pipeline

1. Initialize camera via PyPylon  
2. Capture live frames and convert to BGR8  
3. Run YOLOv8 ONNX model for detection  
4. Parse bounding boxes for chip and laser  
5. Compute micrometer displacement  
6. Visualize detection with bounding boxes, labels, rotation angle, and micron offset  

---

## 🧪 Image Processing Techniques (Exploratory)

Before moving to deep learning, several classical techniques were evaluated:

- Canny Edge Detection  
- Shape detection with contours and area filtering  
- Region of Interest (ROI) detection (used for testing only)  
- Manual calibration using fiber optic cable (125 µm core measured as ~6 pixels)  

Final calibration settled on **30 µm/pixel** for measurement.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👤 Author

**Ziad Yasser Fawzi Gafar**  
Bachelor Thesis – Media Engineering and Technology Faculty  
German University in Cairo  

**Supervisor:** Dr. Haitham Abdelsalam Ahmed Omran  
📅 Submitted: May 19, 2024

---

## 📬 Contact

📧 Email: ziadyasser4111@gmail.com  
