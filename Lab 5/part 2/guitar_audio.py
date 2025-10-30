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
import pyaudio
import queue
from numpy_ringbuffer import RingBuffer
import tflite_runtime.interpreter as tflite

cap = cv.VideoCapture(0)

# --- Configuration ---
# Simplified "Happy Birthday" sequence
# actually cecdegecffede
NOTE_SEQUENCE = ['3s', '3s', 'c', '3s', 'e', '2s',
                '3s', '3s', 'c', '3s', 'd', 'e', 
                '3s', '3s', 'g', '1s', 'e', '2s', 'c',
                 'f', 'f', '1s', 'e', 'd', 'e']
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
    'c': "A (Third String, 2nd Fret)",
    '3s': "Third String Open",
    'd': "D (Second String, 3rd Fret)",
    'e': "C (Second String, 1st Fret)",
    '2s': "Second String Open",
    'f': "F (First String, 1st Fret)",
    'g': "G (First String, 3rd Fret)",
    '1s': "First String Open",
}

# --- Debounce Configuration (New!) ---
MISCLASSIFICATION_THRESHOLD_BASE = 7  # Base threshold at 0% progress
MISCLASSIFICATION_THRESHOLD_MAX = 14  # Max threshold at 90%+ progress
CORRECT_HOLD_TIME = 1.85           # Time in seconds the correct note must be held
FEEDBACK_DISPLAY_TIME = 1.85 # Time in seconds to display "Correct!"

# --- Classifier Setup ---
model_path = 'model.tflite'
image_file_name = "frame.jpg"
labels_path = "labels.txt"
tm_model = TeachableMachineLite(model_path=model_path, labels_file_path=labels_path, model_type='image')

# --- Hand Tracker Setup ---
wCam, hCam = 640, 480
cap.set(cv.CAP_PROP_FRAME_WIDTH, wCam)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, hCam)
detector = htm.handDetector(detectionCon=int(0.7)) 

# --- Sequence State Variables ---
current_note_index = 0
target_note = NOTE_SEQUENCE[current_note_index]
correct_note_start_time = None
last_action_time = time.time() - FEEDBACK_DISPLAY_TIME - 1.0 
misclassification_count = 0

# NEW: State tracking for the two-stage process
STAGE_HOLD = 1 
STAGE_PLAY = 2
stage = STAGE_HOLD # Start in the Hold stage

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


# --- Audio Configuration ---
AUDIO_MODEL_PATH = 'sound_classifier.tflite'
AUDIO_LABELS_PATH = 'sound_labels.txt'
DEVICE_INDEX = 0 # <--- IMPORTANT: Update this index to your microphone's index
SAMPLING_RATE = 48000
FORMAT = np.float32
CHANNELS = 1
AUDIO_CHUNK_SIZE = int(SAMPLING_RATE / 2)
MODEL_REQUIRED_SAMPLES = 44032 
AUDIO_SAMPLES_REQUIRED = MODEL_REQUIRED_SAMPLES

AUDIO_NOTES_MAP = {
    '3-c': 'A',
    '2-d': 'D',
    '2-e': 'C',
    '1-f': 'F',
    '1-g': 'G',
    '1-e': 'First String Open',
    '2-f': 'Second String Open',
    '3-b': 'Third String Open',
}

# --- TFLite Audio Interpreter Setup (REPLACES tm_audio_model init) ---
interpreter = tflite.Interpreter(model_path=AUDIO_MODEL_PATH)
interpreter.allocate_tensors()
audio_input_details = interpreter.get_input_details()[0]
audio_output_details = interpreter.get_output_details()[0]

# Manually load audio labels
with open(AUDIO_LABELS_PATH, 'r') as f:
    audio_labels = [line.strip() for line in f.readlines()]

# --- PyAudio Setup ---
audioQueue = queue.Queue()
pyaudio_instance = pyaudio.PyAudio()

def _callback(in_data, frame_count, time_info, status):
    audioQueue.put(in_data)
    return None, pyaudio.paContinue

AudioBuffer = RingBuffer(capacity=AUDIO_SAMPLES_REQUIRED, dtype=FORMAT)
stream = pyaudio_instance.open(
    input=True,
    start=False,
    format=pyaudio.paFloat32,
    channels=CHANNELS,
    rate=SAMPLING_RATE,
    frames_per_buffer=AUDIO_CHUNK_SIZE,
    stream_callback=_callback,
    input_device_index=DEVICE_INDEX
)
stream.start_stream()

audio_note = "No Audio"

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

    # --- Audio Processing and Classification ---
    raw_audio_label = "No Audio"
    audio_confidence = 0.0
    audio_note = "no note"
    audio_predictions_text = "" # NEW: String to hold all predictions

    while not audioQueue.empty():
        frames = audioQueue.get() 
        framesData = np.frombuffer(frames, dtype=FORMAT) 
        AudioBuffer.extend(framesData[0::CHANNELS])

    if AudioBuffer.is_full:
        audio_buffer_np = np.array(AudioBuffer)
        
        # Reshape and Run the TFLite Interpreter
        input_shape = audio_input_details['shape']
        input_data = audio_buffer_np.reshape(input_shape)

        interpreter.set_tensor(audio_input_details['index'], input_data)
        interpreter.invoke()
        
        # Get the output probabilities
        output_data = interpreter.get_tensor(audio_output_details['index'])
        probabilities = output_data[0]
        
        # Determine the top classification result
        top_index = np.argmax(probabilities)
        audio_confidence = probabilities[top_index] * 100
        raw_audio_label = audio_labels[top_index]
        audio_note = clean_label(raw_audio_label)
        

        THRESHOLD = 0.15
        
        # NEW: Store which notes exceed threshold for later comparison
        detected_audio_notes = {}  # Maps cleaned label to confidence
        
        for i, probability in enumerate(probabilities):
            if probability >= THRESHOLD and audio_labels[i] != "8 Background Noise":
                note_label = audio_labels[i]
                cleaned = clean_label(note_label)
                confidence_percent = probability * 100
                detected_audio_notes[cleaned] = confidence_percent
                
                # Print the detected note and confidence to the console
                print(f"HIGH CONFIDENCE AUDIO DETECTED: {note_label} (cleaned: {cleaned}) at {confidence_percent:.2f}%")

        # Sort predictions by confidence in descending order
        sorted_indices = np.argsort(probabilities)[::-1]
        
        # Build the predictions string, displaying the top 3-5 classes
        display_count = min(len(audio_labels), 5) # Show at most 5 predictions
        for i in range(display_count):
            index = sorted_indices[i]
            label = audio_labels[index]
            confidence_percent = probabilities[index] * 100
            
            # Use the cleaned label for a cleaner display
            clean_pred_label = clean_label(label).upper()
            
            audio_predictions_text += f"{clean_pred_label}: {confidence_percent:.1f}% | "

        # Clean up the end of the string
        audio_predictions_text = audio_predictions_text.strip(' | ')


        # Advance audio window
        samples_to_discard = int(AUDIO_SAMPLES_REQUIRED / 4)
        new_buffer_content = AudioBuffer[samples_to_discard:]
        
        AudioBuffer = RingBuffer(
            capacity=AUDIO_SAMPLES_REQUIRED, 
            dtype=FORMAT,
        )
        AudioBuffer.extend(new_buffer_content)
    
    # --- Sequencing and State Logic ---
    current_time = time.time()
    feedback_message = ""
    
    # Check if the sequence is complete (PRIORITY 1)
    if current_note_index >= len(NOTE_SEQUENCE):
        feedback_message = "SONG COMPLETE! Well Done!"
        target_note = ""
        correct_note_start_time = None
    else: # The sequence is not complete
        target_clean = target_note.lower()
        
        # Check if the target note is an OPEN STRING (stage is always PLAY)
        is_open_string = target_clean in ['1s', '2s', '3s']

        # --- STAGE 1: HOLD POSITION (Visual Check Only) ---
        if stage == STAGE_HOLD and not is_open_string:
            
            # Calculate dynamic threshold based on progress
            if correct_note_start_time is not None:
                progress = (current_time - correct_note_start_time) / CORRECT_HOLD_TIME
                progress = min(1.0, progress)
                
                # Ramp up tolerance: more lenient as progress increases
                # At 0% progress: use base threshold (7 frames)
                # At 90%+ progress: use max threshold (20 frames)
                if progress < 0.9:
                    # Linear interpolation from base to max
                    dynamic_threshold = MISCLASSIFICATION_THRESHOLD_BASE + \
                                      (MISCLASSIFICATION_THRESHOLD_MAX - MISCLASSIFICATION_THRESHOLD_BASE) * (progress / 0.9)
                else:
                    dynamic_threshold = MISCLASSIFICATION_THRESHOLD_MAX
                
                dynamic_threshold = int(dynamic_threshold)
            else:
                # No progress yet, use base threshold
                dynamic_threshold = MISCLASSIFICATION_THRESHOLD_BASE
            
            # CONDITION: Correct VISUAL note is held
            if detected_note == target_clean:
                # Reset misclassification count if correct
                misclassification_count = 0
                
                # Check 1: START THE HOLD TIMER
                if correct_note_start_time is None and (current_time - last_action_time) > FEEDBACK_DISPLAY_TIME:
                    correct_note_start_time = current_time
                
                # Check 2: ADVANCE STAGE (Hold timer finished)
                elif correct_note_start_time is not None and (current_time - correct_note_start_time) >= CORRECT_HOLD_TIME:
                    stage = STAGE_PLAY # Move to the next stage
                    correct_note_start_time = None # Reset timer
                    last_action_time = current_time # Start feedback timer
                    feedback_message = "POSITION HELD! ✅ Now Play the Note!" 
                    
            else:
                # --- Debounce Logic (WRONG FRET DETECTED) ---
                misclassification_count += 1
                if correct_note_start_time is not None and misclassification_count < dynamic_threshold:
                    pass # Still within the debounce grace period
                else:
                    correct_note_start_time = None # RESET hold timer
                    misclassification_count = 0 
                    
        # --- STAGE 2: PLAY NOTE (Audio Check Only) ---
        elif stage == STAGE_PLAY or is_open_string: # Open strings skip directly here
            
            # Determine the audio target (use the mapped note for the sound model)
            # First get the expected note name from NOTES_MAPPED
            expected_note_name = NOTES_MAPPED.get(target_clean, target_clean)
            
            # Now find which audio label maps to that note name
            # Reverse lookup: find the key in AUDIO_NOTES_MAP whose value matches expected_note_name
            audio_target_label = None
            for audio_label, note_name in AUDIO_NOTES_MAP.items():
                if note_name == expected_note_name:
                    audio_target_label = audio_label
                    break

            # Check if the audio note was detected (using the stored detections)
            audio_detected = False
            if audio_target_label is not None and 'detected_audio_notes' in locals():
                cleaned_target = clean_label(audio_target_label)
                if cleaned_target in detected_audio_notes:
                    confidence = detected_audio_notes[cleaned_target]
                    audio_detected = True
                    print(f"MATCH! Expected: {audio_target_label} (cleaned: {cleaned_target}), Confidence: {confidence:.2f}%")
                # else:
                    # print(f"Expected: {audio_target_label} (cleaned: {cleaned_target}) - Not detected above threshold")
            
            # CONDITION: Correct AUDIO note is played
            if audio_detected:
                
                # This check only needs to pass once per note
                if (current_time - last_action_time) > FEEDBACK_DISPLAY_TIME:
                    
                    # Advance note and set up SUCCESS feedback (Move to next song note)
                    current_note_index += 1
                    stage = STAGE_HOLD # Always reset to HOLD for the *next* note
                    
                    if current_note_index < len(NOTE_SEQUENCE):
                        target_note = NOTE_SEQUENCE[current_note_index]
                        feedback_message = "CORRECT! Next Note Ready..." 
                    else:
                        feedback_message = "CORRECT!" 
                        
                    correct_note_start_time = None # Reset hold timer
                    last_action_time = current_time # Reset feedback timer
                    
            else:
                # If the audio is wrong, we don't reset anything, just wait for the strum.
                # If the user strums a wrong note, they just try again.
                pass 
                
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
        target_clean = target_note.lower()
        
        if stage == STAGE_HOLD and not is_open_string:
            # Stage 1: Tell user to HOLD the fret
            instruction_text = INSTRUCTIONS.get(target_clean, f"Hold {NOTES_MAPPED.get(target_clean, target_clean).upper()}")
            stage_label = "HOLD POSITION"
        else:
            # Stage 2: Tell user to PLAY the note (or this is an open string)
            instruction_text = f"Play {NOTES_MAPPED.get(target_clean, target_clean).upper()}"
            stage_label = "PLAY SOUND"
            
        # Build the message (split into two lines)
        feedback_line1 = f"{stage_label}: {instruction_text}"
        feedback_line2 = f"Note {current_note_index + 1}/{len(NOTE_SEQUENCE)}"
        
        # Append the progress bar ONLY if in the HOLD stage and timer is running
        if stage == STAGE_HOLD and correct_note_start_time is not None:
            progress = (current_time - correct_note_start_time) / CORRECT_HOLD_TIME
            progress = min(1.0, progress)
            progress_int = int(progress * 10)
            feedback_line2 += " [" + "#" * progress_int + "-" * (10 - progress_int) + "]"

    # --- Drawing Text on Frame ---
    
    # 1. Instruction/Feedback Message (Large, Center Top, Two Lines)
    if feedback_message:
        # Use BOLD for the instruction text
        display_text = feedback_message.replace('**','')
        text_color = (0, 255, 0) if "CORRECT" in display_text or "COMPLETE" in display_text else (255, 255, 255)
        text_pos = (wCam // 2 - 280, 50)
        cv.putText(frame, display_text, text_pos, 
                    cv.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
    elif current_note_index < len(NOTE_SEQUENCE):
        # Display the two-line instruction
        text_color = (255, 255, 255)
        cv.putText(frame, feedback_line1, (10, 40), 
                    cv.FONT_HERSHEY_SIMPLEX, 0.9, text_color, 2)
        cv.putText(frame, feedback_line2, (10, 75), 
                    cv.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
                    
    # 2. Current Instruction (Bottom Left) - Keep this for the detailed text
    # hold_or_play_text = "Hold" if stage == STAGE_HOLD and not is_open_string else "Play"
    # instruction_text = f"Instruction: {hold_or_play_text} {INSTRUCTIONS.get(target_note, 'N/A')}"
    # cv.putText(frame, instruction_text, (10, hCam - 30), 
    #            cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    detected_text_visual = f"Visual: {raw_detected_label} ({confidence:.1f}%)"
    cv.putText(frame, detected_text_visual, (10, hCam - 55), 
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
               
    # NEW: Display ALL Audio Predictions (Below the visual info)
    detected_text_audio_all = f"Audio Top: {audio_predictions_text}"
    cv.putText(frame, detected_text_audio_all, (10, hCam - 30), 
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2) # Cyan color for audio debug

    # 3. Show the frame
    cv.imshow('Guitar Note Trainer', frame)
    
    # 4. Check for keyboard input
    k = cv.waitKey(1)
    
    # ESC key to exit
    if k % 256 == 27: 
        break
    
    # 'S' key to skip current note/stage
    elif k % 256 == ord('s') or k % 256 == ord('S'):
        print("SKIPPING current note/stage")
        
        # If we're in HOLD stage, skip to PLAY stage for the same note
        if stage == STAGE_HOLD and current_note_index < len(NOTE_SEQUENCE):
            stage = STAGE_PLAY
            correct_note_start_time = None
            last_action_time = current_time
            feedback_message = "SKIPPED HOLD! Now Play the Note!"
            print(f"Skipped to PLAY stage for note {current_note_index + 1}")
        
        # If we're in PLAY stage (or open string), skip to next note
        elif (stage == STAGE_PLAY or is_open_string) and current_note_index < len(NOTE_SEQUENCE):
            current_note_index += 1
            stage = STAGE_HOLD  # Reset to HOLD for next note
            
            if current_note_index < len(NOTE_SEQUENCE):
                target_note = NOTE_SEQUENCE[current_note_index]
                feedback_message = "SKIPPED! Next Note Ready..."
                print(f"Skipped to note {current_note_index + 1}: {target_note}")
            else:
                feedback_message = "SONG COMPLETE! (via skip)"
                
            correct_note_start_time = None
            last_action_time = current_time

# Clean up
cap.release()
cv.destroyAllWindows()
stream.stop_stream()
stream.close()
pyaudio_instance.terminate()