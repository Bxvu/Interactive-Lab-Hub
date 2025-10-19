# Chatterboxes

Benthan Vu (bv233)

The main idea of this device is an interactive desk buddy. I have some stuffed animals, and I thought it would be cool if they could provide a purpose more than just looking cute on my desk, so I wanted to make a way for them to respond.

## Part 1

\*\***Write your own shell file to use your favorite of these TTS engines to have your Pi greet you by name.**\*\*
(This shell file should be saved to your own repo for this lab.)

It is saved as part 1/hello.sh

\*\***Write your own shell file that verbally asks for a numerical based input (such as a phone number, zipcode, number of pets, etc) and records the answer the respondent provides.**\*\*

It is in the repository in part 1/input.sh

\*\***Try creating a simple voice interaction that combines speech recognition, Ollama processing, and text-to-speech output. Document what you built and how users responded to it.**\*\*

I used the 2nd example given. After figuring my way around some errors that prevented it from working initially, I told my roommates to say hi to it. It eventually said hi back. Then my housemates asked it some questions like what color is the sky. It had a long response time and this bored the roommates so they left.

\*\***Post your storyboard and diagram here.**\*\*

I imagine the dialogue to be mostly the participant talking to the duck when they are stuck on a problem, asking how they can solve it. I can also imagine them talking to the duck when it asks to be pet or interacted with.

![Storyboard 1](part%201/storyboard_lab3-1.png)
![Storyboard 2](part%201/storyboard_lab3-2.png)
![Verplank Diagram](part%201/verplank_lab3.png)

\*\***Please describe and document your process.**\*\*

My process was I originally wanted to make a stuffed animal that reacted to you. Kind of like how children pretend that their stuffed animals are alive. I wanted to make it more than part of the imagination. But then I realized that probably wouldn't be very interactive. So I thought that instead, the stuffed animal could be like a desk buddy that allows you to set focus/break timers and during breaks ask you to interact with it, like petting it. You could also ask it questions as a way to get another opinion. I then drew out the storyboard and diagram, and asked a classmate to demo the interactions.

\*\***Describe if the dialogue seemed different than what you imagined when it was acted out, and how.**\*\*

[![Interactions](https://img.youtube.com/vi/U9TLJgeX0vk/maxresdefault.jpg)](https://youtu.be/U9TLJgeX0vk)
The dialogue seemed different because I was expecting the participant to be more aggressive towards the duck. I had a script where the participant would ignore the duck or throw it, but neither of those happened. I had to ask the participant to ignore the duck for the demo recording.

\*\***Describe if the dialogue seemed different than what you imagined, or when acted out, when it was wizarded, and how.**\*\*

There were some delays when wizarding the pi to make it say some words. In addition to that, the first part of some voice lines would get cut off so the full sentence wouldn't be heard. I was expecting the participant to not understand, but it looks like he was able to piece together what the duck meant from the few words that did go through.


## Part 2

1. What are concrete things that could use improvement in the design of your device? For example: wording, timing, anticipation of misunderstandings...

Timing of the audio. Last time the start got cut off a few times. Also the voice was a bit hard to understand.

2. What are other modes of interaction _beyond speech_ that you might also use to clarify how to interact?

Physical buttons and sensors like a proximity sensor.

3. Make a new storyboard, diagram and/or script based on these reflections.

![Storyboard 3](part%202/storyboard_lab3-3.png)
![Storyboard 4](part%202/storyboard_lab3-4.png)

*Document how the system works*

The system is a duck themed desk assistant. There are two main functions of it. A focus timer and the duck itself. 

The focus timer has two states: Focus and break time. There are 3 buttons. Button A and B are on the display, and button C is an additonal button added with a wire. Button A and B respectively increase or decrease the timer by a minute. Holding A and B at the same time saves the current time as the starting time for the current state, next time. For example: A and B pressed during focus time with 5:50 minutes left. This save 5:50, and the next time focus starts, after break time, it will start at 5:50. Button C just toggles whether the timer is paused or not. These updates are shown on the display as well.

The duck assistant uses ollama with a stuffed animal duck personality to respond like a duck with duck related sounds. When the user speaks to it, it first checks if the user gave a focus timer command, and updates the timer accordingly. For example users can say commands like "Increase timer by 6 minutes," "Decrease timer by 2 minutes," "pause," "unpause," and "save this time." This will send a command to the focus timer to update itself accordingly. If it doesn't recognize a timer command, then ollama is used to respond to the user, who hopefully is just talking to the stuffed animal about duck things and not code, because it is a duck. The duck also announces when focus and break times are over so the user has an auditory notification. Two additional sensors are also added for the duck. A proximity sensor and an accelerometer. During break time, the proximity sensor is turned on to help the duck detect if the user is still toiling away on their computer instead of actually getting up and taking a break. If it detects the user, it gives them a reminder every minute. The accelerometer is attached to the duck and allows it to detect if the duck is being petted. The duck will respond with a quack or a thanks. Initially there were some wiring conflicts between the extra button and proximity sensor overwriting each others addresses. After some struggle, I fixed it by cutting a small amount of copper tape and redirecting current from the 3.3V to a different address on the button.

### Code

The code for it is in the part 2 folder of this lab. I have also updated the requirements.txt with some new libraries that were needed for sensors. There are 3 python files. One for the `focus_timer.py` system which focuses on updating the timer and getting sensor data, and another for the `voice_assistant.py` which uses ollama and takes in microphone input and is what outputs the audio. The `desk_buddy.py` file runs both at the same time using multithreading and allows them to communicate to each other, such as the focus timer detecting that the duck was petted, and sending a command to the voice assistant so that it can make a response. I also used Google Gemini to help with the code.

To run, make a venv and install the `requirements.txt` in the main Lab 3 folder, then `cd` to part 2 folder and download the duck's voice in that folder using `python -m piper.download_voices en_GB-northern_english_male-medium`
Then run `python desk_buddy.py.`

*Include videos or screencaptures of both the system and the controller.*

*Click Below image for video*
[![Interactions](https://img.youtube.com/vi/xfNk13iH2lo/maxresdefault.jpg)](https://youtu.be/xfNk13iH2lo)
![System 1](part%202/system1.jpg)
![System 2](part%202/system2.jpg)
![System 3](part%202/system3.jpg)
![System 4](part%202/system4.jpg)
![System 5](part%202/system5.jpg)
![System 6](part%202/system6.png)

### What worked well about the system and what didn't?

When the voice recognition understands the timer commands, it works great updating the timer.
Using the desk assistant for short periods, works fine as well. 
What didn't work was chatting with the duck, its responses took too long. Also it was actually a bit too distracting when trying to work.

### What worked well about the controller and what didn't?

The proximity sensor and accelerometer worked great when detecting the user being too close or the duck being pet.
The commands to update the timer were too narrow. The participants sometimes said something very close to an update command, but were like 1 word off. The accelerometer fell off of the duck during one of the tests, and the proximity sensor was very easy to shift out of place. 

### What lessons can you take away from the WoZ interactions for designing a more autonomous version of the system?

I want the duck to be smarter and actually help the user in a conversation like my proof of concept demo from part 1. Unfortunately, if I want the model to respond fast on the pi, the model has to be a bit less smart. I guess to make it smarter I could have it just use an API like from ChatGPT. If the model was smarter, then I could even feed it the sensor data and have it respond dynamically to being pet or detecting the user. The model also spent a lot of time thinking, and not allowing the user to interrupt it, so it would miss their voice commands. So I could add a way to interrupt the model thinking, or if I didn't do that, maybe I could add a light to show that it is thinking and cannot recognize and speech at the moment. 

### How could you use your system to create a dataset of interaction? What other sensing modalities would make sense to capture?

I could use my system to create a dataset of interaction by maybe saving the proximity data and accelerometer and the time it was recorded to see how often users keep working during break time, and how often they pet the duck. I could also capture the data from whether users use voice commands or just press buttons to see which one is more useful. 







