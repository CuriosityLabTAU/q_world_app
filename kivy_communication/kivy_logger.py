#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

is_pycrypto = True
try:
    from Crypto.PublicKey import RSA
except:
    print('no pycrypto')
    is_pycrypto = False
from datetime import datetime
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore
from kivy.uix.widget import Widget
from os.path import join
from twisted_client import *


# Enum DataMode: file, encrupted, communication
class DataMode:
    file = 'file'
    encrypted = 'encrypted'
    communication = 'communication'
    ros = 'ros'

    def __init__(self):
        pass


# Enum: LogAction: non, press, play, stop, move, down, up, text, spinner, data
class LogAction:
    none = 'none'
    press = 'press'
    play = 'play'
    stop = 'stop'
    move = 'move'
    down = 'down'
    up = 'up'
    text = 'text'
    spinner = 'spinner'
    data = 'data'

    def __init__(self):
        pass


# the static class for the kivy logger
class KL:
    log = None

    @staticmethod
    def start(mode=None, pathname=None, the_ip=None):
        if not pathname:
            return

        KL.log = KivyLogger
        KL.log.pathname = pathname

        if not the_ip:
            KL.log.configure()
        else:
            KL.log.ip = the_ip

        print(pathname)
        if mode is None:
            mode = []
            Logger.info("KL mode:" + str(mode))
        KL.log.set_mode(mode)

    @staticmethod
    def restart():
        KL.log.set_mode(KL.log.base_mode)

    def __init__(self):
        pass


# THE class
class KivyLogger:
    logs = []
    t0 = None
    base_mode = []
    public_key = None
    filename = None
    store = None

    pathname = ''
    ip = None

    @staticmethod
    def configure():
        try:
            the_file = KL.log.pathname + '/../kivy_communication/config.json'
            print(the_file)
            with open(the_file) as json_file:
                json_data = json.load(json_file)

            KL.log.ip = str(json_data['ip'])
        except:
            print('no json configure file')
            pass

    @staticmethod
    def __init__():
        KivyLogger.logs = []
        KivyLogger.t0 = datetime.now()

    @staticmethod
    def set_mode(mode):
        KivyLogger.base_mode = mode
        KivyLogger.t0 = datetime.now()
        if DataMode.file in KivyLogger.base_mode:
            KivyLogger.filename = join(KivyLogger.pathname,
                                       KivyLogger.t0.strftime('%Y_%m_%d_%H_%M_%S_%f') + '.log')
            KivyLogger.store = JsonStore(KivyLogger.filename)
            Logger.info("KivyLogger: " + str(KivyLogger.filename))

        if DataMode.communication in KivyLogger.base_mode:
            KivyLogger.connect()

        if not is_pycrypto:
            if DataMode.encrypted in KivyLogger.base_mode:
                KivyLogger.base_mode.remove(DataMode.encrypted)

        if DataMode.encrypted in KivyLogger.base_mode:
            KivyLogger.get_public_key()
            KivyLogger.save('public_key:' + KivyLogger.public_key.exportKey("PEM"))

    @staticmethod
    def reset():
        KivyLogger.logs = []
        KivyLogger.t0 = datetime.now()

    @staticmethod
    def insert(action=LogAction.none, obj='', comment='', t=None, mode=None, sync=True):
        if t is None:
            t = datetime.now()
        data = {'time':t, 'action':action, 'obj':obj, 'comment':comment}
        KivyLogger.logs.append(data)
        if not mode:
            mode = KivyLogger.base_mode

        data_str = KivyLogger.to_str(data)

        if DataMode.encrypted in mode:
            data_str = KivyLogger.encrypt(data_str)

        if DataMode.communication in mode:
            KivyLogger.send_data(data_str)

        if DataMode.file in mode:
            KivyLogger.save(data_str, sync)

    # file
    @staticmethod
    def save(data_str, sync):
        #print(data_str)
        try:
            if DataMode.encrypted in KivyLogger.base_mode:
                KivyLogger.store.put(datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'),
                                     data=str(data_str).encode('ascii'))
            # else:
            #     KivyLogger.store.put(datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'),
            #                          data=data_str)
            else:
                # update only the dic. need store_sync
                KivyLogger.store.store_put(datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f'), data_str)
                if sync:
                    KivyLogger.store.store_sync()
            Logger.info("save:" +str(sync)+":"+str(KivyLogger.filename))
        except Exception,e:
            print str(e)
            Logger.info("save: did not work")

    # encryption
    @staticmethod
    def to_str(log):
        data = {'time': log['time'].strftime('%Y_%m_%d_%H_%M_%S_%f'),
                'action': log['action'],
                'obj': log['obj'],
                'comment': log['comment']}
        if DataMode.ros in KivyLogger.base_mode:
            data = {'log': data}
        return str(json.dumps(data))

    @staticmethod
    def get_public_key():
        if DataMode.communication in KivyLogger.base_mode:
            # get from communication
            pub_pem = KivyLogger.socket.recv(1024)
        else:
            private_key = RSA.generate(2048, e=65537)
            prv_pem = private_key.exportKey("PEM")
            store = JsonStore(KivyLogger.filename + '.enc')
            store.put('private_key', pem=prv_pem)

            pub_pem = private_key.publickey().exportKey("PEM")

        KivyLogger.public_key = RSA.importKey(pub_pem)
        pass

    @staticmethod
    def encrypt(data_str):
        if DataMode.encrypted in KivyLogger.base_mode:
            data_str = KivyLogger.public_key.encrypt(data_str, 32)
            return data_str
        return data_str

    # communication
    @staticmethod
    def connect():
        try:
            if TwistedClient.ip is None:
                KC.client = TwistedClient(the_ip=KL.log.ip)
            KC.client.connect_to_server(KC.client.ip)
        except:
            KivyLogger.base_mode.remove(DataMode.communication)
            Logger.info("connect: fail")
        pass

    @staticmethod
    def send_data(data_str):
        if DataMode.communication in KivyLogger.base_mode:
            KC.client.send_message(data_str.encode())
        pass

    @staticmethod
    def __del__():
        if KivyLogger.socket is not None:
            KivyLogger.socket.close()


class WidgetLogger(Widget):
    name = ''

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.log_touch(LogAction.down, touch)
            super(WidgetLogger, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            #self.log_touch(LogAction.move, touch)
            super(WidgetLogger, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.log_touch(LogAction.up, touch)
            super(WidgetLogger, self).on_touch_up(touch)

    def on_press(self, *args):
        super(WidgetLogger, self).on_press(*args)
        KL.log.insert(action=LogAction.press, obj=self.name, comment='', sync=False)

    def log_touch(self, action, touch):
        if KL.log is not None:
            Logger.info("KivyLogger log_touch:" + str(touch.profile) + str(action))
            comment = {}
            if 'angle' in touch.profile:
                comment['angle'] = touch.a
            if 'pos' in touch.profile:
                comment['pos'] = str(touch.pos)
            if 'button' in touch.profile:
                comment['button'] = touch.button

            KL.log.insert(action=action, obj=self.name, comment=json.dumps(comment),sync=False)

    def on_play_wl(self, filename):
        KL.log.insert(action=LogAction.play, obj=self.name, comment=filename)

    def on_stop_wl(self, filename):
        KL.log.insert(action=LogAction.stop, obj=self.name, comment=filename)

    def on_text_change(self, instance, value):
        KL.log.insert(action=LogAction.text, obj=self.name, comment=self.text)

    def on_spinner_text(self, instance, value):
        KL.log.insert(action=LogAction.spinner, obj=self.name, comment=value)

    def force_on_touch_down(self, touch):
        self.log_touch(LogAction.down, touch)

    def force_on_touch_up(self, touch):
        self.log_touch(LogAction.up, touch)

''' Example usage:
KL.start([DataMode.file], "/sdcard/curiosity/")#self.user_data_dir)
# Logged* widgets
'''