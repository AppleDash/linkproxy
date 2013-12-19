class Tokenizer:
    @classmethod
    def tokenize(cls, str, toksep=" ", kvsep="="):
        returnable = {}
        kvpairs = str.split(toksep)
        for rawpair in kvpairs:
            k = rawpair.split(kvsep)[0]
            v = rawpair.split(kvsep)[1]
            returnable[k] = v
        return returnable

    @classmethod
    def remtok(cls, lst, tok):
        out = {}
        for k in lst:
            v = lst[k]
            if k != tok:
                out[k] = v
        return out

    @classmethod
    def join(cls, lst, toksep=" ", kvsep="="):
        out = ""
        for k in lst:
            v = lst[k]
            out += k
            out += kvsep
            out += toksep
        out = out[:-1]
        return out