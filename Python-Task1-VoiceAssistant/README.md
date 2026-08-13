# Python Voice Assistant

A desktop voice assistant developed in Python that enables users to interact with their computer using natural voice commands.

The project combines speech recognition, text-to-speech, web services, YouTube integration, macOS application control, and a modern Apple-inspired dark graphical user interface.

## Features

•⁠  ⁠🎙️ Voice command recognition
•⁠  ⁠🗣️ Text-to-speech responses
•⁠  ⁠💬 Conversation history in the GUI
•⁠  ⁠🔎 Google search
•⁠  ⁠▶️ YouTube search and playback
•⁠  ⁠🌐 Open Google and YouTube
•⁠  ⁠🖥️ macOS application control
•⁠  ⁠🕐 Current time and date
•⁠  ⁠🤖 Basic conversational commands
•⁠  ⁠🌑 Apple-inspired dark interface
•⁠  ⁠📜 Automatic conversation scrolling

## Technologies Used

•⁠  ⁠Python 3.12
•⁠  ⁠PySide6 — graphical user interface
•⁠  ⁠SpeechRecognition — voice input
•⁠  ⁠PyAudio — microphone access
•⁠  ⁠yt-dlp — YouTube integration
•⁠  ⁠macOS Speech Synthesis (⁠ say ⁠) — voice responses
•⁠  ⁠Git & GitHub — version control and project hosting

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/aaziiff/Python-Task1-VoiceAssistant.git
cd Python-Task1-VoiceAssistant

USAGE
------

After completing the installation, run the project using the following command:
------------------------------------------------------------------------------
python3 assistant_gui.py

The voice assistant window will open and allow you to interact with the assistant using your microphone.
The application will process the input and display the corresponding output.

example commands:
-----------------
"What is the time?"
"What is today's date?"
"Open Safari"
"Open Calculator"
"Open Finder"
"Open Notes"
"Open Terminal"
"Open Google"
"Open YouTube"
"Search Google for Python tutorials"
"Search YouTube for music"
"Play music on YouTube"

To stop the assistance:
-----------------------
"Stop"
"Exit"
"Goodbye"

Features
---------
•⁠  ⁠Simple and user-friendly interface
•⁠  ⁠Easy-to-use command-line interaction
•⁠  ⁠Fast and efficient execution
•⁠  ⁠Modular and maintainable Python code
•⁠  ⁠Handles user input and provides appropriate responses
•⁠  ⁠Designed as part of the Oasis Infobyte Python Programming Internship

Technologies Used:
--------------------

•⁠  ⁠Python 3
•⁠  ⁠Python Standard Library
•⁠  ⁠Virtual Environment (venv)
•⁠  ⁠Git & GitHub
•⁠  ⁠VS Code

Project Structure
------------------
PYTHON-TASK1-VOICEASSISTANT/
│   
├── assistant_gui.py
|__ assistant_core.py
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore

File Description
----------------
•⁠  ⁠main.py — Main application logic and program entry point.
•⁠  ⁠assistant_gui.py — Graphical user interface for the assistant.
•⁠  ⁠requirements.txt — Lists the Python dependencies required by the project.
•⁠  ⁠README.md — Project documentation and usage instructions.
•⁠  ⁠LICENSE — Project license information.
•⁠  ⁠.gitignore — Specifies files and folders that should not be uploaded to GitHub.

Compatibility
-------------
This project is currently designed and tested for macOS.
The Voice Assistant uses macOS-specific system commands for features such as:
-----------------------------------------------------------------------------
•⁠  ⁠Text-to-speech using the macOS say command
•⁠  ⁠Opening applications using the macOS open command
•⁠  ⁠Controlling applications using AppleScript (osascript)

Supported Platform
--------------------
•⁠  ⁠macOS — Fully supported and tested

Note: The current implementation is not guaranteed to work on Windows or Linux because several features depend on macOS-specific system commands.

Requirements
------------
Before running the project, make sure the following are installed:
•⁠  ⁠Python 3
•⁠  ⁠SpeechRecognition — Speech recognition functionality
•⁠  ⁠PySide6 — Graphical user interface
•⁠  ⁠yt-dlp — Media downloading functionality
•⁠  ⁠PyAudio — Audio input and microphone support
All required Python packages are listed in requirements.txt.
Install the dependencies using:
pip install -r requirements.txt

Author
-------
Asif Muhammed
BCA Student | Python Developer | Aspiring Data Scientist
This project was developed as part of the Oasis Infobyte Python Programming Internship (OIBSIP).