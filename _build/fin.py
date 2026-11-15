# Python evaluator for the sheet formulas used in the decks: an independent check of the JavaScript engine and of LibreOffice.
# It covers the formula language of the exercises: + - * / ^, comparisons, IF, SUM, AVERAGE, MIN, MAX, ABS, ROUND,
# and the finance functions with Excel's argument order and sign convention.
import math, re

REF = re.compile(r'\$?([A-Z]{1,2})\$?(\d+)')
RNG = re.compile(r'\$?([A-Z]{1,2})\$?(\d+):\$?([A-Z]{1,2})\$?(\d+)')


def col(L):
    n = 0
    for ch in L: n = n * 26 + ord(ch) - 64
    return n - 1


def colname(i):
    s, i = '', i + 1
    while i > 0:
        m = (i - 1) % 26; s = chr(65 + m) + s; i = (i - 1) // 26
    return s


def _t(t): return 1 if t else 0


def PV(r, n, p=None, f=None, t=None):
    p, f, t = p or 0, f or 0, _t(t)
    if r == 0: return -(f + p * n)
    q = (1 + r) ** n
    return -(f + p * (1 + r * t) * (q - 1) / r) / q


def FV(r, n, p=None, v=None, t=None):
    p, v, t = p or 0, v or 0, _t(t)
    if r == 0: return -(v + p * n)
    q = (1 + r) ** n
    return -(v * q + p * (1 + r * t) * (q - 1) / r)


def PMT(r, n, v, f=None, t=None):
    f, t = f or 0, _t(t)
    if r == 0: return -(v + f) / n
    q = (1 + r) ** n
    return -(f + v * q) * r / ((1 + r * t) * (q - 1))


def NPER(r, p, v, f=None, t=None):
    f, t = f or 0, _t(t)
    if r == 0: return -(v + f) / p
    return math.log((p * (1 + r * t) - f * r) / (p * (1 + r * t) + v * r)) / math.log(1 + r)


def _root(F, lo=-0.99, hi=10.0):
    a, b = F(lo), F(hi)
    grid = [-0.99, -0.5, -0.2, 0, 0.01, 0.03, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]
    for x, y in zip(grid, grid[1:]):
        if F(x) * F(y) <= 0: lo, hi = x, y; break
    else:
        raise ValueError('#NUM!')
    for _ in range(400):
        m = (lo + hi) / 2
        if F(lo) * F(m) <= 0: hi = m
        else: lo = m
    return (lo + hi) / 2


def RATE(n, p, v, f=None, t=None, g=None):
    p, f, t = p or 0, f or 0, _t(t)
    return _root(lambda r: v + p * n + f if abs(r) < 1e-12 else v * (1 + r) ** n + p * (1 + r * t) * ((1 + r) ** n - 1) / r + f)


def _flat(xs):
    out = []
    for x in xs:
        if isinstance(x, list): out += [v for v in x if isinstance(v, (int, float)) and not isinstance(v, bool)]
        elif isinstance(x, (int, float)): out.append(x)
    return out


def NPV(r, *vals):
    return sum(v / (1 + r) ** (i + 1) for i, v in enumerate(_flat(vals)))


def IRR(vals, g=None):
    v = _flat([vals])
    return _root(lambda r: sum(c / (1 + r) ** i for i, c in enumerate(v)))


def ROUND(x, d=0):
    k = 10 ** int(d); y = abs(x) * k
    return math.copysign(math.floor(y + 0.5 + 1e-9 * max(1, y)) / k, x)


def SUM(*a): return sum(_flat(a))
def AVERAGE(*a): v = _flat(a); return sum(v) / len(v)
def MIN(*a): return min(_flat(a))
def MAX(*a): return max(_flat(a))
def ABS(x): return abs(x)
def POWER(a, b): return a ** b
def SQRT(a): return math.sqrt(a)
def IF(c, a, b=False): return a if c else b
def SUMPRODUCT(*ls): return sum(math.prod(x if isinstance(x, (int, float)) else 0 for x in t) for t in zip(*ls))


FUN = dict(PV=PV, FV=FV, PMT=PMT, NPER=NPER, RATE=RATE, NPV=NPV, IRR=IRR, ROUND=ROUND, SUM=SUM, AVERAGE=AVERAGE, MIN=MIN, MAX=MAX, ABS=ABS, POWER=POWER, SQRT=SQRT, IF=IF, SUMPRODUCT=SUMPRODUCT)


def to_py(f):
    """Excel formula (without '=') to a Python expression over _V(addr) and _R(a, b)."""
    e = RNG.sub(lambda m: f'_R("{m.group(1)}{m.group(2)}","{m.group(3)}{m.group(4)}")', f)
    e = re.sub(r'(?<![A-Z"])\$?([A-Z]{1,2})\$?(\d+)(?![\d("])', lambda m: f'_V("{m.group(1)}{m.group(2)}")', e)
    e = re.sub(r'(\d+(?:\.\d+)?)%', r'(\1/100)', e)
    e = e.replace('^', '**').replace('<>', '!=')
    e = re.sub(r'(?<![<>!=])=(?!=)', '==', e)
    for _ in range(3):
        e = re.sub(r'\(\s*,', '(None,', e); e = re.sub(r',\s*,', ',None,', e); e = re.sub(r',\s*\)', ',None)', e)
    return e


def evaluate(cells):
    """cells: address -> raw (number, text or '=formula'). Returns address -> value for every cell."""
    memo = {}

    def V(a):
        if a in memo: return memo[a]
        raw = cells.get(a)
        if raw is None or raw == '': v = None
        elif isinstance(raw, (int, float)): v = raw
        elif str(raw).startswith('='): v = eval(to_py(str(raw)[1:]), {'__builtins__': {}}, dict(FUN, _V=VV, _R=R))
        else:
            s = str(raw).strip()
            try: v = float(s.rstrip('%')) / (100 if s.endswith('%') else 1)
            except ValueError: v = s
        memo[a] = v
        return v

    def R(a, b):
        (c1, r1), (c2, r2) = [(col(m.group(1)), int(m.group(2))) for m in (REF.match(a), REF.match(b))]
        return [V(f'{colname(c)}{r}') for r in range(min(r1, r2), max(r1, r2) + 1) for c in range(min(c1, c2), max(c1, c2) + 1)]

    def VV(a):
        v = V(a)
        return 0 if v is None else v
    out = {}
    for a in cells:
        out[a] = V(a)
    return out, VV
