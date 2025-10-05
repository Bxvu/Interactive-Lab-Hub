# main.py

import threading
import time
from queue import Queue

# Import the new classes from your files
from focus_timer import FocusTimer
from voice_assistant import OllamaVoiceAssistant

def run_focus_timer(timer_command_queue, audio_command_queue):
    """Run the focus timer app."""
    try:
        timer = FocusTimer(timer_command_queue, audio_command_queue)
        timer.run()
    except Exception as e:
        print(f"Error in Focus Timer thread: {e}")

def run_voice_assistant(timer_command_queue, audio_command_queue):
    """Run the voice assistant."""
    try:
        assistant = OllamaVoiceAssistant(timer_command_queue, audio_command_queue)
        assistant.run_conversation()
    except Exception as e:
        print(f"Error in Voice Assistant thread: {e}")

if __name__ == "__main__":
    # Create a shared queue for communication
    timer_command_queue = Queue()
    audio_command_queue = Queue() 

    # Create threads, passing the queue to both
    focus_timer_thread = threading.Thread(target=run_focus_timer, args=(timer_command_queue, audio_command_queue), daemon=True)
    voice_assistant_thread = threading.Thread(target=run_voice_assistant, args=(timer_command_queue, audio_command_queue), daemon=True)

    print("Starting Focus Timer and Voice Assistant...")
    focus_timer_thread.start()
    voice_assistant_thread.start()

    # Keep the main thread alive to monitor the others
    while True:
        try:
            # You can check if threads are alive here if needed
            if not focus_timer_thread.is_alive():
                print("Focus timer thread has stopped.")
                break
            if not voice_assistant_thread.is_alive():
                print("Voice assistant thread has stopped.")
                break
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down main program...")
            break