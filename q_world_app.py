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
from kivy.animation import Animation
from copy import deepcopy
from the_network import *
LANGUAGE = 'Hebrew'  # 'Hebrew'
sound_path = {'general': 'items/sounds/', 'world': 'x/sounds/'}


class GameScreen(Screen):
    curiosity_game = None

    game_number = -1
    the_app = None
    game_type = None
    game_duration = 120
    game_introduction = ""

    game_network = None
    game_questions = None
    game_edges = None

    def start(self, number=-1, the_app=None, the_type=None, duration=120, introduction="",
              network=None, questions=None, edges=None):
        self.size = (200,100)
        self.game_number = number
        self.the_app = the_app
        self.game_type = the_type
        self.game_duration = duration
        self.game_introduction = introduction

        self.game_network = network
        self.game_questions = questions
        self.game_edges = edges

        self.curiosity_game = CuriosityGame(self)
        self.curiosity_game.game_duration = duration
        if self.game_type[0] == 'full':
            pass
        elif self.game_type[0] == 'n_questions':
            self.curiosity_game.game_questions = the_type[1]
        elif self.game_type[0] == 'n_type':
            self.curiosity_game.game_q_type = ['' for i in range(the_type[1])]

        if self.game_number == 0:
            self.curiosity_game.set_tutorial()

    def on_enter(self, *args):
        log_str = 'start,'
        log_str += 'duration=' + str(self.curiosity_game.game_duration) + ','
        log_str += 'questions=' + str(self.curiosity_game.game_questions)
        KL.log.insert(action=LogAction.data, obj='game_'+str(self.game_number), comment=log_str)

        self.curiosity_game.load(network=self.game_network,
                                 questions=self.game_questions,
                                 edges=self.game_edges)
        Clock.schedule_once(self.explanation_screen, 0.5)

    def explanation_screen(self, dt):
        self.curiosity_game.start()
        self.curiosity_game.tell_story(self.game_introduction[0], self.game_introduction[1])
        Clock.schedule_once(self.end_game, self.curiosity_game.game_duration)

    def end_game(self, dt):
        self.curiosity_game.the_end = True
        if not self.curiosity_game.is_playing:
            self.next_game()

    def next_game(self):
        log_str = 'end,q_type='
        for q in self.curiosity_game.game_q_type:
            log_str += str(q) + ';'
        KL.log.insert(action=LogAction.data, obj='game_' + str(self.game_number), comment=log_str)

        # delete network
        self.curiosity_game.discovered_network = set()
        for c_name, c in self.curiosity_game.network.concepts.items():
            c['visible'] = c['level'] == 1

        if self.game_number < 4:
            self.the_app.sm.current = 'game_' + str(self.game_number+1)
        else:
            KL.log.insert(action=LogAction.data, obj='game', comment='the_end', sync=True)
            self.curiosity_game.is_playing = True
            sl = SoundLoader.load('items/sounds/the_end_Q_World.wav')
            sl.bind(on_stop=self.end_subject)
            sl.play()

    def end_subject(self, *args):
        self.the_app.stop()
            # self.the_app.sm.current = 'zero_screen'


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
    current_question_widget = None

    def __init__(self, game_screen=None):
        self.game_screen = game_screen
        self.the_widget = CuriosityWidget(self)
        self.network = TheNetwork(self)

    def load(self, network=None, questions=None, edges=None):
        self.network.load(network_dict=network,questions=questions, edges=edges, app_size=self.the_widget.size)
        self.the_widget.update_background(self.network.background)
        self.is_playing = False

    def concept_pressed(self, concept_name):
        self.the_widget.clear_widgets()
        for c_name, concept in self.network.concepts.items():
            if concept['visible']:
                self.the_widget.add_widget(concept['widget'])
            if c_name == concept_name:
                if 'why' in concept or 'what' in concept or 'why' in concept:
                    self.the_widget.add_widget(concept['q_widget'])

        if self.tutorial:
            if self.explanations['concept_pressed']['repeats'] > 0:
                self.tell_story(self.explanations['concept_pressed']['text'],
                                self.explanations['concept_pressed']['sound'])
                self.explanations['concept_pressed']['repeats'] -= 1

    def question_pressed(self, question, concept_):
        if self.game_q_type is not None:
            if '' in self.game_q_type:      # there is still a free question type
                self.game_q_type[self.game_q_type.index('')] = question
                for c_name, concept in self.network.concepts.items():
                    for q in concept['q_widget'].q:
                        if q != question:
                            concept['q_widget'].q[q]['image'].disabled = True
                            concept['q_widget'].q[q]['button'].disabled = True
        self.refresh_network()

        current_story = {'text': '', 'sound': []}

        current_story['text'] += self.network.story[concept_ + ',' + question][0]
        for s in self.network.story[concept_ + ',' + question][1]:
            current_story['sound'].append(self.network.image_dir + 'sounds/' + s)

        if self.tutorial:
            if self.explanations['question_pressed']['repeats'] > 0:
                current_story['text'] += self.explanations['question_pressed']['text']
                for s in self.explanations['question_pressed']['sound']:
                    current_story['sound'].append('items/sounds/' + s)
                self.explanations['question_pressed']['repeats'] -= 1

        self.tell_story(text=current_story['text'], story_file=current_story['sound'], story_path='')

        if self.game_questions > 0:
            self.game_questions -= 1
            if self.game_questions == 0:
                Clock.schedule_once(self.game_screen.end_game, 0.5)
                return

    def refresh_network(self):
        self.the_widget.clear_widgets()
        for c_name, concept in self.network.concepts.items():
            if concept['visible']:
                self.the_widget.add_widget(concept['widget'])
                self.discovered_network.add((c_name, 'visible'))
        for c_name, concept in self.network.concepts.items():
            if concept['new']:
                # move to
                new_position = deepcopy(concept['widget'].image_id.pos)
                concept['widget'].image_id.pos = self.network.concepts[concept['new']]['widget'].image_id.pos
                anim = Animation(x=new_position[0], y=new_position[1], duration=1)
                anim.start(concept['widget'].image_id)
                self.check_animation(concept)
                # # blink
                # concept['widget'].image_id.color = (0,0,0,0)
                # Clock.schedule_once(partial(self.new_concept, concept), 0.5)

            concept['new'] = None

        visible_network = []
        for concept in self.discovered_network:
            if concept[1] == 'visible':
                visible_network.append(concept[0])
        visible_network_str = str(visible_network).replace('u\'', '"').replace('\'', '"')
        KL.log.insert(action=LogAction.data, obj='visible_network', comment=visible_network_str)

    def check_animation(self, concept):
        if len(concept['image']) > 1:
            Clock.schedule_once(partial(self.do_animation, concept, 1), 0.2)

    def do_animation(self, concept, t, dt):
        if t < 10:
            concept['widget'].image_id.source = self.network.image_dir + concept['image'][t % len(concept['image'])]
            Clock.schedule_once(partial(self.do_animation, concept, t + 1), 0.2)

    def tell_story(self, text=None, story_file=None, source=None, story_path=None):
        if not source:
            source = 'general'
        if story_path is None:
            story_path = sound_path[source].replace('x', self.network.image_dir)

        self.sounds = []
        for story in story_file:
            story_full_filename = story_path + story
            loaded_sound = SoundLoader.load(story_full_filename)
            if loaded_sound:
                if loaded_sound.length > 0:
                    self.sounds.append(loaded_sound)
        if LANGUAGE == 'English':
            if len(self.sounds) == 0:
                TTS.speak([text])
            else:
                self.play_story()
        elif LANGUAGE == 'Hebrew':
            if len(self.sounds) > 0:
                self.play_story()

    def play_story(self):
        if not self.is_playing:
            if len(self.sounds) > 0:
                self.started_playing()
                self.sounds[0].bind( on_stop=self.continue_play)
                self.sounds[0].play()

    def continue_play(self, *args):
        self.stopped_playing()
        if self.the_end:
            self.game_screen.next_game()
            return
        if len(self.sounds) > 0:
            self.sounds.pop(0)
            self.play_story()

    def started_playing(self):
        self.is_playing = True
        for w in self.the_widget.children:
            w.disabled = True

    def stopped_playing(self):
        self.is_playing = False
        for w in self.the_widget.children:
            w.disabled = False

    def start(self):
        # set the timer of the game
        print('Starting clock...')
        self.refresh_network()
        self.the_end = False

    def set_tutorial(self):
        self.tutorial = True
        self.explanations = {
            'concept_pressed': {
                'repeats': 1,
                'sound': ['intro_specific_object_1.wav', 'intro_specific_object_2.wav'],
                'text': "you can ask a question on this object. what is it made of, why is it here, how does it work."
            },
            'question_pressed': {
                'repeats': 1,
                'sound': ['intro_new_object_1.wav', 'intro_new_object_2.wav'],
                'text': 'a new object appears. you can ask about it also.'
            }
        }


class CuriosityWidget(FloatLayout):
    cg_lbl = None
    the_game = None

    def __init__(self, the_game=None):
        super(CuriosityWidget, self).__init__()
        self.the_game = the_game
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
        self.the_game.network.update_pos_size(instance.size)
