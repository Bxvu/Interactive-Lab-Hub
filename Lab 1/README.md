

# Staging Interaction

\*\***NAME OF COLLABORATOR HERE**\*\*
- Xuesi Chen, Akash Basu, Sean Lewis, Benthan Vu

In the original stage production of Peter Pan, Tinker Bell was represented by a darting light created by a small handheld mirror off-stage, reflecting a little circle of light from a powerful lamp. Tinkerbell communicates her presence through this light to the other characters. See more info [here](https://en.wikipedia.org/wiki/Tinker_Bell). 

There is no actor that plays Tinkerbell--her existence in the play comes from the interactions that the other characters have with her.

For lab this week, we draw on this and other inspirations from theatre to stage interactions with a device where the main mode of display/output for the interactive device you are designing is lighting. You will plot the interaction with a storyboard, and use your computer and a smartphone to experiment with what the interactions will look and feel like. 

_Make sure you read all the instructions and understand the whole of the laboratory activity before starting!_



## Prep

### To start the semester, you will need:
1. Read about Git [here](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F).
2. Set up your own Github "Lab Hub" repository by forking the [Interactive-Lab-Hub repository](https://github.com/FAR-Lab/Interactive-Lab-Hub). To get lab updates, simply [use GitHub's "Sync fork" button when new content is available](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork).

3. Set up the README.md for your Hub repository (for instance, so that it has your name and points to your own Lab 1). You can [learn how to organize and format your README.md here](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax). Make sure to include links to your submissions so they are easy to find.


### For this lab, you will need:
1. Paper
2. Markers/ Pens
3. Scissors
4. Smart Phone -- The main required feature is that the phone needs to have a browser and display a webpage.
5. Computer -- We will use your computer to host a webpage which also features controls.
6. Found objects and materials -- You will have to costume your phone so that it looks like some other devices. These materials can include doll clothes, a paper lantern, a bottle, human clothes, a pillow case, etc. Be creative!

### Deliverables for this lab are: 
1. 7 Storyboards
1. 3 Sketches/photos of costumed devices
1. Any reflections you have on the process
1. Video sketch of 3 prototyped interactions
1. Submit the items above in the lab1 folder of your class [Github page], either as links or uploaded files. Each group member should post their own copy of the work to their own Lab Hub, even if some of the work is the same from each person in the group.

### The Report
This README.md page in your own repository should be edited to include the work you have done (the deliverables mentioned above). Following the format below, you can delete everything but the headers and the sections between the **stars**. Write the answers to the questions under the starred sentences. Include any material that explains what you did in this lab hub folder, and link it in your README.md for the lab.

## Lab Overview
For this assignment, you are going to:

A) [Plan](#part-a-plan) 

B) [Act out the interaction](#part-b-act-out-the-interaction) 

C) [Prototype the device](#part-c-prototype-the-device)

D) [Wizard the device](#part-d-wizard-the-device) 

E) [Costume the device](#part-e-costume-the-device)

F) [Record the interaction](#part-f-record)

Labs are due on Mondays. Make sure this page is linked to on your main class hub page.

## Part A. Plan 

To stage an interaction with your interactive device, think about:

_Setting:_ Where is this interaction happening? (e.g., a jungle, the kitchen) When is it happening?

_Players:_ Who is involved in the interaction? Who else is there? If you reflect on the design of current day interactive devices like the Amazon Alexa, it’s clear they didn’t take into account people who had roommates, or the presence of children. Think through all the people who are in the setting.

_Activity:_ What is happening between the actors?

_Goals:_ What are the goals of each player? (e.g., jumping to a tree, opening the fridge). 

The interactive device can be anything *except* a computer, a tablet computer or a smart phone, but the main way it interacts needs to be using light.

\*\***Describe your setting, players, activity and goals here.**\*\*

### Setting:
The interaction takes place in a lively club environment. The “device” is imagined as part of the club’s lighting system, projecting colors onto a wall or ceiling to signal crowd activity. The time is during an event night when people are actively entering and leaving the space.
### Players:
Club guests who enter and exit the venue.
The interactive device (light system) that responds to the number of people inside.
### Activity:
As people enter or leave the club, the device flashes or changes colors to communicate the change in occupancy. The light system doesn’t just track individual events (entry/exit), but also communicates the current “state” of the crowd with color-coded signals:
Entry → white flash
Exit → black flash
Occupancy thresholds → black, green, yellow, red, or multicolor strobe.
Wave Hand → light brightness/color saturation change.
### Goals:
Guests’ goal: enjoy the experience, understand crowd energy at a glance.
Device’s goal: translate occupancy into an intuitive light signal, keeping everyone aware of the club’s vibe.

Storyboards are a tool for visually exploring a users interaction with a device. They are a fast and cheap method to understand user flow, and iterate on a design before attempting to build on it. Take some time to read through this explanation of [storyboarding in UX design](https://www.smashingmagazine.com/2017/10/storyboarding-ux-design/). Sketch seven storyboards of the interactions you are planning. **It does not need to be perfect**, but must get across the behavior of the interactive device and the other characters in the scene. 

\*\***Include pictures of your storyboards here**\*\*
![Storyboard 1+2+3](part%201a/storyboard1_2_3.png)
![Storyboard 4+5](part%201a/storyboard4_5.png)
![Storyboard 6+7](part%201a/storyboard6_7.png)
![Storyboard 8](part%201a/storyboard8.png)

Present your ideas to the other people in your breakout room (or in small groups). You can just get feedback from one another or you can work together on the other parts of the lab.

\*\***Summarize feedback you got here.**\*\*
1. The flashing for entry/exit events could be distracting if too frequent; maybe consider smoother transitions or subtler effects.
2. Add more spatial features—for example, if people move to a corner of the room, the corresponding light could become brighter to indicate where the crowd is clustering.

## Part B. Act out the Interaction

Try physically acting out the interaction you planned. For now, you can just pretend the device is doing the things you’ve scripted for it.

\*\***Are there things that seemed better on paper than acted out?**\*\*
1. On paper, the rapid flashes for entry/exit events seemed like a fun and clear signal. But when acted out, the flashes felt a bit too distracting and harsh, especially in quick succession. Similarly, the strobe effect at high occupancy looked more overwhelming than energizing in practice—it risked drawing attention away from the actual interaction.

\*\***Are there new ideas that occur to you or your collaborator that come up from the acting?**\*\*
1. Instead of sharp flashes, we could use gentler fades or pulsing lights for entry/exit to make the signals less disruptive.
2. We thought about adding spatial responsiveness, where the lights brighten in the direction or corner of the room that people move toward, giving more context than just occupancy counts.

## Part C. Prototype the device

You will be using your smartphone as a stand-in for the device you are prototyping. You will use the browser of your smart phone to act as a “light” and use a remote control interface to remotely change the light on that device. 

Code for the "Tinkerbelle" tool, and instructions for setting up the server and your phone are [here](https://github.com/IRL-CT/tinkerbelle).

We invented this tool for this lab! 

If you run into technical issues with this tool, you can also use a light switch, dimmer, etc. that you can can manually or remotely control.

\*\***Give us feedback on Tinkerbelle.**\*\*

The app was pretty useful for allowing us to film our demo without having to actually implement it.

## Part D. Wizard the device
Take a little time to set up the wizarding set-up that allows for someone to remotely control the device while someone acts with it. Hint: You can use Zoom to record videos, and you can pin someone’s video feed if that is the scene which you want to record. 

\*\***Include your first attempts at recording the set-up video here.**\*\*

https://drive.google.com/file/d/16q-3w8YigNP197h42Bvn3zztaeE_BG9u/view?usp=drivesdk

Now, change the goal within the same setting, and update the interaction with the paper prototype. 

\*\***Show the follow-up work here.**\*\*

The goal is to flash the screen/lighting to white when someone enters the club.

https://drive.google.com/file/d/1J1FyKKDYUBOAUYOVXfMGRHcnORAxiIA1/view?usp=drivesdk

## Part E. Costume the device

Only now should you start worrying about what the device should look like. Develop three costumes so that you can use your phone as this device.

Think about the setting of the device: is the environment a place where the device could overheat? Is water a danger? Does it need to have bright colors in an emergency setting?

\*\***Include sketches of what your devices might look like here.**\*\*
Prototype #1:
![Sketch Prototype#1](part%201a/sketch1.png)
![Prototype](part%201a/costume1.jpg)
Prototype #2:
![Sketch Prototype#2](part%201a/sketch2.png)
![Prototype](part%201a/costume2-1.jpg)
Prototype #3:
![Sketch Prototype#3](part%201a/sketch3.png)
![Prototype](part%201a/costume3-1.jpg)

\*\***What concerns or opportunitities are influencing the way you've designed the device to look?**\*\*
### Concerns:
The interaction setting requires strong, noticeable lighting. This means the device either needs to achieve higher brightness levels or we may need to use multiple phones as light sources to ensure visibility in a larger or darker environment.
### Opportunitities
The reliance on light opens up creative opportunities for expressive visual effects (color shifts, strobes, gradients) that can enhance the atmosphere. The device can also be scaled by adding more phones or light sources, turning a simple prototype into a flexible system for clubs, bedrooms, or events where light-based cues make the experience more engaging.


## Part F. Record

\*\***Take a video of your prototyped interaction.**\*\*

**Click on the below image to play the video on YouTube**
**Interaction 1**
[![Interaction 1](https://img.youtube.com/vi/8-qJKf9TseE/maxresdefault.jpg)](https://youtu.be/8-qJKf9TseE)
**Interaction 2**
[![Interaction 2](https://img.youtube.com/vi/hpOWgV1T7n8/maxresdefault.jpg)](https://youtu.be/hpOWgV1T7n8)
**Interaction 8**
[![Interaction 8](https://img.youtube.com/vi/70Q2abh3BmU/maxresdefault.jpg)](https://youtu.be/70Q2abh3BmU)
**Music Credit: Seize the Day by Andrey Rossi**
  
\*\***Please indicate who you collaborated with on this Lab.**\*\*
Be generous in acknowledging their contributions! And also recognizing any other influences (e.g. from YouTube, Github, Twitter) that informed your design. 

**Akash Batu: Storyboards #1, #2, #3, #4, #5, Wizarding Tinkerbelle**

**Benthan Vu: Costume #1, Paper Prototype #1, Research & Feedback**

**Carrie Wang: Wizarding the Device, Research & Feedback**

**Evan Fang: Costume #2, Paper Prototype #2, Storyboard #8**

**Sean Lewis: Storyboards #6, #7, Setting up Tinkerbelle**

**Xuesi Chen: Costume #3, Paper Prototype #3, Demo Video Recording and Editing**

****All: Ideating, Research, Video Enactment, Communication

# Staging Interaction, Part 2 

This describes the second week's work for this lab activity.


## Prep (to be done before Lab on Wednesday)

You will be assigned three partners from other groups. Go to their github pages, view their videos, and provide them with reactions, suggestions & feedback: explain to them what you saw happening in their video. Guess the scene and the goals of the character. Ask them about anything that wasn’t clear. 

\*\***Summarize feedback from your partners here.**\*\*
Feedback from a canvas comment said that this seems useful for clubs and security or safety limits. They were unsure of the character goals from the videos and said maybe we could include more people in the demo. 

## Make it your own

Do last week’s assignment again, but this time: 
1) It doesn’t have to (just) use light, 
2) You can use any modality (e.g., vibration, sound) to prototype the behaviors! Again, be creative! Feel free to fork and modify the tinkerbell code! 
3) We will be grading with an emphasis on creativity. 

\*\***Document everything here. (Particularly, we would like to see the storyboard and video, although photos of the prototype are also great.)**\*\*

## New environment
### Setting:
The interaction now takes place in a park. Instead of being a lighting system, this device, in addition to its original goal of keeping count of people exiting and entering, now is used to detect events that may warrant action, such as a small child escaping from their parents sight, or a fight breaking out. 
### Players:
People entering, exiting, and moving around the park.
### Activity:
As people enter or leave the park, the device flashes or changes colors to communicate the change in occupancy. Like before, the light system doesn’t just track individual events (entry/exit), but also communicates the current “state” of the crowd with color-coded signals:
Entry → white flash
Exit → black flash
Occupancy thresholds → black, green, yellow, red, or multicolor strobe.
However, something different from before is that there will be an additional camera/sensor that detects dangerous or harmful events happening in the park, making noise to bring attention to it, or even calling police to help deal with it. 
### Goals:
Guests’ goal: be able to see crowdedness of the park, and be notified of dangerous events nearby.
Device’s goal: translate occupancy into an intuitive light signal, keep watch for dangerous events and notify authorities if needed.

## New storyboards
\*\***Include pictures of your storyboards here**\*\*

### Some extras not shown in the storyboards below
#### Interaction #1 also has beeping noises to alert the parent to follow after their child
#### Interaction #2 additionally calls the cops as well as makes beeping noises
![Storyboard 1-5](part%201b/storyboard1-5.png)
![Storyboard 6-7](part%201b/storyboard6-7.png)

## Device mockups

![Fence](part%201b/direct_light.png)
![Fence2](part%201b/node%20lighting.png)

![Pole](part%201b/red_background.png)
![Pole2](part%201b/yellow.png)
![Pole3](part%201b/green.png)

## New costumes
\*\***Include sketches of what your devices might look like here.**\*\*

Prototype #1:

![Sketch Prototype#1](part%201b/costume1_sketch.png)
![Prototype](part%201b/costume1_1.jpg)
![Prototype](part%201b/costume1_2.jpg)

Prototype #2:

![Sketch Prototype#1](part%201b/costume2_sketch.jpg)
![Prototype](part%201b/costume2_1.jpg)

Prototype #3:

![Sketch Prototype#1](part%201b/costume3_sketch.png)
![Prototype](part%201b/costume3_1.png)

Prototype #4:

![Sketch Prototype#1](part%201b/costume4_sketch.png)
![Prototype](part%201b/costume4_1.jpg)

\*\***What concerns or opportunitities are influencing the way you've designed the device to look?**\*\*
### Concerns:
Since the device is now in the sunlight due to it being in the park, we added a little shade area over the light display in costume 1, to hopefully allow the light color to not be overpowered by sunlight.
### Opportunitities
The reliance on light opens up creative opportunities for expressive visual effects (color shifts, strobes, gradients) that can enhance the atmosphere. At nighttime, having multicolored lights throughout the park can help prevent dangerous events that may have happened to the lack of light. The device can also be scaled by adding more throughout the park, all keeping track of dangerous events and count of people.


## New video demonstrations
\*\***Take a video of your prototyped interaction.**\*\*

**Interaction 1**
[![Interaction 1](https://img.youtube.com/vi/09msoKip1cc/maxresdefault.jpg)](https://youtu.be/09msoKip1cc)
**Interaction 2**
[![Interaction 2](https://img.youtube.com/vi/t-9dse50vPA/maxresdefault.jpg)](https://youtu.be/t-9dse50vPA)
**Interaction 3**
[![Interaction 3](https://img.youtube.com/vi/fyvJGDlQWNw/maxresdefault.jpg)](https://youtu.be/fyvJGDlQWNw)


\*\***Please indicate who you collaborated with on this Lab.**\*\*
Be generous in acknowledging their contributions! And also recognizing any other influences (e.g. from YouTube, Github, Twitter) that informed your design. 

**Akash Batu: Storyboards #1, #2, #3, #4, #5, #6, #7, Video Recorder, Costume #3, Paper Prototype #3**

**Benthan Vu: Costume #1, Paper Prototype #1, Video Participant**

**Carrie Wang: Device Renderings**

**Evan Fang: Costume #4, Paper Prototype #4**

**Sean Lewis: Video Participant, Video Editing**

**Xuesi Chen: Costume #2, Paper Prototype #2**

****All: Ideating, Research, Communication
