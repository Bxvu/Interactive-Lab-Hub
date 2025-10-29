from teachable_machine_lite import TeachableMachineLite
import cv2 as cv
import time # Import time to potentially track FPS or for future use

cap = cv.VideoCapture(0)

# Set frame size (optional, but good practice for consistency)
wCam, hCam = 640, 480
cap.set(cv.CAP_PROP_FRAME_WIDTH, wCam)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, hCam)

model_path = 'model.tflite'
image_file_name = "frame.jpg"
labels_path = "labels.txt"

tm_model = TeachableMachineLite(model_path=model_path, labels_file_path=labels_path)

# Variables for FPS calculation
pTime = 0 

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # 1. Save the frame for classification
    cv.imwrite(image_file_name, frame)
    
    # 2. Classify the image
    results = tm_model.classify_image(image_file_name)
    
    # Extract the highest confidence classification info
    note_label = results.get('label', 'No Label')
    confidence = results.get('confidence', 0.0)
    
    # --- Drawing and Displaying Info (Similar to TA's Example) ---
    
    # 3. Format the text to display
    display_text = f"Note: {note_label}"
    confidence_text = f"Conf: {confidence:.2f}%"

    # 4. Display the detected note label on the frame
    # Parameters: image, text, position (x,y), font, scale, color (BGR), thickness
    cv.putText(frame, display_text, (10, 30), 
               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) # Green text for label
    
    # 5. Display the confidence percentage
    cv.putText(frame, confidence_text, (10, 70), 
               cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2) # Yellow text for confidence

    # Optional: Display FPS (adapted from TA's example)
    cTime = time.time()
    if pTime != 0:
        fps = 1 / (cTime - pTime)
        cv.putText(frame, f'FPS: {int(fps)}', (wCam - 120, 30), 
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    pTime = cTime
    
    # 6. Show the frame with the added text
    cv.imshow('Guitar Note Classifier', frame)
    
    # 7. Check for exit key
    k = cv.waitKey(1)
    if k % 256 == 27: # ASCII for ESC key
        # press ESC to close camera view.
        break

# Clean up
cap.release()
cv.destroyAllWindows()