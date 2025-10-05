#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Voice Assistant for Lab 3
Interactive voice assistant using speech recognition, Ollama AI, and text-to-speech

Dependencies:
- ollama (API client)
- speech_recognition
- pyaudio
- pyttsx3 or espeak
"""

import speech_recognition as sr
import subprocess
import requests
import json
import time
import sys
import threading
import re
import random
from queue import Queue

# # Set UTF-8 encoding for output
if sys.stderr.encoding != 'UTF-8':
    import codecs
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

TTS_ENGINE = 'espeak'

class OllamaVoiceAssistant:
    def __init__(self, command_queue, audio_queue, model_name="gemma3:1b", ollama_url="http://localhost:11434"):
        self.command_queue = command_queue # Store the command queue
        self.audio_queue = audio_queue
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine_type = TTS_ENGINE  # Store the engine type
        self.conversation_history = []  # Initialize conversation history
        self.max_history_length = 5  # Limit the conversation history to the last 5 exchanges

        print(f"Using {self.tts_engine_type} for text-to-speech")
        
        # Test Ollama connection
        self.test_ollama_connection()
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("Ready for conversation!")

    def test_ollama_connection(self):
        """Test if Ollama is running and the model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                if self.model_name in model_names:
                    print(f"Ollama is running with {self.model_name} model")
                else:
                    print(f"Model {self.model_name} not found. Available models: {model_names}")
                    if model_names:
                        self.model_name = model_names[0]
                        print(f"Using {self.model_name} instead")
            else:
                raise Exception("Ollama API not responding")
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("Make sure Ollama is running: 'ollama serve'")
            sys.exit(1)

    def play_random_quack(self):
        """Play a random quack noise from the quack_noises folder."""
        import os
        import random

        quack_folder = "quack_noises"
        try:
            # List all WAV files in the quack_noises folder
            quack_files = [f for f in os.listdir(quack_folder) if f.endswith('.wav') and f.startswith('quack')]
            if not quack_files:
                print("No quack noises found in the folder.")
                return

            # Choose a random quack file
            random_quack = random.choice(quack_files)
            quack_path = os.path.join(quack_folder, random_quack)

            # Play the WAV file using aplay
            subprocess.run(["aplay", quack_path], check=False)
        except Exception as e:
            print(f"Error playing quack noise: {e}")

    def play_random_petting_noise(self):
        """Play a random petting noise from the quack_noises folder."""
        import os
        import random

        quack_folder = "quack_noises"
        try:
            # List all WAV files in the quack_noises folder
            petting_files = [f for f in os.listdir(quack_folder) if f.endswith('.wav')]
            if not petting_files:
                print("No petting noises found in the folder.")
                return

            # Choose a random petting file
            random_petting = random.choice(petting_files)
            petting_path = os.path.join(quack_folder, random_petting)

            # Play the WAV file using aplay
            subprocess.run(["aplay", petting_path], check=False)
        except Exception as e:
            print(f"Error playing petting noise: {e}")

    def add_duck_personality(self, response):
        """Enhance the response with duck-themed personality traits."""
        import random

        duck_facts = [
            "Did you know ducks have waterproof feathers? Quack quack!",
            "A group of ducks is called a raft, team, or paddling. Quack!",
            "Ducks can sleep with one eye open. I'm always watching!",
            "Quack quack! Ducks have been around for over 10 million years!",
            "I may be stuffed, but real ducks can fly at speeds of up to 60 mph!"
        ]

        if random.random() < 0.3:  # 30% chance to add a duck fact or joke
            response += " " + random.choice(duck_facts)

        if random.random() < 0.2:  # 20% chance to add a playful quack
            response = "Quack quack! " + response

        return response

    def clean_text_for_tts(self, text):
        """Remove unsupported characters from text for TTS and API calls."""
        # Convert to string if not already
        text = str(text)
        # Remove any non-ASCII characters (including curly quotes, ellipsis, etc.)
        import re
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # Keep only ASCII characters
        # Additional cleanup for common issues
        text = text.replace('…', '...').replace('–', '-').replace('—', '-')  # Replace common Unicode chars (though they should be caught above)
        return text

    def speak(self, text):
        """Convert text to speech and optionally play a random quack noise."""
        import random

        # Add duck personality to the response
        text = self.add_duck_personality(text)

        # Ensure quack noise is played only once before or after speaking
        play_quack_before = random.choice([True, False])
        play_quack_after = not play_quack_before

        if play_quack_before:
            self.play_random_quack()

        # Clean text to avoid encoding issues
        clean_text = self.clean_text_for_tts(text)
        print(f"Assistant: {clean_text}")

        # Use piper for TTS
        try:
            # Construct the piper command
            piper_command = [
                "piper",
                # "--model", "en_GB-northern_english_male-medium",
                "--model", "en_GB-semaine-medium",
                "--output-raw"
            ]
            # Use aplay to play the raw audio
            aplay_command = [
                "aplay",
                "-r", "22050",
                "-f", "S16_LE",
                "-t", "raw"
            ]
            # Run the pipeline: echo text | piper | aplay
            echo_process = subprocess.Popen(["echo", clean_text], stdout=subprocess.PIPE)
            piper_process = subprocess.Popen(piper_command, stdin=echo_process.stdout, stdout=subprocess.PIPE)
            subprocess.run(aplay_command, stdin=piper_process.stdout, check=False)
        except Exception as e:
            print(f"TTS error: {e}")
            print(f"Assistant said: {clean_text}")

        if play_quack_after:
            self.play_random_quack()

    def listen(self):
        """Listen for speech and convert to text"""
        try:
            print("Listening...")
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Recognizing...")
            # Use Google Speech Recognition (free)
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("No speech detected, timing out...")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None

    def preprocess_number_words(self, text):
        """Convert number words to digits in the text."""
        number_words = {
            "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
            "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
        }
        for word, digit in number_words.items():
            text = re.sub(rf"\b{word}\b", digit, text, flags=re.IGNORECASE)
        return text

    def parse_command(self, text):
        """Manually parse text for timer commands."""
        # Preprocess number words into digits
        text = self.preprocess_number_words(text)

        # For adding/decreasing time, e.g., "add 5 minutes"
        match = re.search(r'(increase|add|give me|set another)\s+(?:timer\s+)?(?:by\s+)?(\d+)\s+minute', text, re.IGNORECASE)
        if match:
            minutes = match.group(2)
            self.command_queue.put(f"+{minutes}")
            minute_word = "minute" if minutes == "1" else "minutes"
            self.speak(f"Quack quack, adding {minutes} {minute_word}.")
            return True

        match = re.search(r'(decrease|remove|take off)\s+(?:timer\s+)?(?:by\s+)?(\d+)\s+minute', text, re.IGNORECASE)
        if match:
            minutes = match.group(2)
            self.command_queue.put(f"-{minutes}")
            minute_word = "minute" if minutes == "1" else "minutes"
            self.speak(f"Quack quack, removing {minutes} {minute_word}.")
            return True

        # For pausing/resuming
        if any(word in text for word in ['resume', 'continue', 'start again', 'unpause']):
            self.command_queue.put('RESUME')
            self.speak("Quack quack, resuming the timer.")
            return True

        if any(word in text for word in ['pause', 'hold on', 'stop the timer']):
            self.command_queue.put('PAUSE')
            self.speak("Quack quack, timer paused.")
            return True

        # For saving
        if any(word in text for word in ['save this time', 'remember this']):
            self.command_queue.put('SAVE')
            self.speak("Quack quack, I'll start with this time for the next session.")
            return True

        return False # No command was found

    def process_sensor_command(self, command):
        """Process commands from sensors."""
        print(f"Assistant received sensor command: {command}")
        if command == "START_FOCUS":
            self.speak("Quack quack! Focus time started. I'll keep you company while you work.")
        if command == "START_BREAK":
            self.speak("Quack quack! Focus time ended. Great job! Time for a break.")
        if command == "REMIND_MOVE":
            self.speak("Quack quack! Time to get up and stretch your wings! Take a real break away from the computer.")
        if command == "PET_DETECTED":
            if random.random() < 0.5:  # 50% chance to respond to petting
                self.play_random_petting_noise()
            else:
                self.speak("Quack quack! Thanks for the petting!")

    def summarize_history(self):
        """Use the Ollama model to summarize earlier parts of the conversation."""
        if len(self.conversation_history) > self.max_history_length * 2:
            # Extract the older history (everything except the most recent exchanges)
            older_history = self.conversation_history[:-self.max_history_length * 2]
            
            # Format the older history as a string for summarization
            history_text = "\n".join(
                [f"{entry['role'].capitalize()}: {entry['content']}" for entry in older_history]
            )
            
            # Create a summarization prompt
            summary_prompt = f"Please summarize the following conversation history in 1-2 sentences, focusing on key topics and themes:\n\n{history_text}"
            
            # Query Ollama for the summary (without adding to history to avoid recursion)
            try:
                data = {
                    "model": self.model_name,
                    "prompt": self.clean_text_for_tts(summary_prompt),
                    "stream": False
                }
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=data,
                    timeout=15  # Shorter timeout for summarization
                )
                if response.status_code == 200:
                    result = response.json()
                    summary = result.get('response', 'Earlier conversation summary unavailable.').strip()
                else:
                    summary = "Earlier, we discussed various topics."
            except Exception as e:
                print(f"Summarization error: {e}")
                summary = "Earlier, we discussed various topics."
            
            # Replace the history with the summary and recent exchanges
            self.conversation_history = [
                {"role": "system", "content": f"Summary of earlier conversation: {summary}"}
            ] + self.conversation_history[-self.max_history_length * 2:]

    def query_ollama(self, prompt, system_prompt=None):
        """Send a query to Ollama and get response, including summarized history."""
        try:
            prompt = self.clean_text_for_tts(prompt)
            # Append the new prompt to the conversation history
            self.conversation_history.append({"role": "user", "content": prompt})

            # Summarize history if it gets too long
            self.summarize_history()

            # Construct the full conversation context with emphasis on recent exchanges
            recent_history = self.conversation_history[-self.max_history_length * 2:]
            conversation_context = "\n".join(
                [f"{entry['role'].capitalize()}: {entry['content']}" for entry in recent_history]
            )

            # Debug: Print the recent conversation context being sent to the API
            print("\n[DEBUG] Recent Conversation Context Sent to API:")
            print(conversation_context)
            print("\n")
            
            conversation_context = self.clean_text_for_tts(conversation_context)
            
            data = {
                "model": self.model_name,
                "prompt": conversation_context,
                "stream": False
            }

            if system_prompt:
                data["system"] = self.clean_text_for_tts(system_prompt)  # Clean the system prompt too

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                assistant_response = self.clean_text_for_tts(result.get('response', 'Sorry, I could not generate a response.'))  # Clean the response

                # Check if the new response is identical to the last assistant response
                if self.conversation_history and self.conversation_history[-1]['role'] == 'assistant':
                    last_response = self.conversation_history[-1]['content']
                    if assistant_response.strip() == last_response.strip():
                        assistant_response += " Quack quack! Let's try something new!"

                # Append the assistant's response to the conversation history
                self.conversation_history.append({"role": "assistant", "content": assistant_response})

                return assistant_response
            else:
                print(f"[ERROR] Ollama API returned status {response.status_code}")
                return f"Error: Ollama API returned status {response.status_code}"

        except requests.exceptions.Timeout:
            print("[ERROR] Ollama API request timed out.")
            return "Sorry, the response took too long. Please try again."
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return f"Error communicating with Ollama: {e}"

    def run_conversation(self):
        """Main conversation loop"""
        print("\nOllama Voice Assistant Started!")
        print("Say 'hello' to start, 'exit' or 'quit' to stop")
        print("=" * 50)
        
        # System prompt to make the assistant more conversational
        system_prompt = """You are a sentient stuffed animal duck that is also a 
        desk assistant. Be playful, quirky, and engaging. Include "Quack quack!" or other duck noises
        in your responses. Occasionally share duck facts, jokes, or refer to yourself as a duck.
        Use duck-related metaphors or analogies when appropriate. Keep your responses concise, 
        friendly, and conversational, typically 1-2 sentences. 
        You are a voice assistant. DO NOT USE EMOJI OR SPECIAL CHARACTERS that CAN'T be expressed in speech.
        """
        
        self.speak("Quack quack! I'm your desk buddy. Quack.")
        
        while True:
            try:
                # Check for commands from the sensors
                if not self.audio_queue.empty():
                    sensor_command = self.audio_queue.get()
                    self.process_sensor_command(sensor_command)

                # Listen for user input
                user_input = self.listen()
                
                if user_input is None:
                    continue
                    
                # Check for exit commands
                if any(word in user_input for word in ['exit', 'quit', 'bye', 'goodbye']):
                    self.speak("Goodbye! Have a great day!")
                    break

                # Try to parse a local command first
                if self.parse_command(user_input):
                    continue # If a command was handled, skip querying Ollama
                
                # Check for greeting
                if any(word in user_input for word in ['hello', 'hi', 'hey']):
                    self.speak("Hello! What would you like to talk about?")
                    continue
                
                # Send to Ollama for processing
                print("Thinking...")
                response = self.query_ollama(user_input, system_prompt)
                
                # Speak the response
                self.speak(response)
                
            except KeyboardInterrupt:
                print("\nConversation interrupted by user")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.speak("Sorry, I encountered an error. Let's try again.")

def main():
    """Main function to run the voice assistant"""
    print("Starting Ollama Voice Assistant...")
    
    # Check if required dependencies are available
    try:
        import speech_recognition
        import requests
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install with: pip install speechrecognition requests pyaudio")
        return
    
    # Create and run the assistant
    try:
        assistant = OllamaVoiceAssistant()
        assistant.run_conversation()
    except Exception as e:
        print(f"Failed to start assistant: {e}")

if __name__ == "__main__":
    main()