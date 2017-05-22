from kivy.properties import StringProperty, ObjectProperty

from kivy_communication import *
from kivy.uix.image import *


class ConceptWidget(WidgetLogger):
    image_id = ObjectProperty(None)
    button_id = ObjectProperty(None)
    parent_network = None

    def __init__(self, parent_network=None):
        super(ConceptWidget, self).__init__()
        self.parent_network = parent_network

    def concept_pressed(self):
        self.parent_network.concept_pressed(self.name)


