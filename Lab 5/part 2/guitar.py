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
import math
import numpy as np 

cap = cv.VideoCapture(0)

# --- Configuration ---
# Simplified "Happy Birthday" sequence
# actually cecdegecffede
NOTE_SEQUENCE = ['c', 'e', 'c', 'd', 'e', 'g', 'e', 'c', 'f', 'f', 'e', 'd', 'e']
# I actually mislabeled some notes, so here is the correct mapping:
# wrong -> actual
# 2-e -> c
# 3-c -> a
# 3-b -> g

NOTES_MAPPED = {
    'c': 'A',
    'd': 'D',
    'e': 'C',
    'f': 'F',
    'g': 'G',
    '1s': 'First String Open',
    '2s': 'Second String Open',
    '3s': 'Third String Open',
}

INSTRUCTIONS = {
    'c': "Hold A (Third String, 2nd Fret)",
    '3s': "Play Third String Open",
    'd': "Hold D (Second String, 3rd Fret)",
    'e': "Hold C (Second String, 1st Fret)",
    '2s': "Play Second String Open",
    'f': "Hold F (First String, 1st Fret)",
    'g': "Hold G (First String, 3rd Fret)",
    '1s': "Play First String Open",
}

# --- Debounce Configuration (New!) ---
MISCLASSIFICATION_THRESHOLD = 7 # Allow 7 consecutive frames of misclassification
CORRECT_HOLD_TIME = 1.85           # Time in seconds the correct note must be held
FEEDBACK_DISPLAY_TIME = 1.85 # Time in seconds to display "Correct!"

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
last_action_time = time.time() - FEEDBACK_DISPLAY_TIME - 1.0 # To track when to switch from 'Correct!' back to 'Holding...'

# --- Debounce State Variable (New!) ---
misclassification_count = 0

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

    # # --- Hand Tracking (Kept for visual reference) ---
    # frame = detector.findHands(frame)
    # lmList = detector.findPosition(frame, draw=False) 

    # if len(lmList) != 0:
    #     # Drawing logic (kept minimal for clarity)
    #     thumbX, thumbY = lmList[4][1], lmList[4][2] 
    #     pointerX, pointerY = lmList[8][1], lmList[8][2] 
    #     cv.circle(frame, (thumbX, thumbY), 10, (255, 0, 255), cv.FILLED)
    #     cv.circle(frame, (pointerX, pointerY), 10, (255, 0, 255), cv.FILLED)
    #     cv.line(frame, (thumbX, thumbY), (pointerX, pointerY), (255, 0, 255), 3)

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
    
    # Check if the sequence is complete (PRIORITY 1)
    if current_note_index >= len(NOTE_SEQUENCE):
        feedback_message = "SONG COMPLETE! Well Done! 🎉"
        target_note = ""
        correct_note_start_time = None
    else:
        # Check if the detected note matches the target note
        if detected_note == target_note.lower():
            
            # Reset misclassification count if correct
            misclassification_count = 0
            
            # CONDITION 1: Check to START the timer
            # The timer only starts if it's currently None AND the feedback period is over.
            if correct_note_start_time is None and (current_time - last_action_time) > FEEDBACK_DISPLAY_TIME:
                correct_note_start_time = current_time
            
            # CONDITION 2: Check to ADVANCE the note (Timer is running AND time is up)
            elif correct_note_start_time is not None and (current_time - correct_note_start_time) >= CORRECT_HOLD_TIME:
                
                # Advance note and set up SUCCESS feedback
                current_note_index += 1
                if current_note_index < len(NOTE_SEQUENCE):
                    target_note = NOTE_SEQUENCE[current_note_index]
                    # This message is displayed during the feedback period by the logic below
                    feedback_message = "CORRECT! Next Note Ready..." 
                else:
                    feedback_message = "CORRECT!" 
                    
                correct_note_start_time = None # Reset hold timer
                last_action_time = current_time # Reset feedback timer
                
        else:
            # --- Debounce Logic (WRONG NOTE DETECTED) ---
            misclassification_count += 1
            
            if correct_note_start_time is not None and misclassification_count < MISCLASSIFICATION_THRESHOLD:
                pass # Still within the debounce grace period
            else:
                correct_note_start_time = None # RESET hold timer
                misclassification_count = 0 
                
    # --- Determine the Display Message (PRIORITY 2 & 3) ---
    
    # PRIORITY 2: Display SUCCESS FEEDBACK if the timer hasn't expired
    if current_note_index < len(NOTE_SEQUENCE) and (current_time - last_action_time) <= FEEDBACK_DISPLAY_TIME:
        # We need to know if the last action was *advancing* the note, which we can check
        # by seeing if we are in the initial frames of the sequence (current_note_index > 0)
        
        # If the success message was set in the block above, use it. Otherwise, assume default success text.
        if "CORRECT" not in feedback_message:
            feedback_message = "CORRECT! Next Note Ready..."
            
    # PRIORITY 3: Display HOLD INSTRUCTION (only if NOT COMPLETE and NOT in feedback period)
    elif current_note_index < len(NOTE_SEQUENCE):
        # Default instruction: wait for the target note (If no feedback is active)
        
        # Use a more descriptive instruction from your INSTRUCTIONS dict
        # instruction_text = INSTRUCTIONS.get(target_note, f"Hold {NOTES_MAPPED.get(target_note, target_note).upper()}")

        # Build the message
        feedback_message = f"Hold {NOTES_MAPPED.get(target_note, target_note).upper()} | Note {current_note_index + 1}/{len(NOTE_SEQUENCE)}"
        
        # Append the progress bar if the hold timer is running
        if correct_note_start_time is not None:
            progress = (current_time - correct_note_start_time) / CORRECT_HOLD_TIME
            progress = min(1.0, progress) # Cap progress at 100%
            progress_int = int(progress * 10)
            feedback_message += " [" + "#" * progress_int + "-" * (10 - progress_int) + "]"

    # --- Drawing Text on Frame ---
    
    # 1. Instruction/Feedback Message (Large, Center Top)
    if feedback_message:
        # Use BOLD for the instruction text
        display_text = feedback_message.replace('**','')
        text_color = (0, 255, 0) if "CORRECT" in display_text or "COMPLETE" in display_text else (255, 255, 255)
        text_pos = (wCam // 2 - 280, 50)
        cv.putText(frame, display_text, text_pos, 
                    cv.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
                    
    # 2. Current Instruction (Bottom Left) - Keep this for the detailed text
    instruction_text = f"Instruction: {INSTRUCTIONS.get(target_note, 'N/A')}"
    cv.putText(frame, instruction_text, (10, hCam - 30), 
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