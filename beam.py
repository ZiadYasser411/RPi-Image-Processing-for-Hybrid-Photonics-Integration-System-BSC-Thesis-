#####cinogy code
import xmlrpc.client
import time
import sys
import os

# please adjust the host name (/ IP address) and port number
proxy = xmlrpc.client.ServerProxy("http://localhost:8080/")
RayCi = proxy.RayCi

def selectCamera():
    IdDocLive = None
    
    # get list of all opened Live Modes
    LiveModeList = proxy.RayCi.LiveMode.list()
        
    # search for the first camera already connected to a Live Mode
    for LiveModeItem in LiveModeList:
        if (LiveModeItem['sName'] != 'not connected'):
            ConsideredTempCamera = proxy.RayCi.LiveMode.Camera.getIdCurrentCam(LiveModeItem['nIdDoc'])
            if ConsideredTempCamera['sName'] != 'Video Stream': # Live Mode must be connected to a real camera
                IdDocLive = LiveModeItem['nIdDoc']
                CameraItem = ConsideredTempCamera
                OpenedLiveMode = False # don't close it after usage
                break
        
    if IdDocLive == None: # if no running camera, that is already connected to a Live Mode, was found
        # get number of connected cameras  
        CameraCount = proxy.RayCi.LiveMode.Camera.getIdCamListSize()
        if CameraCount == 0:
            raise Exception('No camera found.')
        # open new Live Mode with the first available camera
        CameraItem = proxy.RayCi.LiveMode.Camera.getIdCamListItem(-1, 0)
        IdDocLive = proxy.RayCi.LiveMode.open(CameraItem['nIdCamHigh'], CameraItem['nIdCamLow'])
        print('Opened new Live Mode')
        OpenedLiveMode = True # close after usage
    print('Using camera', CameraItem['sName'])
    print(proxy.RayCi.LiveMode.isConnected)
    
    # Add video measurement functionality here
    # Create a new video measurement within the selected Live Mode document
    videoDocId = proxy.RayCi.LiveMode.Measurement.newVideo(IdDocLive)

    # Set the video codec to be used (e.g., "LAGS"). Ensure the codec is installed on the host.
    print("Recording video for 20 seconds...")
    proxy.RayCi.Video.Recording.Settings.setCodec(videoDocId, "LAGS")
    
    print("Recording video for 20 seconds... done")
    proxy.RayCi.Video.Recording.Settings.setFreeRunning(videoDocId)
    
    # Start video recording
    proxy.RayCi.Video.Recording.start(videoDocId)

    # Wait for the specified duration

    proxy.RayCi.LiveMode.Settings.Lut.load(IdDocLive, "jet")
    # Alternative: Load a custom LUT from a file path
    # proxy.RayCi.LiveMode.Settings.Lut.load(docId, "C:\\MyCustomLut.lut")

    # Set the threshold values to change the base LUT -> actual LUT mapping range
    proxy.RayCi.LiveMode.Settings.Lut.setThreshold(IdDocLive, 0.0, 0.5)

    # Enable the “auto contrast” option to provide a high contrast inside the AOI
    proxy.RayCi.LiveMode.Settings.Lut.setAutoContrast(IdDocLive, True)  # Modifying LUT parameters and displaying colors
    # Query the actual LUT
    width = RayCi.LiveMode.Data.getSizeX(IdDocLive)
    height = RayCi.LiveMode.Data.getSizeY(IdDocLive)
    data = RayCi.LiveMode.Data.getPreview(IdDocLive)
    
    # unformattedLut = RayCi.LiveMode.Settings.Lut.getActualLut(IdDocLive, 8)
    # lut = byteArrayToUnsignedInt32Array(unformattedLut)

    # # Iterate over each pixel and display the corresponding RGB tuple
    # for y in range(height):
    #     for x in range(width):
    #         # Check the type of data and handle it accordingly
    #         if isinstance(data, xmlrpc.client.Binary):
    #             # Extract bytes from the Binary object
    #             data_bytes = data.data
    #             # Use the extracted bytes to index the lut
    #             argb = lut[data_bytes[y * width + x]]
    #         else:
    #             # Use data directly
    #             argb = lut[data[y * width + x]]
                
    #         # Extract R, G, and B values from the tuple
    #         red = (argb >> 16) & 0xFF
    #         green = (argb >> 8) & 0xFF
    #         blue = (argb >> 0) & 0xFF
    #         # Display the RGB values
    #         print(f"RGB of pixel @ pos ({x}, {y}) is ({red}, {green}, {blue})")
    # Stop video recording
    print("Recording video for 20 seconds...")
    time.sleep(5)  # Assuming the measurement lasts for 20 seconds
    print("Recording video for 20 seconds...done")
    proxy.RayCi.Video.Recording.stop(videoDocId)
    save_path = "S:\\GUC\\Bachelor\\python\\MyRecordedVideo.avi"
    proxy.RayCi.Video.saveAs(videoDocId, save_path)

    return (IdDocLive, OpenedLiveMode)

def byteArrayToUnsignedInt32Array(byte_array):
    # Convert Binary object to bytes
    byte_array_bytes = byte_array.data

    # Check if the length of byte_array is divisible by 4
    if len(byte_array_bytes) % 4 != 0:
        raise ValueError("Byte array length must be divisible by 4")

    # Create an array to hold the unsigned 32-bit integers
    uint32_array = []

    # Iterate over the byte array, converting every 4 bytes to an unsigned 32-bit integer
    for i in range(0, len(byte_array_bytes), 4):
        uint32 = int.from_bytes(byte_array_bytes[i:i+4], byteorder='little', signed=False)
        uint32_array.append(uint32)
# Assuming byte_array is the variable you want to get the type of
    print(type(uint32_array))

    return uint32_array


def configureCamera( IdDocLive, Wavelength_nm ):
    # define wavelength
    RayCi.LiveMode.Header.Laser.setWaveLength(IdDocLive, float(Wavelength_nm))
    # configure units
    RayCi.LiveMode.Settings.Units.Spatial.setUnit(IdDocLive, 'mm')
    # set 2nd moments as beam width method
    RayCi.LiveMode.Analysis.Settings.setMethod(IdDocLive, 2)

def backgroundCalibration( IdDocLive ):
    # configure background calibration, average over 16 frames
    RayCi.LiveMode.Background.Recording.Settings.setFrameSpan(IdDocLive, 16)
    RayCi.LiveMode.Background.Recording.Settings.setAllExposure(IdDocLive)
    # start calibration
    RayCi.LiveMode.Background.Recording.start(IdDocLive)
    # wait until calibration is done
    print('Background calibration started, please wait', end='', flush=True)
    time.sleep(0.1)
    while RayCi.LiveMode.Background.Recording.isRecording(IdDocLive):
        print('.', sep='', end='', flush=True)
        time.sleep(0.2)
    print()
    print('Finished background calibration')

def performMeasurement( IdDocLive, LaserSNo ):
    # configure Area of Interest
    RayCi.LiveMode.AOI.Adjustment.setActive(IdDocLive, True)
    # open a new single measurement
    IdDocSingle = RayCi.LiveMode.Measurement.newSingle(IdDocLive)
    # configure single measurement
    RayCi.Single.Header.Laser.setSerial(IdDocSingle, str(LaserSNo))
    # configure measurement process, average over 8 frames
    RayCi.Single.Recording.Settings.setSingleShot(IdDocSingle, False)
    RayCi.Single.Recording.Settings.setFrameSpan(IdDocSingle, 8)
    RayCi.Single.Recording.Settings.setMedian(IdDocSingle, True)
    # start measurement
    RayCi.Single.Recording.start(IdDocSingle)
    # wait until measurement is finished
    print('Measurement started, please wait', end='', flush=True)
    time.sleep(0.1)
    while RayCi.Single.Recording.isRecording(IdDocSingle):
        print('.', sep='', end='', flush=True)
        time.sleep(0.2)
    print()
    print('Finished measurement')
    return IdDocSingle

def evaluateFWHM( IdDocSingle, IdCrossSect ):
    # adjust to the center of beam, if possible
    RayCi.Single.CrossSection.adjust(IdDocSingle, IdCrossSect, 1)
    # configure first cursor pair for FWHM = 50%
    RayCi.Single.CrossSection.Cursor.Settings.setBeamWidthRatio(IdDocSingle, IdCrossSect, 0, 50.0)
    # read distance
    return RayCi.Single.CrossSection.Cursor.getDistance(IdDocSingle, IdCrossSect, 0)

def evaluateFWHM_xy( IdDocSingle ):
    IdCrossSectX=0
    IdCrossSectY=1
    SizeX = RayCi.Single.Data.getSizeX()
    SizeY = RayCi.Single.Data.getSizeY()
    # open cross section throw the center of image
    RayCi.Single.CrossSection.Settings.setX_px(IdDocSingle, IdCrossSectX, int(SizeY/2))
    RayCi.Single.CrossSection.Settings.setY_px(IdDocSingle, IdCrossSectY, int(SizeX/2))
    # evaluate FWHM
    FWHM_x = evaluateFWHM(IdDocSingle, IdCrossSectX)
    FWHM_y = evaluateFWHM(IdDocSingle, IdCrossSectY)
    Unit = RayCi.Single.CrossSection.Cursor.getUnit(IdDocSingle, IdCrossSectY)
    return (FWHM_x, FWHM_y, Unit)

def evaluate2ndMoments_xy(IdDocSingle ):
        Center_x = RayCi.Single.Analysis.SecondMoments.Centroid.getX(IdDocSingle)
        Center_y = RayCi.Single.Analysis.SecondMoments.Centroid.getY(IdDocSingle)
        Width_x = RayCi.Single.Analysis.SecondMoments.WidthLab.getX(IdDocSingle)
        Width_y = RayCi.Single.Analysis.SecondMoments.WidthLab.getY(IdDocSingle)
        Unit = RayCi.Single.Analysis.SecondMoments.WidthLab.getUnit(IdDocSingle)
        return (Center_x, Center_y, Width_x, Width_y, Unit)

def saveMeasurement( IdDocSingle, PathName ):
    base_file, ext = os.path.splitext(PathName)
    RayCi.Single.saveAs(IdDocSingle, base_file+'.tif', True)
    RayCi.Single.Data.exportAsCsv(IdDocSingle, base_file+'.csv', ',', True)

def main():
    print("Welcome to CINOGY's Python example")
    print()
    a=input("Start RayCi and press ENTER to continue...")
    (IdDocLive, OpenedLiveMode) = selectCamera()
    print();
    wl=input("Enter the wavelength [nm]: ")
    configureCamera(IdDocLive, wl)
    print()
    print("Block the beam (switch off the laser) to perform the background calibration.")
    a=input("Press ENTER if you are ready...")
    backgroundCalibration(IdDocLive)
    print()
    print("Switch on the beam to perform a measurement.")
    a=input("Press ENTER if you are ready...")
    NextRun=True
    while NextRun:
        try:
            print()
            sno=input("Enter laser serial number: ")
            IdDocSingle = performMeasurement(IdDocLive, sno)
            print("Evaluate measurement")
            # are any data available ?
            if RayCi.Single.isValid(IdDocSingle):
                # do we have any signal ?
                if RayCi.Single.Analysis.Statistic.Peak.isValid(IdDocSingle):
                    try:
                        Center_x, Center_y, Width_x, Width_y, Width_Unit = evaluate2ndMoments_xy(IdDocSingle)
                        print()
                        print("2nd Moments:")
                        print("Center x: ", Center_x, Width_Unit)
                        print("Center y: ", Center_y, Width_Unit)
                        print("Width  x: ", Width_x, Width_Unit)
                        print("Width  y: ", Width_y, Width_Unit)
                    except Exception as inst:
                        print(inst)                                                
                    try:
                        FWHM_x, FWHM_y, FWHM_Unit = evaluateFWHM_xy(IdDocSingle)
                        print()
                        print("FWHM   x: ", FWHM_x, FWHM_Unit)
                        print("FWHM   y: ", FWHM_y, FWHM_Unit)
                    except Exception as inst:
                        print(inst)
                    try:
                        print()
                        pathName = input("Enter save path for measurement file: ")
                        saveMeasurement(IdDocSingle, pathName)
                    except Exception as inst:
                        print(inst)
                else:
                    print("No signal")
            else:
                print("Invalid data")
            RayCi.Single.close(IdDocSingle)
        except Exception as inst:
            print(inst)
        print()
        print("Press")
        print("1: Perform the next measurement")
        print("0: Exit")
        InvalidAnswer = True
        while InvalidAnswer:
            ans = input()
            if ans=='1':
                InvalidAnswer=False
                NextRun=True
            elif ans=='0':
                InvalidAnswer=False
                NextRun=False
    
    if OpenedLiveMode:
        RayCi.LiveMode.close(IdDocLive);


if __name__ == "__main__":
    sys.exit(main())