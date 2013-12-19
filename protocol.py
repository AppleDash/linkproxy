class Protocol():
    def __init__(self, other, tag):
        self.other = other
        self.tag = tag
        self.sock = None

    def on_read_line(self, ln, raw):
        print("<- [%s] %s" % (self.tag, raw))
        self.on_recv_unknown(raw)

    def on_write_line(self, raw):
        print("-> [%s] %s" % (self.tag, raw))

    def send_to_other(self, ln):
        self.other.sock.send(bytes("%s\r\n" % (ln,), encoding="utf-8"))

    def send_to(self, ln):
        self.sock.send(bytes("%s\r\n" % (ln,), encoding="utf-8"))
        self.on_write_line(ln)

    def on_recv_unknown(self, raw):
        self.other.send_unknown(raw)

    def send_unknown(self, raw):
        self.send_to(raw)


class ProtocolUnreal(Protocol):
    pass