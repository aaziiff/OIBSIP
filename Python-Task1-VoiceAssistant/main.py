from assistant_core import listen, process_command, speak


def main():
    speak("Hello! I am your voice assistant.")

    running = True

    while running:

        command = listen()

        if command:
            running = process_command(command)


if __name__ == "__main__":
    main()