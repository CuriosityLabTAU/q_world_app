#!/usr/bin/kivy
# -*- coding: utf-8 -*-
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty, ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout
from functools import partial
from kivy.graphics import Rectangle
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy_communication import *
from hebrew_management import HebrewManagement
from text_handling import *
from kivy.uix.screenmanager import Screen
from the_network import *
LANGUAGE = 'English'  # 'Hebrew'


class GameScreen(Screen):
    curiosity_game = None

    game_number = -1
    the_app = None
    game_type = None
    game_duration = 120

    game_network = None
    game_questions = None
    game_edges = None

    def start(self, number=-1, the_app=None, the_type=None, duration=120,
              network=None, questions=None, edges=None):
        self.game_number = number
        self.the_app = the_app
        self.game_type = the_type
        self.game_duration = duration

        self.game_network = network
        self.game_questions = questions
        self.game_edges = edges

        self.curiosity_game = CuriosityGame(self)
        self.curiosity_game.game_duration = duration
        if the_type[0] == 'full':
            pass
        elif the_type[0] == 'n_questions':
            self.curiosity_game.game_questions = the_type[1]
        elif the_type[0] == 'n_type':
            self.curiosity_game.game_q_type = ['' for i in range(the_type[1])]

        if self.game_number == 0:
            self.curiosity_game.set_tutorial()

        self.curiosity_game.load(network=self.game_network,
                                 questions=self.game_questions,
                                 edges=self.game_edges)

    def on_enter(self, *args):
        log_str = 'start,'
        log_str += 'duration=' + str(self.curiosity_game.game_duration) + ','
        log_str += 'questions=' + str(self.curiosity_game.game_questions)
        KL.log.insert(action=LogAction.data, obj='game_'+str(self.game_number), comment=log_str)

        Clock.schedule_once(self.end_game, self.curiosity_game.game_duration)
        self.curiosity_game.start()

    def end_game(self, dt):
        log_str = 'end,q_type='
        for q in self.curiosity_game.game_q_type:
            log_str += str(q) + ';'
        KL.log.insert(action=LogAction.data, obj='game_' + str(self.game_number), comment=log_str)

        # delete network
        self.curiosity_game.discovered_network = set()
        for c_name, c in self.curiosity_game.network.concepts.items():
            c['visible'] = c['level'] == 1

        try:
            self.the_app.sm.current = 'game_' + str(self.game_number+1)
        except:
            self.the_app.sm.current = 'zero_screen'


class CuriosityGame:
    game_screen = None
    the_widget = None
    the_end = False
    game_duration = 120
    game_questions = -1
    game_q_type = []
    discovered_network = set()
    tutorial = False
    explanations = None

    def __init__(self, game_screen=None):
        self.game_screen = game_screen
        self.the_widget = CuriosityWidget()
        self.network = TheNetwork(self)

    def load(self, network=None, questions=None, edges=None):
        self.network.load(network_dict=network,questions=questions, edges=edges)
        self.the_widget.update_background(self.network.background)
        self.refresh_network()

    def concept_pressed(self, concept_name):
        self.the_widget.clear_widgets()
        for c_name, concept in self.network.concepts.items():
            if concept['visible']:
                self.the_widget.add_widget(concept['widget'])
            if c_name == concept_name:
                self.the_widget.add_widget(concept['q_widget'])

        if self.tutorial:
            if self.explanations['concept_pressed']['repeats'] > 0:
                self.explanations['concept_pressed']['sound'].play()
                self.explanations['concept_pressed']['repeats'] -= 1

    def question_pressed(self, question):
        if self.game_questions > 0:
            self.game_questions -= 1
            if self.game_questions == 0:
                self.game_screen.end_game(0)

        if self.game_q_type is not None:
            if '' in self.game_q_type:      # there is still a free question type
                self.game_q_type[self.game_q_type.index('')] = question
                for c_name, concept in self.network.concepts.items():
                    for q in concept['q_widget'].q:
                        if q != question:
                            concept['q_widget'].q[q]['image'].disabled = True
                            concept['q_widget'].q[q]['button'].disabled = True
        self.refresh_network()

        if self.tutorial:
            if self.explanations['question_pressed']['repeats'] > 0:
                self.explanations['question_pressed']['sound'].play()
                self.explanations['question_pressed']['repeats'] -= 1

    def refresh_network(self):
        self.the_widget.clear_widgets()
        for c_name, concept in self.network.concepts.items():
            if concept['visible']:
                self.the_widget.add_widget(concept['widget'])
                self.discovered_network.add((c_name, 'visible'))
        print(self.discovered_network)

    def start(self):
        # set the timer of the game
        print('Starting clock...')
        self.refresh_network()
        self.the_end = False

    def set_tutorial(self):
        self.tutorial = True
        self.explanations = {
            'concept_pressed': {
                'repeats': 3,
                'sound': SoundLoader.load('items/concept_press_explanation.wav')
            },
            'question_pressed': {
                'repeats': 3,
                'sound': SoundLoader.load('items/question_press_explanation.wav')
            }
        }

class CuriosityWidget(FloatLayout):
    cg_lbl = None

    def __init__(self):
        super(CuriosityWidget, self).__init__()
        with self.canvas.before:
            self.rect = Rectangle(source='')
            self.bind(size=self._update_rect, pos=self._update_rect)
        self.cg_lbl = []
        for k in range(0,3):
            self.cg_lbl.append(Label(font_name='fonts/the_font.ttf', halign='right', text='',
                            pos=(10, 10 + 75 * k), font_size='48sp', size_hint_y=0.1, color=[0,0.1,0.5,1.0]))
            self.add_widget(self.cg_lbl[-1])

    def update_background(self, filename):
        with self.canvas.before:
            self.rect = Rectangle(source=filename, size=self.size)
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
