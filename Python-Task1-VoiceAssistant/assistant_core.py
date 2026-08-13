import speech_recognition as sr
import datetime
import webbrowser
import subprocess
import yt_dlp


def speak(text):
    print("Assistant:", text)
    subprocess.run(["say", text])
    return text


def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=12
            )

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

    try:
        command = recognizer.recognize_google(audio)

        print("You:", command)

        return command.lower()

    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
        return ""

    except sr.RequestError:
        print("Speech recognition service is unavailable.")
        return ""


def google_search(command):

    command = command.lower().strip()

    phrases = [
        "search google for ",
        "search for ",
        "search google ",
        "find ",
        "look for "
        "can you please"
        "please search for"
        "could you please search for"
    ]

    for phrase in phrases:

        if phrase in command:

            query = command.split(
                phrase,
                1
            )[1]

            query = query.replace(
                " on google",
                ""
            ).strip()

            return query

    return ""


def process_command(command):

    command = command.lower().strip()

    print("Processing:", command)

    # -------------------------
    # HELLO
    # -------------------------

    if "hello" in command or "hi" in command:

        return speak(
            "Hello! How can I help you?"
        )


    # -------------------------
    # TIME
    # -------------------------

    elif "time" in command:

        current_time = datetime.datetime.now().strftime(
            "%I:%M %p"
        )

        return speak(
            f"The current time is {current_time}"
        )


    # -------------------------
    # DATE
    # -------------------------

    elif "date" in command or "today" in command:

        today = datetime.datetime.now().strftime(
            "%B %d, %Y"
        )

        return speak(
            f"Today's date is {today}"
        )


    # -------------------------
    # NAME
    # -------------------------

    elif (
        "name" in command
        or "who are you" in command
    ):

        return speak(
            "My name is Voice Assistant."
        )


    # -------------------------
    # CREATOR
    # -------------------------

    elif (
        "who made you" in command
        or "who make you" in command
        or "who built you" in command
        or "who build you" in command
    ):

        return speak(
            "I was created by Asif Muhammed."
        )


    # -------------------------
    # SAFARI
    # -------------------------

    elif "open safari" in command:

        speak("Opening Safari.")

        subprocess.run([
            "open",
            "-a",
            "Safari"
        ])

        return "Opening Safari."


    elif "close safari" in command:

        speak("Closing Safari.")

        subprocess.run([
            "osascript",
            "-e",
            'tell application "Safari" to quit'
        ])

        return "Closing Safari."


    # -------------------------
    # CALCULATOR
    # -------------------------

    elif "open calculator" in command:

        speak("Opening Calculator.")

        subprocess.run([
            "open",
            "-a",
            "Calculator"
        ])

        return "Opening Calculator."


    elif "close calculator" in command:

        speak("Closing Calculator.")

        subprocess.run([
            "osascript",
            "-e",
            'tell application "Calculator" to quit'
        ])

        return "Closing Calculator."


    # -------------------------
    # FINDER
    # -------------------------

    elif "open finder" in command:

        speak("Opening Finder.")

        subprocess.run([
            "open",
            "-a",
            "Finder"
        ])

        return "Opening Finder."


    elif "close finder" in command:

        speak("Closing Finder.")

        subprocess.run([
            "osascript",
            "-e",
            'tell application "Finder" to quit'
        ])

        return "Closing Finder."


    # -------------------------
    # NOTES
    # -------------------------

    elif "open notes" in command:

        speak("Opening Notes.")

        subprocess.run([
            "open",
            "-a",
            "Notes"
        ])

        return "Opening Notes."


    elif "close notes" in command:

        speak("Closing Notes.")

        subprocess.run([
            "osascript",
            "-e",
            'tell application "Notes" to quit'
        ])

        return "Closing Notes."


    # -------------------------
    # TERMINAL
    # -------------------------

    elif "open terminal" in command:

        speak("Opening Terminal.")

        subprocess.run([
            "open",
            "-a",
            "Terminal"
        ])

        return "Opening Terminal."


    elif "close terminal" in command:

        speak("Closing Terminal.")

        subprocess.run([
            "osascript",
            "-e",
            'tell application "Terminal" to quit'
        ])

        return "Closing Terminal."


    # -------------------------
    # PLAY YOUTUBE VIDEO
    # -------------------------

    elif "play" in command and "youtube" in command:

        video_query = command

        video_query = video_query.replace(
            "play",
            "",
            1
        )

        video_query = video_query.replace(
            "youtube",
            "",
            1
        )

        video_query = video_query.replace(
            " in ",
            " "
        )

        video_query = video_query.replace(
            " on ",
            " "
        )

        video_query = video_query.strip()

        if not video_query:

            return speak(
                "What would you like me to play on YouTube?"
            )

        try:

            response_text = (
                f"Playing {video_query} on YouTube."
            )

            speak(response_text)

            ydl_opts = {
                "quiet": True,
                "extract_flat": True
            }

            with yt_dlp.YoutubeDL(
                ydl_opts
            ) as ydl:

                info = ydl.extract_info(
                    f"ytsearch1:{video_query}",
                    download=False
                )

            entries = info.get(
                "entries",
                []
            )

            if not entries:

                return speak(
                    "Sorry, I couldn't find that video."
                )

            video_url = entries[0]["url"]

            subprocess.run([
                "open",
                "-a",
                "Google Chrome",
                video_url
            ])

            return response_text

        except Exception as e:

            print(
                "YouTube error:",
                e
            )

            return speak(
                "Sorry, I couldn't find that video."
            )


    # -------------------------
    # SEARCH YOUTUBE
    # -------------------------

    elif (
        "search" in command
        and "youtube" in command
    ):

        search_query = command

        search_query = search_query.replace(
            "search",
            "",
            1
        )

        search_query = search_query.replace(
            "youtube",
            "",
            1
        )

        search_query = search_query.replace(
            "for",
            "",
            1
        )

        search_query = search_query.replace(
            " in ",
            " "
        )

        search_query = search_query.strip()

        if search_query:

            response_text = (
                f"Searching YouTube for {search_query}."
            )

            speak(response_text)

            search_url = (
                "https://www.youtube.com/results?search_query="
                + search_query.replace(" ", "+")
            )

            webbrowser.open(
                search_url
            )

            return response_text

        else:

            return speak(
                "What would you like me to search for on YouTube?"
            )


    # -------------------------
    # GOOGLE SEARCH
    # -------------------------

    elif (
        "search google" in command
        or "find" in command
        or "look for" in command
        or command.startswith("search for ")
    ):

        search_query = google_search(
            command
        )

        if search_query:

            response_text = (
                f"Searching Google for {search_query}."
            )

            speak(response_text)

            search_url = (
                "https://www.google.com/search?q="
                + search_query.replace(" ", "+")
            )

            webbrowser.open(
                search_url
            )

            return response_text

        else:

            return speak(
                "What would you like me to search for?"
            )


    # -------------------------
    # OPEN GOOGLE
    # -------------------------

    elif "open google" in command:

        speak("Opening Google.")

        webbrowser.open(
            "https://www.google.com"
        )

        return "Opening Google."


    # -------------------------
    # OPEN YOUTUBE
    # -------------------------

    elif "open youtube" in command:

        speak("Opening YouTube.")

        webbrowser.open(
            "https://www.youtube.com"
        )

        return "Opening YouTube."


    # -------------------------
    # EXIT
    # -------------------------

    elif (
        "stop" in command
        or "exit" in command
        or "goodbye" in command
    ):

        return speak(
            "Goodbye! Have a great day."
        )


    # -------------------------
    # UNKNOWN COMMAND
    # -------------------------

    else:

        return speak(
            "I'm still learning. "
            "I don't know how to do that yet."
        )