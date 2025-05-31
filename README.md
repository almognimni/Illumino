[Canva Presentation](https://www.canva.com/design/DAGnU78_K-o/1K60Z6Pj0uzDGjTP4mFYaA/view?utm_content=DAGnU78_K-o&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h79417e2b24#1)


- Introduction
   - Objective
   - Example Scenario
   - High-Level Design
   - Features
   - MP3 to MIDI conversion
   - Scenarios
   - Flow
- Design
   - The components
   - Client - server architecture
      - 1. Server (Raspberry Pi)
      - 2. Client (Web Interface)
   - The DB (in the raspberry) contains the following fields
   - packages


## Introduction

playing musical instruments like the piano can be a daunting challenge for
beginners. Traditional lessons often require significant financial investment and
commitment, which can deter many potential learners. Our project addresses
these barriers by providing an affordable, engaging, and interactive piano
learning tool. Unlock your musical potential with our Interactive Piano Learning
System. Designed to inspire beginners and enhance experienced players, this
solution combines technology with a seamless user experience. Featuring LED-
guided learning, real-time feedback, our system transforms the way you engage
with music—making learning intuitive, engaging, and fun. Whether you're picking
up your first tune or refining your skills, this platform empowers you to progress
at your own pace while enjoying every note.

### Objective

An interactive piano learning system based on a piano equipped with LED lights
connected to a Raspberry Pi. The system enables users to play songs using MIDI
files, with lights illuminating the corresponding keys.

### Example Scenario

The user uploads an MP3 file to the app. Using AI and specific libraries the file is
converted into a MIDI format, which lights up the piano keys according to the
notes. In practice mode, subsequent keys illuminate only after the user presses
the correct key.

### High-Level Design

**Architecture**

**1. Hardware:** A piano with LED lights connected to a Raspberry Pi/Arduino.
**2. Software:**
    **Client:** A management app for songs and playback.
    **Server:** MIDI file processing and AI-based audio-to-MIDI conversion.


### Features

Learning mode – This feature is designed to help users learn piano at their own
pace. The piano keys light up according to the song’s notes, waiting for the user
to press the correct key before advancing. This mode is ideal for beginners who
need more time to process and respond.

Playing mode performance/stage mode – For advanced learners or those
practicing speed and accuracy, this mode lights the keys at a set pace,
independent of the player’s input. Users are scored based on their timing and
accuracy, providing a performance metric to track progress.

Variable speed – Learners can adjust the playback speed of songs. This flexibility
allows beginners to start slow and gradually increase the tempo as they become
more confident. Different difficulty levels ensure a scalable learning curve.

Song Library and Customization - The device comes preloaded with a curated list
of songs but also supports adding custom tracks. Users can search, sort, and
organize songs by criteria such as difficulty, or artist. This feature ensures that
learners have a diverse selection to choose from.

Hand-Specific Training - Players can focus on either hand by selecting the
corresponding mode. This feature is particularly useful for practicing hand
independence, a critical skill in piano playing.

Record and Save - The system allows users to record their performances and
save them as MIDI files for later playback. This feature is useful for self-
assessment and progress tracking.

Light Show - In addition to its educational use, the LED strip can display light
animations synchronized with music, providing a visually appealing experience.
This feature enhances entertainment value, making the device suitable for
casual or social settings.

Standalone Operation - Equipped with a screen and physical buttons, the device
can function independently. This eliminates the need for external devices and
makes it a compact, portable solution.


Web Application - The optional web application serves as an intuitive interface
for managing features, uploading custom songs, and viewing statistics. The app
connects to the device via a Wi-Fi hotspot, ensuring seamless interaction.


### MP3 to MIDI conversion

We will be using a convolutional neural network to classify isolated frequencies
to notes and then transcribing them to MIDI. The isolation will be done with
either and either using Fourier transform, Constant-Q Transform (CQT), or using
the NN directly with the non-isolated data.

The goal is to provide a polyphonic transcription (transcription of multiple notes
like chords simultaneously) which would be crucial considering the polyphonic
nature of the piano which allows playing with both hands simultaneously.

We plan on being able to detect the start and end times (onset and offset) of
each note to determine the correct duration for it in the MIDI file.

The supported file types will include MP3 and WAV which are the most common
audio file types for music.

Depending on the performance and accuracy of the model, we might try to
differentiate between musical notes and non-musical sounds, to ensure that
only the.



### Scenarios

The product will provide a solution for everybody who's willing to learn to play
piano, and have a fun engaging experience alone or with their friends, without
commitment to lessons or curriculum.

For example:

1. David Schwartz, 30, a music enthusiast. David has never played the piano
    before, he was always to busy to enlist to music lessons, and the initial
    stepping stone was to big of a challenge. David always was curios about
    playing the piano and given our product now he's able to get back from
    work, and study at his own pace.
2. Amy Cohen, 9 , Amy has friends that play in the school band and she was
    always jealous of their talent. Amy switch hobbies a lot so her parents
    don’t want to get a serios piano and lessons for her, so instead they buy
    her a basic keyboard and our product so she could learn to play whenever
    and as little as she would like.
3. Daniel and John are professional piano players who share a deep passion
    for music. They have developed a friendly rivalry, often meeting to
    challenge each other and test their skills. Both players thrive on
    competition, using their encounters as a way to push themselves to new
    heights. Their ultimate goal is to see who can achieve the highest score,
    constantly striving for improvement while enjoying the thrill of their
    musical duels.
4. Tomer, 26, has been playing the piano for 3 years and loves to compete
    and play with his friends. He and couple of his playing friends decided to
    get the product to challenge and try to top each other scores. They added
    each other as friends using the built in community hub, from which they
    can see each other scores and issue challenges.


5. Yevgeny, 37, is an advanced piano player who's been playing for 12 years.
    He mostly like to be with himself so he doesn't play in concerts. Playing
    with himself no longer proves to be an engaging challenge for him. so he
    decided to get the product and compete in the monthly challenges of the
    community hub which features various difficulty levels for song and a
    leaderboard to see the top scores worldwide. Yevgeny has taken
    challenge to get to the top 10 players in such monthly challenge.


### Flow

**Initial Setup Flow:**

1. Placing the Light Strip:
    The user places the light strip on top of the piano, ensuring it's properly
    aligned with the keys for optimal visibility.
2. Connecting the Raspberry Pi:
    The user connects the Raspberry Pi to the piano’s MIDI output using a USB
    cable or through a MIDI-to-USB converter, enabling the system to receive
    note data from the piano.
3. Calibrating the Light Strip:
    The user calibrates the light strip, ensuring the LEDs correspond
    accurately to the piano keys. This process may involve adjusting the
    position or configuring the system through an interface to make sure the
    lights are aligned with the correct keys.

**using:**

4. Choosing a Song:
    The user selects a song either directly through the Raspberry Pi interface
    or using a web application that syncs with the system.
5. Choosing a mode:

```
5.1. Learning Mode:
In Learning Mode, the first note of the selected song lights up on the
piano, signaling the user to press the corresponding key.
The user proceeds to play the song, with the light strip guiding the
correct notes. The system waits for the correct key to be pressed
before progressing, allowing the user to learn at their own pace.
5.2. Performance/stage Mode:
The user begins playing the song on the piano without any light
cues or clues from the system. At this stage, the lights remain off,
and the user plays from memory or knowledge of the song, relying
purely on their own skill and fluency.
```

6. Performance Score:
    Once the song ends, the app evaluates the user's performance, providing
    a detailed score based on accuracy, timing, and fluency. The user is then
    shown feedback on their playing, helping them assess their proficiency.


## Design

### The components

1. Piano with Midi output –
    - The piano serves as the primary instrument. It needs to be either a
       digital piano or an acoustic piano retrofitted with a MIDI output.
    - The MIDI output of the piano sends note data to the Raspberry Pi
       for processing.
2. Raspberry Pi Zero –
    - The Raspberry Pi Zero acts as the brain of the system. It processes
       the MIDI data from the piano, controls the LED strip, and interfaces
       with the app (if applicable). It also runs the necessary software to
       manage song playback and learning modes.
    - Connects to the piano via MIDI (USB or MIDI-to-USB converter).
    - Controls the LED strip by sending signals through the GPIO pins or
       a dedicated LED controller.
3. LED Strip –
    - The LED strip provides the visual cue for the user, lighting up the
       corresponding piano keys. It will be used to indicate which keys
       to play at each moment, offering guidance for beginners and
       feedback for experienced players.
    - The LED strip is connected to the Raspberry Pi via GPIO pins or
       through a dedicated controller to ensure precise timing and
       control over each light.
4. MicroSD card-
    - The MicroSD card is used to store the Raspberry Pi's operating
       system, the software for controlling the LED strip, MIDI
       processing, and any other necessary files such as MIDI songs or
       user data.


- Use a high-speed microSD card to ensure smooth operation and
    quick loading of songs and user data.
5. Power Supply –
- Provides power to the Raspberry Pi and the LED strip. The power
supply needs to be able to handle the combined requirements
of the Raspberry Pi, LED strip, and any additional components.


Architecture diagram


### Client - server architecture

The raspberry will act as a server, managing the DB and facilitating the features
while an optional web client could act as a more friendly interface and upload
songs to the device via onboard wifi hotspot.

#### 1. Server (Raspberry Pi)

**Responsibilities:**

- Acts as the central processing unit, managing the entire system’s logic
    and communication.
- Hosts the database and stores song files, user data, and performance
    metrics.
- Controls the LED strip based on MIDI inputs and user interactions.
- Manages communication with the web client, either through a local Wi-Fi
    hotspot or direct network connection.

#### 2. Client (Web Interface)

**Responsibilities:**

- Provides the user-friendly interface for interacting with the system.
- Allows users to upload songs, view performance feedback, and configure
    settings.


### The DB (in the raspberry) contains the following fields

Song name - The name of the song. This will be used to identify the song in the
system and when the user selects a song for playback or practice.

artist name - The name of the artist or composer who created the song. This
helps users track the artist and organize songs accordingly.

Length - The length of the song in seconds. This helps track the overall duration
of the song and provides an idea of how long a user will be practicing.

top score - The highest performance score achieved by any user for this song.
This could be based on factors such as accuracy, timing, and overall fluency.

Date - The date when the song was added to the system or the date when the
song was last converted. This will help track song history and additions.

converted (bool) - A boolean value indicating whether the song has been
converted from its original format to MIDI. This helps track the status of the song
file in the system.

1. Users Table
    Field Name Description
    **user_id**^ Unique identifier for each user^
    **username** The username chosen by the user
    **email** User's email address
    **password** Encrypted password for user security
    **join_date** Date when the user registered
2. Songs Table
    Field Name Description

**song_id** (^) Unique identifier for each
song^
**song_name** (^) Name of the song
**artist_name** (^) Name of the song's artist
**length** (^) Duration of the song
**top_score**^ Highest score achieved^


```
user_id _top_score Highest score achieved
player
```
**upload_date** (^) Date when the song was
uploaded^
**converted** Whether the song has
been MIDI-converted
**midi_file_path** Path to the MIDI file
3.Performances song
Field Name Description
**performance_id**^ Unique identifier for the performance^
**performance_name** Unique name for the performance
**skill_level_chosen** Skill level of the performance
**score** Number of points in the performance^
**user_id**^ Unique identifier for the user^
**created_at** Date and time when the performance was
created

### packages

mido – with working with midi files

GPIO- for the raspberry screen

RPi.GPIO and rpi_ws281x – for the LEDs

numpy


