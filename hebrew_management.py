#!/usr/bin/python
# -*- coding: utf-8 -*-

class HebrewManagement():

    @staticmethod
    def multiline(text, num_char, start_to_end=False):
        text0 = text
        if start_to_end:
            text0 = text0[::-1]
        new_lines = []
        i = 0
        while i < len(text0):
            j = 0
            txt = ""
            while j < num_char or not text0[i].isspace():
                if text0[i] == "*":
                    i = i+1
                    break
                txt += text0[i]
                j = j+1
                i = i+1
                if not i < len(text0):
                    break

            new_lines.append(txt.strip())

        return new_lines