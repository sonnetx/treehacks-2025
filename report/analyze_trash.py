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

from basic_pipeline import TrashAnalyzer
from report import ReportData
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
         

    def capture_image(self) -> Optional[str]:
        """
        Captures an image from the OAK-D camera instantly and saves it as 'after_TIMESTAMP.jpg'.
        """
        with dai.Device(self.pipeline) as device:
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            
            # Wait for the first available frame
            inRgb = qRgb.get()
            frame = inRgb.getCvFrame()

            image_path = os.path.join(self.save_path, f"after.jpg")
            cv2.imwrite(image_path, frame)

            print(f"Saved image: {image_path}")
            return image_path

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
    print(f"Trash emissions: {report_data.trashEmissions} kg CO2e")
    print(f"Recycle emissions: {report_data.recycleInTrashEmissions} kg CO2e")
    print(f"Compost emissions: {report_data.compostInTrashEmissions} kg CO2e")

if __name__ == "__main__":
    main() 