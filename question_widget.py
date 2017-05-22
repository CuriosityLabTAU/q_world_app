from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy_communication import *
from kivy.uix.image import *


class QuestionWidget(WidgetLogger):
    image_id_what = ObjectProperty(None)
    button_id_what = ObjectProperty(None)
    image_id_how = ObjectProperty(None)
    button_id_how = ObjectProperty(None)
    parent_concept = ''
    parent_network = None

    def __init__(self, parent_concept='', parent_network=None):
        super(QuestionWidget, self).__init__()

        self.parent_concept = parent_concept
        self.parent_network = parent_network

        self.q = {
            "what": {
                "image": self.image_id_what,
                "button": self.button_id_what
            },
            "how": {
                "image": self.image_id_how,
                "button": self.button_id_how
            },
            "why": {
                "image": self.image_id_why,
                "button": self.button_id_why
            }
        }

    def question_pressed(self, question):
        self.parent_network.question_pressed(self.parent_concept, question)


