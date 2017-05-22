import json
from random import choice
import time
from kivy.clock import Clock

the_tts = None
try:
    from plyer import tts
    tts.speak('')
    the_tts = 'plyer'
except:
    pass

try:
    import pyttsx
    the_tts = 'pyttsx'
except:
    pass


class TTS:
    engine = None
    what = ''

    @staticmethod
    def start():
        TTS.engine =  None
        if the_tts is 'pyttsx':
            TTS.engine = pyttsx.init()
            TTS.engine.setProperty('voice', 'HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Speech/Voices/Tokens/TTS_MS_EN-US_ZIRA_11.0')
            TTS.engine.connect(topic='finished-utterance', cb=TTS.finished)

    @staticmethod
    def finished():
        print('finished', TTS.what)
        return True

    @staticmethod
    def speak(the_text, finished=None):
        for txt in the_text:
            if the_tts is 'pyttsx':
                TTS.engine.say(txt)
            if the_tts is 'plyer':
                tts.speak(txt)
                time.sleep(float(len(txt)) * 0.05)
                if finished:
                    Clock.schedule_once(finished, 0)
        if the_tts is 'pyttsx':
            TTS.engine.runAndWait()
            time.sleep(1)
            if finished:
                finished(0.0)


class TextHandler:

    def __init__(self, condition='growth'):
        self.data = None
        self.condition = condition
        self.what = None
        TTS.start()

    def load_text(self, filename='./tablet_app/robot_text.json'):
        with open(filename) as data_file:
            self.data = json.load(data_file)

    def say(self, what):
        self.what = what
        if what in self.data:
            the_options = self.data[what]
            the_text = []
            if isinstance(the_options, list):
                the_text.append(choice(the_options))
            elif isinstance(the_options, dict):
                if 'all' in the_options:
                    the_text.append(choice(the_options['all']))
                if self.condition in the_options:
                    the_text.append(choice(the_options[self.condition]))

            print('speak: ', the_text)
            TTS.speak(the_text)
            return True
        else:
            return False