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
        #print("[%s] -> [%s] %s" % (self.tag, self.other.tag, raw))
        self.on_write_override(raw, Line.parse(raw))

    def on_write_override(self, raw, ln):
        pass

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
        else:
            self.on_recv_unknown(raw)

    def on_capab(self, ln, flag, params):
        if flag == "USERMODES" or flag == "CHANMODES":
            self.send_to_server(ln.linestr)
            print("-- [%s] Echoed back CAPAB USERMODES/CHANMODES to fool InspIRCd..." % (self.tag,))
        elif flag == "CAPABILITIES":
            if "CHANMODES" in params:
                self.send_to_server(ln.linestr)
            else:
                self.on_recv_unknown(ln.linestr)
            tokens = Tokenizer.tokenize(params)
            for k in tokens:
                v = tokens[v]

        else:
            self.on_recv_unknown(ln.linestr)

    def send_capab(self, flag, params):
        out = "CAPAB %s" % (flag,)
        if params != "":
            out += " :%s" % (params,)
        self.send_to_server(out)


class ProtocolCharybdis(Protocol):
    def on_capab(self, ln, flag, params):
        self.cache["CAPAB_PARAMS"] = params
