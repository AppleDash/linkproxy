from protocol import *
import socket
import threading
from line import Line
import select

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
            self.proto.on_line_from_server(ln, raw)

    def stop(self):
        self.running = False

class ProxyThread(threading.Thread):
    def __init__(self, proto1, proto2):
        super(ProxyThread, self).__init__()
        self.proto1 = proto1
        self.proto2 = proto2
        self.running = False

    def run(self):
        def readtoend(s):
            out = ""
            while 1:
                c = s.recv(1).decode()
                if c is None:
                    return None
                if c == "\r" or c == "\n":
                    return out.strip()
                out += c
        self.running = True
        while self.running:
            r, w, e = select.select([self.proto1.sock, self.proto2.sock], [], [])
            for s in r:
                raw = readtoend(s)
                ln = Line.parse(raw)
                if s == self.proto1.sock:
                    self.proto1.on_line_from_server(ln, raw)
                else:
                    self.proto2.on_line_from_server(ln, raw)
    def stop(self):
        self.running = False



class LinkProxy():
    protodict = {
        'unreal': ProtocolUnreal,
        'raw': Protocol,
        'inspircd': ProtocolInspircd
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
        self.t = ProxyThread(self.proto1, self.proto2)
        self.t.start()

lp = LinkProxy()
if lp.open("inspircd", 1234, "inspircd", 12345):
    while 1:
        try:
            pass
        except KeyboardInterrupt:
            break
lp.t.stop()
