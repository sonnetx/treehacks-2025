from ultralytics import YOLO
import cv2
import numpy as np

def detect_objects(image_path, confidence_threshold=0.05):
    """
    Perform object detection on an image using YOLOv8
    
    Args:
        image_path (str): Path to the input image
        confidence_threshold (float): Minimum confidence score for detections
        
    Returns:
        tuple: (annotated_image, detections)
    """
    # Load the pretrained model
    model = YOLO('yolov8n.pt')  # Uses the nano model, can be changed to 's', 'm', 'l', or 'x' for larger models
    
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not read the image")
    
    # Run inference
    results = model(image)[0]
    
    # Process and visualize detections
    annotated_image = image.copy()
    detections = []
    
    for box in results.boxes:
        # Get box coordinates
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        # Get confidence and class
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        class_name = results.names[class_id]
        
        # Filter by confidence
        if confidence < confidence_threshold:
            continue
            
        # Add detection to list
        detections.append({
            'class': class_name,
            'confidence': confidence,
            'bbox': (x1, y1, x2, y2)
        })
        
        # Draw bounding box
        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Add label
        label = f'{class_name}: {confidence:.2f}'
        cv2.putText(annotated_image, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return annotated_image, detections

def save_results(image, output_path):
    """Save the annotated image"""
    cv2.imwrite(output_path, image)

# Example usage
if __name__ == "__main__":
    # Specify your image path
    image_path = "C:/Users/sonne/Downloads/trash.jpg"
    output_path = "detected.jpg"
    
    try:
        # Perform detection
        annotated_image, detections = detect_objects(image_path)
        
        # Save the annotated image
        save_results(annotated_image, output_path)
        
        # Print detections
        print("\nDetections:")
        for det in detections:
            print(f"Class: {det['class']}, Confidence: {det['confidence']:.2f}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")