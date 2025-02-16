import os
import json
from typing import Tuple, Optional
import cv2
import time
import depthai as dai
from pathlib import Path
import sys

# Add parent directory to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

from report.basic_pipeline import TrashAnalyzer
from report.report import ReportData
from dotenv import load_dotenv

class CameraCapture:
    def __init__(self, save_path: str = "captured_photos"):
        """Initialize camera capture with save directory."""
        self.save_path = save_path
        Path(save_path).mkdir(parents=True, exist_ok=True)
        self.pipeline = self._create_pipeline()

    def _create_pipeline(self) -> dai.Pipeline:
        """Create and configure the camera pipeline."""
        pipeline = dai.Pipeline()

        # Create camera node
        colorCam = pipeline.create(dai.node.ColorCamera)
        
        # Configure camera
        colorCam.setBoardSocket(dai.CameraBoardSocket.CAM_B)
        colorCam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_800_P)
        colorCam.setPreviewSize(640, 480)
        colorCam.setInterleaved(False)
        colorCam.setFps(30)

        # Create output
        xoutRgb = pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        colorCam.preview.link(xoutRgb.input)

        return pipeline

    def capture_before_after(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Capture before and after images using the OAK-D camera.
        Returns tuple of (before_image_path, after_image_path).
        """
        with dai.Device(self.pipeline) as device:
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            print("\nCapturing BEFORE image...")
            print("Press 'c' to capture the BEFORE image, 'q' to quit")
            
            before_path = None
            after_path = None
            
            # Capture before image
            while True:
                inRgb = qRgb.get()
                frame = inRgb.getCvFrame()
                
                cv2.imshow("Camera Feed", frame)
                key = cv2.waitKey(1)
                
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    return None, None
                elif key == ord('c'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    before_path = f"{self.save_path}/before_{timestamp}.jpg"
                    cv2.imwrite(before_path, frame)
                    print(f"Saved BEFORE image: {before_path}")
                    break
            
            print("\nCapturing AFTER image...")
            print("Press 'c' to capture the AFTER image, 'q' to quit")
            
            # Capture after image
            while True:
                inRgb = qRgb.get()
                frame = inRgb.getCvFrame()
                
                cv2.imshow("Camera Feed", frame)
                key = cv2.waitKey(1)
                
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    return None, None
                elif key == ord('c'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    after_path = f"{self.save_path}/after_{timestamp}.jpg"
                    cv2.imwrite(after_path, frame)
                    print(f"Saved AFTER image: {after_path}")
                    break
            
            cv2.destroyAllWindows()
            return before_path, after_path

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not openai_api_key or not perplexity_api_key:
        print("Error: Missing API keys in .env file")
        return
    
    # Initialize camera and analyzer
    camera = CameraCapture()
    analyzer = TrashAnalyzer(openai_api_key, perplexity_api_key)
    
    # Capture images
    before_path, after_path = camera.capture_before_after()
    
    if not before_path or not after_path:
        print("Image capture cancelled")
        return
    
    # Analyze the images
    print("\nAnalyzing images...")
    report_data = analyzer.analyze_trash(before_path, after_path)
    
    # Print results
    print("\nAnalysis Results:")
    print(f"Number of trash items: {report_data.numTrash}")
    print(f"Number of compost items: {report_data.numCompost}")
    print(f"Number of recycle items: {report_data.numRecycle}")
    print(f"Recyclable items: {', '.join(report_data.recycleNames)}")
    print(f"Compostable items: {', '.join(report_data.compostNames)}")
    print(f"CO2 impact from recycling: {report_data.recycleSavings:.3f} kg CO2e")
    print(f"CO2 impact from composting: {report_data.compostSavings:.3f} kg CO2e")

if __name__ == "__main__":
    main() 