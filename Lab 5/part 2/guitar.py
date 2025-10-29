from teachable_machine_lite import TeachableMachineLite
import cv2 as cv
import time
import sys
from pathlib import Path

# Ensure parent directory is on sys.path so we can import HandTrackingModule
parent = Path(__file__).resolve().parent.parent
if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))

import HandTrackingModule as htm
import HandTrackingModule as htm 
import math
import numpy as np 

cap = cv.VideoCapture(0)

# --- Configuration ---
# Simplified "Happy Birthday" sequence (replace with your actual note labels)
# The labels MUST exactly match the 'label' output from your model, e.g., '1 C Major'
NOTE_SEQUENCE = ['c', 'e', 'c', 'd', 'e', 'g', 'e', 'c', 'f']
CORRECT_HOLD_TIME = 1.5 # Time in seconds the correct note must be held
FEEDBACK_DISPLAY_TIME = 1.5 # Time in seconds to display "Correct!"

# --- Classifier Setup ---
model_path = 'model.tflite'
image_file_name = "frame.jpg"
labels_path = "labels.txt"
tm_model = TeachableMachineLite(model_path=model_path, labels_file_path=labels_path)

# --- Hand Tracker Setup ---
wCam, hCam = 640, 480
cap.set(cv.CAP_PROP_FRAME_WIDTH, wCam)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, hCam)
detector = htm.handDetector(detectionCon=int(0.7)) 

# --- Sequence State Variables ---
current_note_index = 0
target_note = NOTE_SEQUENCE[current_note_index]
correct_note_start_time = None
last_action_time = time.time() # To track when to switch from 'Correct!' back to 'Holding...'

# --- Main Loop Variables ---
pTime = 0 

def clean_label(label):
    """
    Cleans the Teachable Machine label output to extract only the core note name.
    Example: '1 c nothing' -> 'c'
    Example: '2 e' -> 'e'
    """
    # 1. Remove leading number and space (e.g., '1 C Major' -> 'C Major')
    parts = label.split(' ', 1)
    if len(parts) > 1 and parts[0].isdigit():
        label = parts[1]
    
    # 2. Split by space and take the first part (e.g., 'C Major' -> 'C')
    core_note = label.split(' ')[0].strip().lower()
    
    # 3. Handle 'nothing' or similar background labels
    if core_note == 'nothing' or not core_note:
        return 'no note' # Use a distinct string for when nothing is detected
        
    return core_note

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # --- Hand Tracking (Kept for visual reference) ---
    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False) 

    if len(lmList) != 0:
        # Drawing logic (kept minimal for clarity)
        thumbX, thumbY = lmList[4][1], lmList[4][2] 
        pointerX, pointerY = lmList[8][1], lmList[8][2] 
        cv.circle(frame, (thumbX, thumbY), 10, (255, 0, 255), cv.FILLED)
        cv.circle(frame, (pointerX, pointerY), 10, (255, 0, 255), cv.FILLED)
        cv.line(frame, (thumbX, thumbY), (pointerX, pointerY), (255, 0, 255), 3)

    # --- Guitar Note Classification ---
    cv.imwrite(image_file_name, frame)
    results = tm_model.classify_image(image_file_name)
    
    # Extract the highest confidence classification info
    raw_detected_label = results.get('label', 'No Note')
    confidence = results.get('confidence', 0.0)
    
    # Clean up the detected label 
    detected_note = clean_label(raw_detected_label)
    
    # --- Sequencing and State Logic ---
    current_time = time.time()
    feedback_message = ""
    
    # Check if the sequence is complete
    if current_note_index >= len(NOTE_SEQUENCE):
        feedback_message = "SONG COMPLETE! 🎉"
        target_note = "" # Clear target
        correct_note_start_time = None
    else:
        # Check if the detected note matches the target note
        if detected_note == target_note.lower():
            
            if correct_note_start_time is None:
                # Start the timer for holding the correct note
                correct_note_start_time = current_time
            
            # Check if the note has been held long enough
            elif (current_time - correct_note_start_time) >= CORRECT_HOLD_TIME:
                
                # Move to the next note in the sequence
                current_note_index += 1
                if current_note_index < len(NOTE_SEQUENCE):
                    target_note = NOTE_SEQUENCE[current_note_index]
                    feedback_message = "CORRECT! ✅ Next Note Ready..."
                else:
                    feedback_message = "CORRECT! ✅" # Final correct note
                    
                correct_note_start_time = None # Reset timer
                last_action_time = current_time # Start feedback display timer
                
        else:
            # If the detected note is wrong, reset the hold timer
            correct_note_start_time = None
            
        # Determine the user instruction message
        if current_note_index < len(NOTE_SEQUENCE):
            if current_note_index == 0 or (current_time - last_action_time) > FEEDBACK_DISPLAY_TIME:
                # Default instruction: wait for the target note
                feedback_message = f"Hold **{target_note.upper()}** (Note {current_note_index + 1}/{len(NOTE_SEQUENCE)})"
                if correct_note_start_time:
                    # Show progress bar/timer
                    progress = (current_time - correct_note_start_time) / CORRECT_HOLD_TIME
                    progress_int = int(progress * 10)
                    feedback_message += " [" + "#" * progress_int + "-" * (10 - progress_int) + "]"

    # --- Drawing Text on Frame ---
    
    # 1. Instruction/Feedback Message (Large, Center Top)
    if feedback_message:
        text_color = (0, 255, 0) if "CORRECT" in feedback_message or "COMPLETE" in feedback_message else (255, 255, 255)
        text_pos = (wCam // 2 - 200, 50)
        cv.putText(frame, feedback_message.replace('**',''), text_pos, 
                   cv.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
                   
    # 2. Currently Detected Note (Top Left)
    detected_text = f"Detected: {raw_detected_label} ({confidence:.1f}%)"
    cv.putText(frame, detected_text, (10, hCam - 30), 
               cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2) 

    # 3. Show the frame
    cv.imshow('Guitar Note Trainer', frame)
    
    # 4. Check for exit key (ESC)
    k = cv.waitKey(1)
    if k % 256 == 27: 
        break

# Clean up
cap.release()
cv.destroyAllWindows()