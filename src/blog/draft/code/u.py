from functools import partial, reduce

itself = lambda x: x
plus = lambda x, y: x + y
minus = lambda x, y: x - y


class FBase:
    def __init__(self, f1=itself):
        self.f1 = f1

    def __add__(self, val):
        if type(val) == FBase:
            return FReducer(plus, self, val)
        else:
            return FBase(partial(plus, val))

    def __call__(self, args):
        if self._is_list_args(args) and len(args) == 1:
            return self.f1(args[0])
        else:
            return self.f1(args)

    def _is_list_args(self, args):
        return isinstance(args, tuple) or isinstance(args, list)

    def __getattr__(self, attr):
        import re
        mo = re.match('^_(\d{1,2})$', attr)
        if mo is not None:
            return FPos(int(mo.group(1)))
        else:
            return FBase(lambda x: getattr(x, attr))


class FReducer(FBase):
    def __init__(self, op, f1):
        self.op = op
        self.accum = None

    def __call__(self, args):
        if self._is_list_args(args):
            rest, last = args[:-1], args[-1]
            ex, ey = self.f1(rest), self.f2(last)
            return self.op(ex, ey)


class FPos(FBase):
    def __init__(self, pos, f1=itself):
        super(FPos, self).__init__(f1)
        self.pos = pos

    def __add__(self, val):
        if isinstance(val, FBase):
            return FBinaryPos(plus, self, val)
        else:
            return FPos(self.pos, partial(plus, val))

    def __call__(self, args, call_args=None):
        if call_args is None:
            return self.f1(args[self.pos])
        elif self._is_list_args(args) and len(args) == 1:
            return self.f1(call_args[self.pos])
        else:
            return call_args[self.pos]


class FBinaryPos(FBinary, FPos):
    def __call__(self, args, call_args=None):
        # this happens only on the top-level call
        if call_args == None:
            call_args = args

        if self._is_list_args(args):
            rest, last = args[:-1], args[-1]
            ex, ey = self.f1(rest, call_args), self.f2(last, call_args)
            return self.op(ex, ey)


_ = FBase()
for i in range(0, 30):
    globals()['_%d' % i] = FPos(i)

m = map(_._0 + _._1 + _._1, [(1,2,3), (3,4,5)])

m = map(_0 + _1 + _2, [(1, 2, 3)])
class C:
    speed = 10
m = map(_.speed, [C(), C(), C()])
# m = map(_ + _, [(1, 2), (2, 3), (3, 4)])
# m = map(_ + _ - _, [(1, 2, 3), (2, 3, 4), (3, 4, 5)])
print(list(m))
