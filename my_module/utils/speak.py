import pyttsx3


class Speak:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.set_voice()
        self.set_speed(150)

    def set_voice(self):
        voices = self.engine.getProperty("voices")

        for voice in voices:
            if "female" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break
            else:
                self.engine.setProperty("voice", voices[1].id)

    def set_speed(self, speed: int):
        self.engine.setProperty("rate", speed)

    def say(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
