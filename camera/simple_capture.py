from pathlib import Path
import cv2
import time
import depthai as dai
import numpy as np

def capture_photos(save_path: str = "captured_photos"):
    """
    Capture photos from OAK-D camera and save them to the specified directory.
    
    Args:
        save_path (str): Directory where photos will be saved
    """
    # Ensure save directory exists
    Path(save_path).mkdir(parents=True, exist_ok=True)
    
    # Create pipeline
    pipeline = dai.Pipeline()

    # Create camera node
    colorCam = pipeline.create(dai.node.ColorCamera)

    # Configure ColorCamera node
    colorCam.setBoardSocket(dai.CameraBoardSocket.CAM_B)
    colorCam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_800_P)
    colorCam.setPreviewSize(640, 480)
    colorCam.setInterleaved(False)
    colorCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)  # Explicitly set BGR color order
    colorCam.setFps(30)

    # Create XLinkOut node
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    xoutRgb.setStreamName("rgb")

    # Link the nodes
    colorCam.preview.link(xoutRgb.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        # Output queue
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        print("Camera ready! Press 'c' to capture, 'q' to quit")
        
        frame_count = 0
        while True:
            inRgb = qRgb.get()

            # Get the frame
            frame = inRgb.getCvFrame()
            
            # Show the frame
            cv2.imshow("RGB", frame)

            # Handle key presses
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == ord('c'):
                # Save RGB image
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                rgb_filename = f"{save_path}/rgb_{timestamp}_{frame_count}.jpg"
                
                cv2.imwrite(rgb_filename, frame)
                
                print(f"Saved image: \n{rgb_filename}")
                frame_count += 1

        cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_photos()