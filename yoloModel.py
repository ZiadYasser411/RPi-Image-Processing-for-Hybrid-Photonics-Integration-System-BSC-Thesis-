from roboflow import Roboflow

rf = Roboflow(api_key="RooIvrhbvkTyoMZab5No")
project = rf.workspace("ziads-workspace").project("chip-detection-bljtf")
version = project.version(2)
dataset = version.download("yolov8")
