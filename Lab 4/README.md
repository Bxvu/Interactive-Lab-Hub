
# Ph-UI!!!

<details>
	<summary><strong>Instructions for Students (Click to Expand)</strong></summary>
  
	**Submission Cleanup Reminder:**
	- This README.md contains extra instructional text for guidance.
	- Before submitting, remove all instructional text and example prompts from this file.
	- You may delete these sections or use the toggle/hide feature in VS Code to collapse them for a cleaner look.
	- Your final submission should be neat, focused on your own work, and easy to read for grading.
  
	This helps ensure your README.md is clear, professional, and uniquely yours!
</details>

---
<details>
	<summary><strong>Deliverables</strong></summary>
## Lab 4 Deliverables

### Part 1 (Week 1)
**Submit the following for Part 1:**  
*️⃣ **A. Capacitive Sensing**
	- Photos/videos of your Twizzler (or other object) capacitive sensor setup
	- Code and terminal output showing touch detection

*️⃣ **B. More Sensors**
	- Photos/videos of each sensor tested (light/proximity, rotary encoder, joystick, distance sensor)
	- Code and terminal output for each sensor

*️⃣ **C. Physical Sensing Design**
	- 5 sketches of different ways to use your chosen sensor
	- Written reflection: questions raised, what to prototype
	- Pick one design to prototype and explain why

*️⃣ **D. Display & Housing**
	- 5 sketches for display/button/knob positioning
	- Written reflection: questions raised, what to prototype
	- Pick one display design to integrate
	- Rationale for design
	- Photos/videos of your cardboard prototype

---

### Part 2 (Week 2)
**Submit the following for Part 2:**  
*️⃣ **E. Multi-Device Demo**
	- Code and video for your multi-input multi-output demo (e.g., chaining Qwiic buttons, servo, GPIO expander, etc.)
	- Reflection on interaction effects and chaining

*️⃣ **F. Final Documentation**
	- Photos/videos of your final prototype
	- Written summary: what it looks like, works like, acts like
	- Reflection on what you learned and next steps

---
</details>

## Lab Overview
**NAMES OF COLLABORATORS HERE**
Benthan Vu (bv233) (I think I was too ambitious, I should've gotten a teammate...)

<details>
	<summary><strong>Instructions</strong></summary>
For lab this week, we focus both on sensing, to bring in new modes of input into your devices, as well as prototyping the physical look and feel of the device. You will think about the physical form the device needs to perform the sensing as well as present the display or feedback about what was sensed. 

## Part 1 Lab Preparation

### Get the latest content:
As always, pull updates from the class Interactive-Lab-Hub to both your Pi and your own GitHub repo. As we discussed in the class, there are 2 ways you can do so:


Option 1: On the Pi, `cd` to your `Interactive-Lab-Hub`, pull the updates from upstream (class lab-hub) and push the updates back to your own GitHub repo. You will need the personal access token for this.
```
pi@ixe00:~$ cd Interactive-Lab-Hub
pi@ixe00:~/Interactive-Lab-Hub $ git pull upstream Fall2025
pi@ixe00:~/Interactive-Lab-Hub $ git add .
pi@ixe00:~/Interactive-Lab-Hub $ git commit -m "get lab4 content"
pi@ixe00:~/Interactive-Lab-Hub $ git push
```

Option 2: On your own GitHub repo, [create pull request](https://github.com/FAR-Lab/Developing-and-Designing-Interactive-Devices/blob/2021Fall/readings/Submitting%20Labs.md) to get updates from the class Interactive-Lab-Hub. After you have latest updates online, go on your Pi, `cd` to your `Interactive-Lab-Hub` and use `git pull` to get updates from your own GitHub repo.

Option 3: (preferred) use the Github.com interface to update the changes.

### Start brainstorming ideas by reading: 

* [What do prototypes prototype?](https://www.semanticscholar.org/paper/What-do-Prototypes-Prototype-Houde-Hill/30bc6125fab9d9b2d5854223aeea7900a218f149)
* [Paper prototyping](https://www.uxpin.com/studio/blog/paper-prototyping-the-practical-beginners-guide/) is used by UX designers to quickly develop interface ideas and run them by people before any programming occurs. 
* [Cardboard prototypes](https://www.youtube.com/watch?v=k_9Q-KDSb9o) help interactive product designers to work through additional issues, like how big something should be, how it could be carried, where it would sit. 
* [Tips to Cut, Fold, Mold and Papier-Mache Cardboard](https://makezine.com/2016/04/21/working-with-cardboard-tips-cut-fold-mold-papier-mache/) from Make Magazine.
* [Surprisingly complicated forms](https://www.pinterest.com/pin/50032245843343100/) can be built with paper, cardstock or cardboard.  The most advanced and challenging prototypes to prototype with paper are [cardboard mechanisms](https://www.pinterest.com/helgangchin/paper-mechanisms/) which move and change. 
* [Dyson Vacuum Cardboard Prototypes](http://media.dyson.com/downloads/JDF/JDF_Prim_poster05.pdf)
<p align="center"><img src="https://dysonthedesigner.weebly.com/uploads/2/6/3/9/26392736/427342_orig.jpg"  width="200" > </p>

### Gathering materials for this lab:

* Cardboard (start collecting those shipping boxes!)
* Found objects and materials--like bananas and twigs.
* Cutting board
* Cutting tools
* Markers


(We do offer shared cutting board, cutting tools, and markers on the class cart during the lab, so do not worry if you don't have them!)

## Deliverables \& Submission for Lab 4

The deliverables for this lab are, writings, sketches, photos, and videos that show what your prototype:
* "Looks like": shows how the device should look, feel, sit, weigh, etc.
* "Works like": shows what the device can do.
* "Acts like": shows how a person would interact with the device.

For submission, the readme.md page for this lab should be edited to include the work you have done:
* Upload any materials that explain what you did, into your lab 4 repository, and link them in your lab 4 readme.md.
* Link your Lab 4 readme.md in your main Interactive-Lab-Hub readme.md. 
* Labs are due on Mondays, make sure to submit your Lab 4 readme.md to Canvas.
</details>


## Lab Overview

A) [Capacitive Sensing](#part-a)

B) [OLED screen](#part-b) 

C) [Paper Display](#part-c)

D) [Materiality](#part-d)

E) [Servo Control](#part-e)

F) [Record the interaction](#part-f)

<details>
	<summary><strong>Instructions</strong></summary>
## The Report (Part 1: A-D, Part 2: E-F)

### Quick Start: Python Environment Setup

1. **Create and activate a virtual environment in Lab 4:**
	```bash
	cd ~/Interactive-Lab-Hub/Lab\ 4
	python3 -m venv .venv
	source .venv/bin/activate
	```
2. **Install all Lab 4 requirements:**
	```bash
	pip install -r requirements2025.txt
	```
3. **Check CircuitPython Blinka installation:**
	```bash
	python blinkatest.py
	```
	If you see "Hello blinka!", your setup is correct. If not, follow the troubleshooting steps in the file or ask for help.
</details>

### Part A
### Capacitive Sensing, a.k.a. Human-Twizzler Interaction 
<details>
<summary><strong>Instructions</strong></summary>

We want to introduce you to the [capacitive sensor](https://learn.adafruit.com/adafruit-mpr121-gator) in your kit. It's one of the most flexible input devices we are able to provide. At boot, it measures the capacitance on each of the 12 contacts. Whenever that capacitance changes, it considers it a user touch. You can attach any conductive material. In your kit, you have copper tape that will work well, but don't limit yourself! In the example below, we use Twizzlers--you should pick your own objects.


<p float="left">
<img src="https://cdn-learn.adafruit.com/guides/cropped_images/000/003/226/medium640/MPR121_top_angle.jpg?1609282424" height="150" />
 
</p>

Plug in the capacitive sensor board with the QWIIC connector. Connect your Twizzlers with either the copper tape or the alligator clips (the clips work better). Install the latest requirements from your working virtual environment:

These Twizzlers are connected to pads 6 and 10. When you run the code and touch a Twizzler, the terminal will print out the following

```
(circuitpython) pi@ixe00:~/Interactive-Lab-Hub/Lab 4 $ python cap_test.py 
Twizzler 10 touched!
Twizzler 6 touched!
```
</details>

![Capacitor](part%201/cap.jpg)

*Click Below image for video*

[![Interactions](https://img.youtube.com/vi/I6tdIZzLYfs/maxresdefault.jpg)](https://youtu.be/I6tdIZzLYfs)

### Part B
### More sensors
<details>
<summary><strong>Instructions</strong></summary>
#### Light/Proximity/Gesture sensor (APDS-9960)

We here want you to get to know this awesome sensor [Adafruit APDS-9960](https://www.adafruit.com/product/3595). It is capable of sensing proximity, light (also RGB), and gesture! 
 
<img src="https://cdn-shop.adafruit.com/970x728/3595-06.jpg" width=200>
 

Connect it to your pi with Qwiic connector and try running the three example scripts individually to see what the sensor is capable of doing!

```
(circuitpython) pi@ixe00:~/Interactive-Lab-Hub/Lab 4 $ python proximity_test.py
...
(circuitpython) pi@ixe00:~/Interactive-Lab-Hub/Lab 4 $ python gesture_test.py
...
(circuitpython) pi@ixe00:~/Interactive-Lab-Hub/Lab 4 $ python color_test.py
...
```

You can go the the [Adafruit GitHub Page](https://github.com/adafruit/Adafruit_CircuitPython_APDS9960) to see more examples for this sensor!
</details>

![proxcolorgest](part%201/proxcolorgesture.jpg)

*Click Below image for videos*

[![prox](https://img.youtube.com/vi/MyS7XXwDgcQ/maxresdefault.jpg)](https://youtu.be/MyS7XXwDgcQ)
[![color](https://img.youtube.com/vi/dEJ8L7eb9eM/maxresdefault.jpg)](https://youtu.be/dEJ8L7eb9eM)
[![gest](https://img.youtube.com/vi/YtqIwmAK8Q8/maxresdefault.jpg)](https://youtu.be/YtqIwmAK8Q8)

#### Rotary Encoder 
<details>
<summary><strong>Instructions</strong></summary>
A rotary encoder is an electro-mechanical device that converts the angular position to analog or digital output signals. The [Adafruit rotary encoder](https://www.adafruit.com/product/4991#technical-details) we ordered for you came with separate breakout board and encoder itself, that is, they will need to be soldered if you have not yet done so! We will be bringing the soldering station to the lab class for you to use, also, you can go to the MakerLAB to do the soldering off-class. Here is some [guidance on soldering](https://learn.adafruit.com/adafruit-guide-excellent-soldering/preparation) from Adafruit. When you first solder, get someone who has done it before (ideally in the MakerLAB environment). It is a good idea to review this material beforehand so you know what to look at.

<p float="left">

   
<img src="https://cdn-shop.adafruit.com/970x728/377-02.jpg" height="200" />
<img src="https://cdn-shop.adafruit.com/970x728/4991-09.jpg" height="200">
</p>

Connect it to your pi with Qwiic connector and try running the example script, it comes with an additional button which might be useful for your design!

```
(circuitpython) pi@ixe00:~/Interactive-Lab-Hub/Lab 4 $ python encoder_test.py
```

You can go to the [Adafruit Learn Page](https://learn.adafruit.com/adafruit-i2c-qt-rotary-encoder/python-circuitpython) to learn more about the sensor! The sensor actually comes with an LED (neo pixel): Can you try lighting it up? 
</details>

![encoder](part%201/encoder.jpg)

*Click Below image for video*

[![encoder](https://img.youtube.com/vi/4RZHMMwM74Q/maxresdefault.jpg)](https://youtu.be/4RZHMMwM74Q)

#### Joystick 
<details>
<summary><strong>Instructions</strong></summary>

A [joystick](https://www.sparkfun.com/products/15168) can be used to sense and report the input of the stick for it pivoting angle or direction. It also comes with a button input!

<p float="left">
<img src="https://cdn.sparkfun.com//assets/parts/1/3/5/5/8/15168-SparkFun_Qwiic_Joystick-01.jpg" height="200" />
</p>

Connect it to your pi with Qwiic connector and try running the example script to see what it can do!

```
(circuitpython) pi@ixe00:~/Interactive-Lab-Hub/Lab 4 $ python joystick_test.py
```

You can go to the [SparkFun GitHub Page](https://github.com/sparkfun/Qwiic_Joystick_Py) to learn more about the sensor!
</details>

![joystick](part%201/joystick.jpg)

*Click Below image for video*

[![joystick](https://img.youtube.com/vi/k3Qw6kJv3Qc/maxresdefault.jpg)](https://youtu.be/k3Qw6kJv3Qc)

#### Distance Sensor
<details>
<summary><strong>Instructions</strong></summary>

Earlier we have asked you to play with the proximity sensor, which is able to sense objects within a short distance. Here, we offer [Sparkfun Proximity Sensor Breakout](https://www.sparkfun.com/products/15177), With the ability to detect objects up to 20cm away.

<p float="left">
<img src="https://cdn.sparkfun.com//assets/parts/1/3/5/9/2/15177-SparkFun_Proximity_Sensor_Breakout_-_20cm__VCNL4040__Qwiic_-01.jpg" height="200" />

</p>

Connect it to your pi with Qwiic connector and try running the example script to see how it works!

```
(circuitpython) pi@ixe00:~/Interactive-Lab-Hub/Lab 4 $ python qwiic_distance.py
```

You can go to the [SparkFun GitHub Page](https://github.com/sparkfun/Qwiic_Proximity_Py) to learn more about the sensor and see other examples
</details>

![distance](part%201/distance.jpg)

*Click Below image for video*

[![distance](https://img.youtube.com/vi/kKaXwxZhD78/maxresdefault.jpg)](https://youtu.be/kKaXwxZhD78)

### Part C
### Physical considerations for sensing
<details>
<summary><strong>Instructions</strong></summary>

Usually, sensors need to be positioned in specific locations or orientations to make them useful for their application. Now that you've tried a bunch of the sensors, pick one that you would like to use, and an application where you use the output of that sensor for an interaction. For example, you can use a distance sensor to measure someone's height if you position it overhead and get them to stand under it.
</details>

**\*\*\*Draw 5 sketches of different ways you might use your sensor, and how the larger device needs to be shaped in order to make the sensor useful.\*\*\***

![sketches](part%201/p1c_sketches.png)

**\*\*\*What are some things these sketches raise as questions? What do you need to physically prototype to understand how to anwer those questions?\*\*\***

One question these sketches raise is how am I going to get a bigger screen for some of the ideas. Another question is how I am going to connect a sensor from far away if I have a bigger screen. For Idea #5, I saw the sensor is very accurate in collecting a range of colors, so I need to figure out if I want to save all of them, or save them within a certain threshold, like steps. For idea #3, I need to think about how to increase the force of the bowling ball throw if the sensor can only sense directions and not how fast the gesture was done. What I need to physically prototype is how far I can put a sensor away from the raspberry pi, and how I can make it so that the display is upright in a position that is easy for people to see. For the specific questions like I have for idea #3 and #5, I think I would need to deal with that in software instead of a physical prototype.

**\*\*\*Pick one of these designs to prototype.\*\*\***

I will pick the bowling game. I think it provides the most interactivity of all the ideas I thought of.

### Part D
### Physical considerations for displaying information and housing parts
<details>
<summary><strong>Instructions</strong></summary>

Here is a Pi with a paper faceplate on it to turn it into a display interface:


<img src="https://github.com/FAR-Lab/Developing-and-Designing-Interactive-Devices/blob/2020Fall/images/paper_if.png?raw=true"  width="250"/>


This is fine, but the mounting of the display constrains the display location and orientation a lot. Also, it really only works for applications where people can come and stand over the Pi, or where you can mount the Pi to the wall.

Here is another prototype for a paper display:

<img src="https://github.com/FAR-Lab/Developing-and-Designing-Interactive-Devices/blob/2020Fall/images/b_box.png?raw=true"  width="250"/>


Your kit includes these [SparkFun Qwiic OLED screens](https://www.sparkfun.com/products/17153). These use less power than the MiniTFTs you have mounted on the GPIO pins of the Pi, but, more importantly, they can be more flexibly mounted elsewhere on your physical interface. The way you program this display is almost identical to the way you program a  Pi display. Take a look at `oled_test.py` and some more of the [Adafruit examples](https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/tree/master/examples).

<p float="left">
<img src="https://cdn.sparkfun.com//assets/parts/1/6/1/3/5/17153-SparkFun_Qwiic_OLED_Display__0.91_in__128x32_-01.jpg" height="200" />

</p>


It holds a Pi and usb power supply, and provides a front stage on which to put writing, graphics, LEDs, buttons or displays.

This design can be made by scoring a long strip of corrugated cardboard of width X, with the following measurements:

| Y height of box <br> <sub><sup>- thickness of cardboard</sup></sub> | Z  depth of box <br><sub><sup>- thickness of cardboard</sup></sub> | Y height of box  | Z  depth of box | H height of faceplate <br><sub><sup>* * * * * (don't make this too short) * * * * *</sup></sub>|
| --- | --- | --- | --- | --- | 

Fold the first flap of the strip so that it sits flush against the back of the face plate, and tape, velcro or hot glue it in place. This will make a H x X interface, with a box of Z x X footprint (which you can adapt to the things you want to put in the box) and a height Y in the back. 

Here is an example:

<img src="https://github.com/FAR-Lab/Developing-and-Designing-Interactive-Devices/blob/2020Fall/images/horoscope.png?raw=true"  width="250"/>

Think about how you want to present the information about what your sensor is sensing! Design a paper display for your project that communicates the state of the Pi and a sensor. Ideally you should design it so that you can slide the Pi out to work on the circuit or programming, and then slide it back in and reattach a few wires to be back in operation.
</details>

**\*\*\*Sketch 5 designs for how you would physically position your display and any buttons or knobs needed to interact with it.\*\*\***

![sketches](part%201/p1d_sketches.png)

**\*\*\*What are some things these sketches raise as questions? What do you need to physically prototype to understand how to anwer those questions?\*\*\***

Some things these sketches raise as questions are how I can connect my pi to a projector or TV. If I am not going to use a big screen, just the 2 pi screens, then how can I make it so the screen can be positioned higher in such a way that the user doesn't need to look down that far. What I need to physically prototype is making a box that can hold the pi and connect to its sensors, as well as having an extended part that goes upward for the displays in designs 1, 4, and 5. For designs 2 and 3, I have a projector and also can try to use the TV in the House rooftop to see if I can display the pi screen. 

**\*\*\*Pick one of these display designs to integrate into your prototype.\*\*\***

I will integrate design 3. It will have the whole game in one large screen. And then additional game information on the two displays connected to the pi.

**\*\*\*Explain the rationale for the design.\*\*\*** (e.g. Does it need to be a certain size or form or need to be able to be seen from a certain distance?)

The rationale for design 3 is that it will be easier to see the screen if it's projected onto a bigger area. It will also provide a better sense of bowling since the screen is bigger and hopefully immerse the user better, even though the throwing part wont be similar to bowling at all. The wall needs to be at least 5 ft away from the projector, but the pi can be right next to it. The sensor as well. 

Build a cardboard prototype of your design.

**\*\*\*Document your rough prototype.\*\*\***

First I made a slanted box thing so the user doesn't need to look straight down.

![image](part%201/p1_triangle_stand.jpg)

I then attached the pi and its screen. I made some boxes for them so they don't look like fully exposed circuitry.

![image](part%201/p1_screens.jpg)

After that I also attached the gesture sensor.

![image](part%201/p1_prototype.jpg)

Finally, I connected the pi to my projector, and it seems like the display worked. Here is the final prototype, looks similar to the design I sketched, but I moved the trangle display stand slightly away from the projector so it doesn't overheat, since I saw it has a fan on its back.

![image](part%201/p1_front_view.jpg)
![image](part%201/p1_side_view.jpg)

Also here is a bunch of scraps from all the cutting I had to do to figure out what would work best.

![image](part%201/p1_scraps.jpg)

# LAB PART 2

### Part 2

Following exploration and reflection from Part 1, complete the "looks like," "works like" and "acts like" prototypes for your design, reiterated below.



### Part E

#### Chaining Devices and Exploring Interaction Effects

My device is a bowling game. It uses 3 sensors. The joystick, rotary encoder, and gesture sensor. It outputs to a game screen, the speaker, and a couple of LEDs. 
Here is a picture of the sensors the device uses:

![image](part%202/submission/sensors1.jpg)

##### Code

The code is split into two main files in the part 2 folder. All the sensor initialization and data collection for the joystick, encoder, gesture detector, and controlling the LEDS on the breadboard is in `sensors.py` while the game state of the game like the amount of pins remaining is in `bowling_game.py`. I have also updated `requirements2025.txt` with libraries needed for my prototype. Google Gemini helped with the code too. 

To run the game, install the requirements in a venv, and then cd to the part 2 folder and run `python bowling_game.py`. Also You need the sensors and breadboard also connected to the pi or else it won't work. 

##### Prototype In Action

*Click Below image for video*
[![Interactions](https://img.youtube.com/vi/RBoHuEK0bSc/maxresdefault.jpg)](https://youtu.be/RBoHuEK0bSc)
More interaction can be seen in following video demos further below

##### Sketch of Connections

![image](part%202/submission/lab4_sketch.png)
![image](part%202/submission/lab4_interactions.png)

##### Reflection

I spent multiple hours trying to figure out how to use the breadboard and GPIO expander. There were no instructions on the Lab Hub so I had to look online. I only had LEDS with 4 legs and some resistors, but most of the tutorials told me to also use jumper cables and an LED with two legs. I guess that's due to me not knowing exactly what was required when I got some of the materials during Lab time. So because of that, I decided to go to the MakerLab and hope that they had the missing pieces. They did, and I was able to get to work. Because I had never worked with wires before, it took a long time figuring out the combinations of where to place things. I repeatedly asked Google Gemini to help me, but its responses were confusing and sometimes the pi would shut down randomly. All the tutorials I opened connected the breadboard directly to the pi with jumper cables, but I wanted to use the GPIO expander since the screen was in the way of the pins on the pi. Eventually I got a LED to work, and that led to me finally figuring out how to use the GPIO expander.

![image](part%202/submission/leds1.jpg)

Here is a video of my progression *Click Below image for video*
[![Interactions](https://img.youtube.com/vi/ZdTUadfNn1A/maxresdefault.jpg)](https://youtu.be/ZdTUadfNn1A)

Final Setup: 

![image](part%202/submission/led_setup.jpg)

What I learned about multi-input/multi-output interaction was that most of the time, having one sensor by itself works great, but then when you add them together, sometimes their addresses can conflict, causing errors. This seems to mainly happen when chaining together sensors from different companies. The joystick and the GPIO expander had this issue, as the joystick was from Adafruit while the expander was from Qwiic. I tried changing the address of the expander with copper tape, like how I was able to do it with the LED button in a previous lab, but this time it didn't work. I asked Google Gemini how I could change the address, and it said to use jumper cables. That did work, but unfortunately the only way I could get the address to change was to position the cables in a fragile position. So one tap and they would fall off. 

Here is an image of my attempt to use copper tape to change the expander address.

![image](part%202/submission/copper_tape.jpg)


<details>
	<summary><strong>Instructions</strong></summary>

For Part 2, you will design and build a fun interactive prototype using multiple inputs and outputs. This means chaining Qwiic and STEMMA QT devices (e.g., buttons, encoders, sensors, servos, displays) and/or combining with traditional breadboard prototyping (e.g., LEDs, buzzers, etc.).

**Your prototype should:**
- Combine at least two different types of input and output devices, inspired by your physical considerations from Part 1.
- Be playful, creative, and demonstrate multi-input/multi-output interaction.

**Document your system with:**
- Code for your multi-device demo
- Photos and/or video of the working prototype in action
- A simple interaction diagram or sketch showing how inputs and outputs are connected and interact
- Written reflection: What did you learn about multi-input/multi-output interaction? What was fun, surprising, or challenging?

**Questions to consider:**
- What new types of interaction become possible when you combine two or more sensors or actuators?
- How does the physical arrangement of devices (e.g., where the encoder or sensor is placed) change the user experience?
- What happens if you use one device to control or modulate another (e.g., encoder sets a threshold, sensor triggers an action)?
- How does the system feel if you swap which device is "primary" and which is "secondary"?

Try chaining different combinations and document what you discover!

See encoder_accel_servo_dashboard.py in the Lab 4 folder for an example of chaining together three devices.

**`Lab 4/encoder_accel_servo_dashboard.py`**

#### Using Multiple Qwiic Buttons: Changing I2C Address (Physically & Digitally)

If you want to use more than one Qwiic Button in your project, you must give each button a unique I2C address. There are two ways to do this:

##### 1. Physically: Soldering Address Jumpers

On the back of the Qwiic Button, you'll find four solder jumpers labeled A0, A1, A2, and A3. By bridging these with solder, you change the I2C address. Only one button on the chain can use the default address (0x6F).

**Address Table:**

| A3 | A2 | A1 | A0 | Address (hex) |
|----|----|----|----|---------------|
|  0 |  0 |  0 |  0 |    0x6F       |
|  0 |  0 |  0 |  1 |    0x6E       |
|  0 |  0 |  1 |  0 |    0x6D       |
|  0 |  0 |  1 |  1 |    0x6C       |
|  0 |  1 |  0 |  0 |    0x6B       |
|  0 |  1 |  0 |  1 |    0x6A       |
|  0 |  1 |  1 |  0 |    0x69       |
|  0 |  1 |  1 |  1 |    0x68       |
|  1 |  0 |  0 |  0 |    0x67       |
| ...| ...| ...| ... |     ...      |

For example, if you solder A0 closed (leave A1, A2, A3 open), the address becomes 0x6E.

**Soldering Tips:**
- Use a small amount of solder to bridge the pads for the jumper you want to close.
- Only one jumper needs to be closed for each address change (see table above).
- Power cycle the button after changing the jumper.

##### 2. Digitally: Using Software to Change Address

You can also change the address in software (temporarily or permanently) using the example script `qwiic_button_ex6_changeI2CAddress.py` in the Lab 4 folder. This is useful if you want to reassign addresses without soldering.

Run the script and follow the prompts:
```bash
python qwiic_button_ex6_changeI2CAddress.py
```
Enter the new address (e.g., 5B for 0x5B) when prompted. Power cycle the button after changing the address.

**Note:** The software method is less foolproof and you need to make sure to keep track of which button has which address!


##### Using Multiple Buttons in Code

After setting unique addresses, you can use multiple buttons in your script. See these example scripts in the Lab 4 folder:

- **`qwiic_1_button.py`**: Basic example for reading a single Qwiic Button (default address 0x6F). Run with:
	```bash
	python qwiic_1_button.py
	```

- **`qwiic_button_led_demo.py`**: Demonstrates using two Qwiic Buttons at different addresses (e.g., 0x6F and 0x6E) and controlling their LEDs. Button 1 toggles its own LED; Button 2 toggles both LEDs. Run with:
	```bash
	python qwiic_button_led_demo.py
	```

Here is a minimal code example for two buttons:
```python
import qwiic_button

# Default button (0x6F)
button1 = qwiic_button.QwiicButton()
# Button with A0 soldered (0x6E)
button2 = qwiic_button.QwiicButton(0x6E)

button1.begin()
button2.begin()

while True:
		if button1.is_button_pressed():
				print("Button 1 pressed!")
		if button2.is_button_pressed():
				print("Button 2 pressed!")
```

For more details, see the [Qwiic Button Hookup Guide](https://learn.sparkfun.com/tutorials/qwiic-button-hookup-guide/all#i2c-address).

---

### PCF8574 GPIO Expander: Add More Pins Over I²C

Sometimes your Pi’s header GPIO pins are already full (e.g., with a display or HAT). That’s where an I²C GPIO expander comes in handy.

We use the Adafruit PCF8574 I²C GPIO Expander, which gives you 8 extra digital pins over I²C. It’s a great way to prototype with LEDs, buttons, or other components on the breadboard without worrying about pin conflicts—similar to how Arduino users often expand their pinouts when prototyping physical interactions.

**Why is this useful?**
- You only need two wires (I²C: SDA + SCL) to unlock 8 extra GPIOs.
- It integrates smoothly with CircuitPython and Blinka.
- It allows a clean prototyping workflow when the Pi’s 40-pin header is already occupied by displays, HATs, or sensors.
- Makes breadboard setups feel more like an Arduino-style prototyping environment where it’s easy to wire up interaction elements.

**Demo Script:** `Lab 4/gpio_expander.py`

<p align="center">
    <img src="gpio_leds.gif" alt="GPIO Expander LED Demo" width="400"/>
</p>

We connected 8 LEDs (through 220 Ω resistors) to the expander and ran a little light show. The script cycles through three patterns:
- Chase (one LED at a time, left to right)
- Knight Rider (back-and-forth sweep)
- Disco (random blink chaos)

Every few runs, the script swaps to the next pattern automatically:
```bash
python gpio_expander.py
```

This is a playful way to visualize how the expander works, but the same technique applies if you wanted to prototype buttons, switches, or other interaction elements. It’s a lightweight, flexible addition to your prototyping toolkit.

---

### Servo Control with SparkFun Servo pHAT
For this lab, you will use the **SparkFun Servo pHAT** to control a micro servo (such as the Miuzei MS18 or similar 9g servo). The Servo pHAT stacks directly on top of the Adafruit Mini PiTFT (135×240) display without pin conflicts:
- The Mini PiTFT uses SPI (GPIO22, 23, 24, 25) for display and buttons ([SPI pinout](https://pinout.xyz/pinout/spi)).
- The Servo pHAT uses I²C (GPIO2 & 3) for the PCA9685 servo driver ([I2C pinout](https://pinout.xyz/pinout/i2c)).
- Since SPI and I²C are separate buses, you can use both boards together.
**⚡ Power:**
- Plug a USB-C cable into the Servo pHAT to provide enough current for the servos. The Pi itself should still be powered by its own USB-C supply. Do NOT power servos from the Pi’s 5V rail.

<p align="center">
    <img src="Servo_pHAT.gif" alt="Servo pHAT Demo" width="400"/>
</p>

**Basic Python Example:**
We provide a simple example script: `Lab 4/pi_servo_hat_test.py` (requires the `pi_servo_hat` Python package).
Run the example:
```
python pi_servo_hat_test.py
```
For more details and advanced usage, see the [official SparkFun Servo pHAT documentation](https://learn.sparkfun.com/tutorials/pi-servo-phat-v2-hookup-guide/all#resources-and-going-further).
A servo motor is a rotary actuator that allows for precise control of angular position. The position is set by the width of an electrical pulse (PWM). You can read [this Adafruit guide](https://learn.adafruit.com/adafruit-arduino-lesson-14-servo-motors/servo-motors) to learn more about how servos work.

---
</details>


### Part F

### Record

<details>
	<summary><strong>Instructions</strong></summary>
Document all the prototypes and iterations you have designed and worked on! Again, deliverables for this lab are writings, sketches, photos, and videos that show what your prototype:
* "Looks like": shows how the device should look, feel, sit, weigh, etc.
* "Works like": shows what the device can do
* "Acts like": shows how a person would interact with the device
</details>

**Looks like**

The prototype I made for part 1 of the lab seemed a bit too steep for all the sensors and stuff added to it, so I made a new prototype that is still slanted, but not as much. It is made of two layers, so that the wires that need to connect to the pi, which are the power and hdmi cables, can go beneath the sensors instead of crossing over them. If you look closely, I also added some screws to the sensors to make sure they don't go out of place when the player turns or rotates them. The device should sit next to the projector or screen that has the bowling game, hopefully so the player can simply look up to see whats happening. 

![image](part%202/submission/final_device_top.jpg)

![image](part%202/submission/final_device_side.jpg)

**Works like**

The device is kind of like a controller for the bowling game made specifically for it. I was envisioning it kind of working like an arcade cabinet game with all these different input devices. Basically the user can move the ball left and right or rotate it at the start of the lane. Then when they are ready they can swipe up over the gesture sensor to throw the ball. Then the ball is thrown and there are some simple physics for the cones that it hits. When all pins are knocked over, the user wins and the game resets. There are also sound effects for when the ball is thrown, when a pin is hit, and when the player wins. Additionally, in the win state, the LEDs flash as a celebratory action.

*Click Below image for video*
[![Interactions](https://img.youtube.com/vi/UMPQX-aOaxM/maxresdefault.jpg)](https://youtu.be/UMPQX-aOaxM)

**Acts like**

Here is a video of interactions with users. I was trying to fix my LEDs before it so I forgot to bring the speaker and they didn't get to experience audio output, but they were able to see most of the device. Overall it seemed pretty intuitive for the users, as they were able to rotate, move, and throw the ball at the pins until they won.

[![Interactions](https://img.youtube.com/vi/BQRtVDMC7cQ/maxresdefault.jpg)](https://youtu.be/BQRtVDMC7cQ)

##### Final Thoughts

If there was a better more robust way to have my LED lights, I would like to learn about it. They worked fine when I first set them up in the makerlab, but later, after walking home, the wires shifted and sometimes the lights wouldn't work. There must be a better way to hold them in place. Also the placement of the gesture sensor and breadboard could be changed. I didn't think about how the jumper wire that changes the GPIO expander's address may interfere with the user's swipe upwards. If I could learn a better way to change the expander's address that would be nice too. Some feedback from users is that I should remove the red cube, change some of the font color of the game, and add more bounciness to the ball. The projector placement also was kind of bad during one user test since many of the outlets I tried to connect to in the room did not work except for one next to a wall, away from any table. Also there was still too much daylight so the screen was hard to see. The last test I did connected to a TV which seemed a bit better but the pi had to be close to it due to wire limited wire lengths.
