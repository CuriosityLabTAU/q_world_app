#!/usr/bin/python
# -*- coding: utf-8 -*-

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy_logger import WidgetLogger


class MySpinnerOption(SpinnerOption):
    pass


class LoggedSpinner(WidgetLogger, Spinner):
    pass


class LoggedTextInput(WidgetLogger, TextInput):
    pass
# requires:
#   textinput.bind(text=textinput.on_text_change)


class LoggedButton(WidgetLogger, Button):
    pass


class LoggedCheckBox(WidgetLogger, CheckBox):
    pass


class AnswerButton(WidgetLogger, CheckBox):
    question = ""
    answer = ""
    form = None

    def on_press(self, *args):
        super(AnswerButton, self).on_press(*args)
        self.form.set_answer(self.question, self.answer)
