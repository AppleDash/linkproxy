from util import Tokenizer
from line import Line

class Protocol():
    def __init__(self, other, tag):
        self.other = other
        self.tag = tag
        self.sock = None
        self.cache = {}

    def on_line_from_server(self, ln, raw):
        print("<- [%s] [RAW] %s" % (self.tag, raw))
        self.on_recv_unknown(raw)

    def on_write_line(self, raw):
        print("-> [%s] [RAW] %s" % (self.tag, raw))

    def send_to_other(self, ln):
        self.other.sock.send(bytes("%s\r\n" % (ln,), encoding="utf-8"))

    def send_to_server(self, ln):
        self.sock.send(bytes("%s\r\n" % (ln,), encoding="utf-8"))
        self.on_write_line(ln)

    def on_recv_unknown(self, raw):
        self.other.send_unknown(raw)

    def send_unknown(self, raw):
        self.send_to_server(raw)

    def on_capab(self, ln, flag, params):
        pass

    def send_capab(self, flag, params):
        pass

    #:SID EUID nick 1 ts modes ident vhost ip uid realhost * :Xena
    def on_euid(self, sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos):
        pass

    def send_euid(self, sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos):
        pass


class ProtocolUnreal(Protocol):
    pass


class ProtocolInspircd(Protocol):
    cmodes = ""
    umodes = ""

    def on_line_from_server(self, ln, raw):
        print("<- [%s] [RAW] %s" % (self.tag, raw))
        if ln.command == "CAPAB":
            flag = ln.params[0]
            params = ""
            if len(ln.params) > 1:
                params = ln.params[1]
            self.on_capab(ln, flag, params)
        elif ln.command == "UID":
            #:${SID} UID ${UID} TS Nickname realhost vhost ident ip ts modes :gecos
            sid = ln.hostmask.host
            uid = ln.params[0]
            ts = ln.params[1]
            nick = ln.params[2]
            realhost = ln.params[3]
            vhost = ln.params[4]
            ident = ln.params[5]
            ip = ln.params[6]
            modes = ln.params[7]
            gecos = ln.params[8]
            self.on_euid(sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos)
        else:
            self.on_recv_unknown(raw)

    def on_capab(self, ln, flag, params):
        self.send_to_server(ln.linestr)

    def send_capab(self, flag, params):
        out = "CAPAB %s" % (flag,)
        if params != "":
            out += " :%s" % (params,)
        self.send_to_server(out)


    def on_euid(self, sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos):
        self.other.send_euid(sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos)

    def send_euid(self, sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos):
        str = ":%s UID %s %s %s %s %s %s %s %s %s :%s" % (sid, uid, ts, nick, realhost, vhost, ident, ip, ts, modes, gecos)
        self.send_to_server(str)


class ProtocolCharybdis(Protocol):
    def on_line_from_server(self, ln, raw):
        if ln.command == "EUID":
            sid = ln.hostmask.host
            nick = ln.params[0]
            ts = ln.params[2]
            modes = ln.params[3]
            ident = ln.params[4]
            vhost = ln.params[5]
            ip = ln.params[6]
            uid = ln.params[7]
            realhost = ln.params[8]
            gecos = ln.linestr[10]
            self.on_euid(sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos)

    def on_capab(self, ln, flag, params):
        self.cache["CAPAB_PARAMS"] = params

    def on_euid(self, sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos):
        self.other.send_euid(sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos)

    def send_euid(self, sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos):
        #:${SID} EUID nick 1 ts modes ident vhost ip uid realhost * :Xena
        str = ":%s EUID %s 1 %s %s %s %s %s %s %s * :%s" % (sid, nick, ts, modes, ident, vhost, ip, uid, realhost, gecos)
        self.send_to_server(str)
