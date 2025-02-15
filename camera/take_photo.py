from pathlib import Path
import cv2
import time
import depthai as dai
# import argparse
import json
import numpy as np

W, H = 640, 480  # Default resolution

# Create pipeline
pipeline = dai.Pipeline()
# Create camera nodes
colorLeft = pipeline.create(dai.node.ColorCamera)
colorRight = pipeline.create(dai.node.ColorCamera)
spatialDetectionNetwork = pipeline.create(dai.node.YoloSpatialDetectionNetwork)

# Configure ColorCamera nodes
colorLeft.setBoardSocket(dai.CameraBoardSocket.CAM_B)
colorLeft.setResolution(dai.ColorCameraProperties.SensorResolution.THE_800_P)
colorLeft.setVideoSize(W, H)
colorLeft.setPreviewSize(640, 480)
colorLeft.setInterleaved(False)
colorLeft.setFps(30)

colorRight.setBoardSocket(dai.CameraBoardSocket.CAM_C)
colorRight.setResolution(dai.ColorCameraProperties.SensorResolution.THE_800_P)
colorRight.setVideoSize(W, H)
colorRight.setPreviewSize(640, 480)
colorRight.setInterleaved(False)
colorRight.setFps(30)

# Create the StereoDepth node
stereo = pipeline.create(dai.node.StereoDepth)
stereo.setDepthAlign(dai.CameraBoardSocket.CAM_B)  # Align depth to the LEFT camera socket
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
stereo.setOutputSize(W, H)
stereo.setLeftRightCheck(True)
stereo.setSubpixel(True)

# Link cameras to StereoDepth
colorLeft.video.link(stereo.left)
colorRight.video.link(stereo.right)

spatialDetectionNetwork.setNumInferenceThreads(2)
spatialDetectionNetwork.input.setBlocking(False)

# Create XLinkOut nodes
xoutRgb = pipeline.create(dai.node.XLinkOut)
xoutRgb.setStreamName("rgb")

nnOut = pipeline.create(dai.node.XLinkOut)
nnOut.setStreamName("nn")

xoutBoundingBoxDepthMapping = pipeline.create(dai.node.XLinkOut)
xoutBoundingBoxDepthMapping.setStreamName("boundingBoxDepthMapping")

xoutDepth = pipeline.create(dai.node.XLinkOut)
xoutDepth.setStreamName("depth")

# Link the nodes
spatialDetectionNetwork.passthrough.link(xoutRgb.input)
spatialDetectionNetwork.out.link(nnOut.input)
spatialDetectionNetwork.boundingBoxMapping.link(xoutBoundingBoxDepthMapping.input)
stereo.depth.link(spatialDetectionNetwork.inputDepth)
spatialDetectionNetwork.passthroughDepth.link(xoutDepth.input)

colorLeft.preview.link(spatialDetectionNetwork.input)


# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    # Output queues to get rgb frames, nn data, and depth
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)
    xoutBoundingBoxDepthMappingQueue = device.getOutputQueue(name="boundingBoxDepthMapping", maxSize=4, blocking=False)
    depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)


    startTime = time.monotonic()
    counter = 0
    fps = 0
    color = (255, 255, 255)
    detection_count = 0
    detection_collection = []
    pick = True
    column = 0
    
    while True:                    
        inRgb = qRgb.get()
        inDet = qDet.get()
        depth = depthQueue.get()

        frame = inRgb.getCvFrame()
        depthFrame = depth.getFrame()
        
        depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
        depthFrameColor = cv2.equalizeHist(depthFrameColor)
        depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_OCEAN)

        counter += 1
        current_time = time.monotonic()
        if (current_time - startTime) > 1 :
            fps = counter / (current_time - startTime)
            counter = 0
            startTime = current_time

        detections = inDet.detections
        if len(detections) != 0:
            boundingBoxMapping = xoutBoundingBoxDepthMappingQueue.get()
            roiDatas = boundingBoxMapping.getConfigData()

            for roiData in roiDatas:
                roi = roiData.roi.denormalize(depthFrame.shape[1], depthFrame.shape[0])
                topLeft = roi.topLeft()
                bottomRight = roi.bottomRight()

                xmin = int(topLeft.x)
                ymin = int(topLeft.y)
                xmax = int(bottomRight.x)
                ymax = int(bottomRight.y)

                cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)

        # Display the frame
        height = frame.shape[0]
        width  = frame.shape[1]
        for detection in detections:
            if detection.confidence < 0.7:
                continue
            
            label = labels[detection.label]
            print(label)
            
            if str(label) == "Planting pod":
                pick = True
            else:
                pick = False
                
            detection_count += 1
            # Denormalize bounding box
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)
            cv2.putText(frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 0)
            cv2.putText(frame, "{:.2f}".format(detection.confidence*100), (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            cv2.putText(frame, f"X: {int(detection.spatialCoordinates.x)} mm", (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            cv2.putText(frame, f"Y: {int(detection.spatialCoordinates.y)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            cv2.putText(frame, f"Z: {int(detection.spatialCoordinates.z)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

            print("Confidence: ", detection.confidence * 100, "%")
            # print("minX: ",detection.xmin, "minY: ",detection.ymin, "maxX: ",detection.xmax, "maxY: ",detection.ymax)
            print("X: ",detection.spatialCoordinates.x, "mm", "Y: ",detection.spatialCoordinates.y, "mm", "Z: ",detection.spatialCoordinates.z, "mm")
            
            detection_collection.append([detection.spatialCoordinates.x, detection.spatialCoordinates.y, detection.spatialCoordinates.z])
        
        cv2.putText(frame, "NN fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)
        cv2.imshow("depth", depthFrameColor)
        cv2.imshow("rgb", frame)

        if cv2.waitKey(1) == ord('q'):
            break