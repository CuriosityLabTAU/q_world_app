#!/usr/bin/python
# -*- coding: utf-8 -*-
from kivy.app import App
from kivy_communication import *
from kivy.uix.screenmanager import ScreenManager, Screen
from text_handling import *
from copy import deepcopy
from q_world_app import *


class ZeroScreen(Screen):

    def on_enter(self, *args):
        KL.restart()

    def start(self):
        self.ids['subject_id'].bind(text=self.ids['subject_id'].on_text_change)


class QWorldApp(App):
    game_screen = []
    filename = 'network_new.json'

    def build(self):
        self.init_communication()

        TTS.start()

        self.sm = ScreenManager()

        screen = ZeroScreen()
        screen.start()
        screen.ids['subject_id'].bind(text=screen.ids['subject_id'].on_text_change)
        self.sm.add_widget(screen)

        concepts_path = 'items/'

        concepts_json = JsonStore(concepts_path + self.filename)
        print(concepts_json.keys())
        for i_net, net in enumerate(concepts_json.get("sequence")):
            self.game_screen.append(GameScreen(name='game_' + str(i_net)))
            self.game_screen[-1].start(number=i_net, the_app=self, the_type=(net['type'], net['n']),
                                       duration=net['duration'],
                                       introduction=net['introduction'],
                                       network=deepcopy(concepts_json.get(net['network'])),
                                       questions=deepcopy(concepts_json.get('questions')),
                                       edges=deepcopy(concepts_json.get('edges')))
            self.game_screen[-1].add_widget(self.game_screen[-1].curiosity_game.the_widget)

        for gs in self.game_screen:
            self.sm.add_widget(gs)

        self.sm.current = 'zero_screen'
        return self.sm

    def init_communication(self):
        KC.start(the_ip='192.168.1.254', the_parents=[self])  # 127.0.0.1
        KL.start(mode=[DataMode.file], pathname=self.user_data_dir)

    def on_connection(self):
        KL.log.insert(action=LogAction.data, obj='QWorldApp', comment='start')

    def press_start(self, pre_post):
        # self.game_screen.curiosity_game.filename = 'items_' + pre_post + '.json'
        self.sm.current = 'game_0'

if __name__ == '__main__':
    QWorldApp().run()
