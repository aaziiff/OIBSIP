import sys
import threading
import assistant_core

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFrame
)


# --------------------------------
# GUI SIGNALS
# --------------------------------

class AssistantSignals(QObject):

    user_message = Signal(str)
    assistant_message = Signal(str)
    status_changed = Signal(str)
    listening_started = Signal()
    listening_finished = Signal()


signals = AssistantSignals()


# --------------------------------
# MAIN WINDOW
# --------------------------------

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Voice Assistant")
window.resize(760, 820)


# --------------------------------
# APPLE STYLE
# --------------------------------

window.setStyleSheet("""

    QWidget {
        background-color: #000000;
        color: #F5F5F7;
        font-family: Arial;
    }

    QLabel#title {
        font-size: 34px;
        font-weight: bold;
        color: #F5F5F7;
    }

    QLabel#subtitle {
        font-size: 15px;
        color: #86868B;
    }

    QLabel#status {
        font-size: 15px;
        color: #30D158;
        font-weight: bold;
    }

    QFrame#card {
        background-color: #1C1C1E;
        border: 1px solid #2C2C2E;
        border-radius: 18px;
    }

    QTextEdit {
        background-color: #1C1C1E;
        color: #F5F5F7;
        border: none;
        border-radius: 18px;
        padding: 18px;
        font-size: 15px;
    }

    QPushButton {
        background-color: #F5F5F7;
        color: #000000;
        border: none;
        border-radius: 28px;
        font-size: 16px;
        font-weight: bold;
        padding: 16px 30px;
    }

    QPushButton:hover {
        background-color: #D2D2D7;
    }

    QPushButton:pressed {
        background-color: #A1A1A6;
    }

    QPushButton:disabled {
        background-color: #3A3A3C;
        color: #8E8E93;
    }

    QLabel#footer {
        color: #6E6E73;
        font-size: 12px;
    }

""")


# --------------------------------
# LAYOUT
# --------------------------------

layout = QVBoxLayout()

layout.setContentsMargins(
    55,
    45,
    55,
    35
)

layout.setSpacing(12)


# --------------------------------
# TITLE
# --------------------------------

title = QLabel("Voice Assistant")

title.setObjectName("title")

title.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)

layout.addWidget(title)


# --------------------------------
# SUBTITLE
# --------------------------------

subtitle = QLabel(
    "Your personal desktop assistant"
)

subtitle.setObjectName("subtitle")

subtitle.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)

layout.addWidget(subtitle)


layout.addSpacing(10)


# --------------------------------
# STATUS
# --------------------------------

status = QLabel("●  Ready")

status.setObjectName("status")

status.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)

layout.addWidget(status)


layout.addSpacing(15)


# --------------------------------
# CONVERSATION CARD
# --------------------------------

card = QFrame()

card.setObjectName("card")

card_layout = QVBoxLayout(card)

card_layout.setContentsMargins(
    5,
    5,
    5,
    5
)


conversation = QTextEdit()

conversation.setReadOnly(True)

conversation.setPlaceholderText(
    "Your conversations will appear here..."
)

card_layout.addWidget(
    conversation
)

layout.addWidget(
    card,
    1
)


layout.addSpacing(20)


# --------------------------------
# MICROPHONE BUTTON
# --------------------------------

button_layout = QHBoxLayout()

mic_button = QPushButton(
    "🎙  Start Listening"
)

mic_button.setMinimumHeight(58)

button_layout.addStretch()

button_layout.addWidget(
    mic_button
)

button_layout.addStretch()

layout.addLayout(
    button_layout
)


layout.addSpacing(15)


# --------------------------------
# FOOTER
# --------------------------------

footer = QLabel(
    "Voice Assistant  •  Python"
)

footer.setObjectName("footer")

footer.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)

layout.addWidget(
    footer
)


window.setLayout(
    layout
)


# --------------------------------
# SHOW USER MESSAGE
# --------------------------------

def show_user_message(text):

    conversation.append(
        f"""
        <div style="
            margin-top:12px;
            margin-bottom:8px;
        ">
        <b style="color:#FFFFFF;">
        You
        </b>
        </div>

        <div style="
            color:#D1D1D6;
            margin-bottom:15px;
        ">
        {text}
        </div>
        """
    )

    conversation.verticalScrollBar().setValue(
        conversation.verticalScrollBar().maximum()
    )


# --------------------------------
# SHOW ASSISTANT MESSAGE
# --------------------------------

def show_assistant_message(text):

    conversation.append(
        f"""
        <div style="
            margin-top:12px;
            margin-bottom:8px;
        ">
        <b style="color:#30D158;">
        Voice Assistant
        </b>
        </div>

        <div style="
            color:#F5F5F7;
            margin-bottom:15px;
        ">
        {text}
        </div>
        """
    )

    conversation.verticalScrollBar().setValue(
        conversation.verticalScrollBar().maximum()
    )


# --------------------------------
# LISTENING STATE
# --------------------------------

def start_listening_ui():

    status.setText(
        "●  Listening..."
    )

    mic_button.setText(
        "🎙  Listening..."
    )

    mic_button.setEnabled(
        False
    )


# --------------------------------
# FINISHED STATE
# --------------------------------

def finish_listening_ui():

    status.setText(
        "●  Ready"
    )

    mic_button.setText(
        "🎙  Start Listening"
    )

    mic_button.setEnabled(
        True
    )


# --------------------------------
# VOICE COMMAND
# --------------------------------

def listen_for_command():

    signals.listening_started.emit()

    command = assistant_core.listen()

    if not command:

        signals.status_changed.emit(
            "●  Didn't hear anything"
        )

        signals.listening_finished.emit()

        return


    # Show user's speech

    signals.user_message.emit(
        command
    )


    # Processing

    signals.status_changed.emit(
        "●  Processing..."
    )


    # Process command

    response = assistant_core.process_command(
        command
    )


    # Show assistant response

    if response:

        signals.assistant_message.emit(
            response
        )


    # Finished

    signals.listening_finished.emit()


# --------------------------------
# START LISTENING
# --------------------------------

def start_listening():

    thread = threading.Thread(
        target=listen_for_command,
        daemon=True
    )

    thread.start()


# --------------------------------
# CONNECT SIGNALS
# --------------------------------

signals.user_message.connect(
    show_user_message
)

signals.assistant_message.connect(
    show_assistant_message
)

signals.status_changed.connect(
    status.setText
)

signals.listening_started.connect(
    start_listening_ui
)

signals.listening_finished.connect(
    finish_listening_ui
)


mic_button.clicked.connect(
    start_listening
)


# --------------------------------
# START APPLICATION
# --------------------------------

window.show()

sys.exit(
    app.exec()
)