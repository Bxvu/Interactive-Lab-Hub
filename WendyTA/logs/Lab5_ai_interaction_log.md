# Lab 5 AI Interaction Log - Observant Systems

This file automatically logs all significant interactions between students and WendyTA (GitHub Copilot Chat) during Lab 5.

## How to Use This Log
- **Automatic**: WendyTA appends entries when providing substantial help
- **Timestamped**: Each interaction includes date/time in YYYY-MM-DD HH:MM:SS format
- **Commit Required**: Students must commit this file with their lab submission
- **Attribution**: Reference this log in your Lab 5 README.md under "AI Usage"

## Log Entries
*Interactions will be automatically appended below with timestamps*

---

## [2025-01-22 14:30:00] - Speed Mode Implementation
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 5/part 2/guitar_audio.py`
- **AI-Generated Code**: 
  - Added game mode system with `GAME_MODE` variable ("normal" or "speed")
  - Implemented mode-specific timing: `SPEED_MODE_HOLD_TIME = 0.8s`, `SPEED_MODE_FEEDBACK_TIME = 0.5s`
  - Created dynamic timing variables `active_hold_time` and `active_feedback_time` that switch based on mode
  - Implemented relaxed audio matching for speed mode (accepts ANY note played, not specific notes)
  - Added 'M' key to toggle between normal and speed modes
  - Added on-screen mode display (cyan text for speed, white for normal)
  - Added controls hint: "Press M to toggle mode | S to skip"

- **Student Modifications**: Student requested separate game mode for faster practice with relaxed accuracy

### Interaction Summary
- **Questions Asked**: "how can i add another separate mode for this program, like speed mode, which lowers the time of the feedback and also doesn't care about the exact note being correct, just that any note has been played"

- **Answers Provided**: 
  - Implemented dual-mode system with configuration variables
  - Modified all timing logic to use `active_hold_time` and `active_feedback_time` instead of hardcoded constants
  - Changed audio detection logic: speed mode accepts `len(detected_audio_notes) > 0`, normal mode checks specific note match
  - Added keyboard toggle ('M' key) that switches modes and resets timers
  - Visual feedback shows current mode on screen

- **Learning Objectives**: 
  - Understanding conditional game mechanics based on mode selection
  - Implementing relaxed matching criteria for different difficulty levels
  - Dynamic variable assignment based on game state
  - User experience design: different practice modes for different learning goals

### Next Steps
- Test both modes to verify speed mode works as intended (faster, accepts any note)
- Consider adding more modes or difficulty variations
- Possible enhancement: display different visual cues for speed mode (color changes, icons)

---

## [2025-10-30 15:45:00] - Silence Detection Between Notes
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 5/part 2/guitar_audio.py`
- **AI-Generated Code**: 
  - Added silence detection configuration: `SILENCE_FRAMES_REQUIRED = 3`
  - Implemented `silence_frame_count` counter to track consecutive silent frames
  - Added `waiting_for_silence` flag that prevents accepting new notes until silence detected
  - Modified audio detection logic to increment/reset silence counter based on note presence
  - Updated PLAY stage to only check for notes when NOT waiting for silence
  - Set `waiting_for_silence = True` after each note completion
  - Added debug output: "SILENCE DETECTED (X frames) - Ready for next note"

- **Student Modifications**: Student identified issue where multiple notes could be sped through because the next note detection picks up the previous note still playing

### Interaction Summary
- **Questions Asked**: "right now, multiple notes can be sped through because the next note may detect the previous note still being played. can you make sure that the microphone hears nothing or background noise first for a few frames before accepting another note"

- **Answers Provided**: 
  - Implemented silence gate mechanism requiring 3 consecutive frames with no notes detected
  - Audio detection now tracks whether any notes exceed threshold, incrementing silence counter when clean
  - After completing a note, system enters "waiting for silence" mode
  - New notes cannot be accepted until `SILENCE_FRAMES_REQUIRED` silent frames detected
  - Prevents carryover detection from previous note's sustain/ring-out

- **Learning Objectives**: 
  - Understanding state machine design with gating conditions
  - Implementing debouncing logic for audio event detection
  - Using flags to control state transitions and prevent false positives
  - Temporal sequencing: ensuring proper gaps between discrete events

### Next Steps
- Test to verify notes don't advance prematurely with sustained guitar tones
- May need to adjust `SILENCE_FRAMES_REQUIRED` based on playing style (slower = more frames needed)
- Could add visual indicator showing "waiting for silence" status to give user feedback

---

## [2025-10-30 16:00:00] - Speed Mode Lenient Tolerance
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 5/part 2/guitar_audio.py`
- **AI-Generated Code**: 
  - Added speed mode-specific misclassification thresholds: `SPEED_MODE_THRESHOLD_BASE = 12`, `SPEED_MODE_THRESHOLD_MAX = 25`
  - Modified dynamic threshold calculation to use mode-specific thresholds
  - Speed mode now uses 12-25 frame buffer (vs normal mode's 7-14 frames)
  - Updated threshold selection logic to check `GAME_MODE` and assign appropriate base/max values
  - Applied mode-specific base threshold when no progress has started

- **Student Modifications**: Student requested more lenient misclassification buffer in speed mode for easier/faster gameplay

### Interaction Summary
- **Questions Asked**: "in speed mode, increase the misclassification buffer for hold progress so its more lenient"

- **Answers Provided**: 
  - Implemented separate threshold constants for speed mode (nearly double the normal mode values)
  - Modified progressive tolerance system to select thresholds based on current game mode
  - Speed mode now tolerates ~71% more misclassifications at base (12 vs 7 frames)
  - At high progress (90%+), speed mode tolerates ~79% more misclassifications (25 vs 14 frames)
  - This makes hand positioning less strict in speed mode, supporting faster progression

- **Learning Objectives**: 
  - Understanding difficulty tuning through parameter variation
  - Implementing mode-specific behavior while maintaining shared logic structure
  - Balancing speed vs accuracy trade-offs in interactive systems
  - Progressive scaling applied differently across game modes

### Next Steps
- Test speed mode with new tolerances to verify it feels appropriately lenient
- May adjust values further if still too strict or too loose
- Consider adding visual indication of current tolerance level (progress bar or threshold meter)

---
