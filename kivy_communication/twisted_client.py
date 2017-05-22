#install_twisted_rector must be called before importing the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor, protocol


# the static class for the kivy communication
class KC:
    client = None

    @staticmethod
    def start(the_parents=None, the_ip=None):
        KC.client = TwistedClient(the_parents=the_parents, the_ip=the_ip)

    def __init__(self):
        pass


class EchoClient(protocol.Protocol):
    parents = []

    def __init__(self):
        pass

    def connectionMade(self):
        self.factory.client.on_connection(self.transport)
        for p in self.factory.client.parents:
            try:
                p.on_connection()
            except:
                print('parent ', p, ' has no on_connection')

    def dataReceived(self, data):
        self.factory.client.data_received(data)


class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, client):
        self.client = client

    def clientConnectionLost(self, conn, reason):
        self.client.send_status("connection lost:" + str(conn) + str(reason))

    def clientConnectionFailed(self, conn, reason):
        self.client.send_status("connection failed:" + str(conn) + str(reason))


class TwistedClient:
    connection = None
    parents = None
    ip = None
    factory = None

    def __init__(self, the_parents=None, the_ip=None):
        TwistedClient.parents = the_parents
        TwistedClient.ip = the_ip
        TwistedClient.factory = EchoFactory(TwistedClient)

    @staticmethod
    def add_parent(the_parent):
        if TwistedClient.parent is None:
            TwistedClient.parents = []
        TwistedClient.parents.append(the_parent)

    @staticmethod
    def connect_to_server(the_ip=None):
        if the_ip:
            TwistedClient.ip = the_ip
        if TwistedClient.ip:
            TwistedClient.send_status('connecting to ' + TwistedClient.ip)

            reactor.connectTCP(TwistedClient.ip, 8000, TwistedClient.factory)
        else:
            TwistedClient.print_message('missing ip!')

    @staticmethod
    def on_connection(connection):
        TwistedClient.send_status("connected successfully!")
        TwistedClient.connection = connection

    @staticmethod
    def send_message(*args):
        try:
            msg = args[0]
            if msg and TwistedClient.connection:
                TwistedClient.connection.write(msg)
        except:
            TwistedClient.send_status('incorrect message')

    @staticmethod
    def send_status(status):
        if TwistedClient.parents is not None:
            for p in TwistedClient.parents:
                try:
                    p.send_status(status)
                except:
                    pass
        print('status: ', status)

    @staticmethod
    def data_received(data):
        print('received data:', data, ' sending it to ', TwistedClient.parents)
        if TwistedClient.parents is not None:
            for p in TwistedClient.parents:
                try:
                    p.data_received(data)
                    print('twisted client: parent ', p, 'received ', data)
                except:
                    print('twisted client: parent ', p, ' has no data_received')
        print('data: ', data)

''' Example usage:
    def init_kc(self):
        KC.start(the_parents=[self], the_ip='127.0.0.1')

    def connect_to_server(self, *args):
        KC.client.connect_to_server(args[0])

    def send_message(self, *args):
        KC.client.send_message(str(args[0].text))

    def data_received(self, msg, *args):
        self.label.text += msg + '\n'

    def send_status(self, msg, *args):
        self.label.text += msg + '\n'
'''