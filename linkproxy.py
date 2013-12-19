from protocol import *
import socket
import threading
from line import Line

class HandlerThread(threading.Thread):
    def __init__(self, proto):
        super(HandlerThread, self).__init__()
        self.proto = proto
        self.sock = proto.sock
        self.running = False

    def run(self):
        self.running = True
        for raw in self.sock.makefile("r"):
            if not self.running or raw is None or raw == "":
                break
            raw = raw.strip()
            ln = Line.parse(raw)
            self.proto.on_read_line(ln, raw)

    def stop(self):
        self.running = False


class LinkProxy():
    protodict = {
        'unreal': ProtocolUnreal
    }

    def __init__(self):
        pass

    def open(self, proto1, port1, proto2, port2):
        try:
            proto1 = self.protodict[proto1]
            proto2 = self.protodict[proto2]
        except KeyError:
            print("Error opening proxy, invalid link protocol given.")
            return False

        self.port1 = port1
        self.port2 = port2
        self.proto1 = proto1(None, "Server1")
        self.proto2 = proto2(self.proto1, "Server2")
        self.proto1.other = self.proto2
        self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock1.bind(("", self.port1))
            self.sock1.listen(1)
            self.sock2.bind(("", self.port2))
            self.sock2.listen(1)
        except Exception as ex:
            print("Error opening proxy, couldn't bind socket.")
            print(str(ex))
            return False
        self.run()
        return True

    def run(self):
        (s1, addr) = self.sock1.accept()
        print("Accepted s1")
        (s2, addr) = self.sock2.accept()
        print("Accepted s2")
        self.proto1.sock = s1
        self.proto2.sock = s2
        self.t1 = HandlerThread(self.proto1)
        self.t2 = HandlerThread(self.proto2)
        self.t1.start()
        self.t2.start()

lp = LinkProxy()
if lp.open("unreal", 6668, "unreal", 6667):
    while 1:
        try:
            pass
        except KeyboardInterrupt:
            break
lp.t1.stop()
lp.t2.stop()
