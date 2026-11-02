"""ANGLE-circuit emitter for the dfthcsos task: J = 5 words per circuit, brot = 8, 128 qubits.

Address a (11 bits) = 4 low bits + 7 high bits. Each output bit of the batch delta is a GF(2) polynomial in the
address bits; its monomials split into high-only, low-only and mixed (high x low) parts.

Qubits: selection 0..10, word j bit b = 11 + 8j + b, workspace 51..127 (77) plus the five bit-7 qubits, which are
borrowed (cleared by CX bit6 -> bit7 at the start; the sign gauge bit7 == bit6 holds for every batch).

1. High cache: all high monomials (masks 1..85) are kept on qubits for the whole circuit. The 7 single bits are
   selection qubits; the other 78 cost one Toffoli each.
2. Three low stages (low masks 1-7, 8-11, 12-15). A stage computes its non-trivial low monomials into 4 slots
   (4, 3 and 4 Toffolis), emits the products of its plan, then clears the slots with measurement-based AND
   uncomputation (no Toffolis). One product AND(h1 + l2, h2 + l1) of two linear forms over the cached monomials
   has mixed part h1 l1 + h2 l2, so one Toffoli gives two rank-one mixed terms, XORed into several outputs.
3. The remaining pure parts (high-only, low-only, constant) are linear in the cached monomials, so they cost only
   CNOTs. They are found by exact simulation of pass 1 and added in pass 2.

compile_circuit asserts, over all NA addresses, every output bit, bit 7, a clean workspace and unchanged selection.
Written for the Kaggle "Google Quantum AI - Verifiable Quantum Circuit Compilation" competition. Apache-2.0.
"""
import numpy as np
NA = 1363; NSEL = 11; J = 5; BROT = 8
B7 = [11 + 8 * j + 7 for j in range(J)]; B6 = [11 + 8 * j + 6 for j in range(J)]
OUTQ = [11 + 8 * j + b for j in range(J) for b in range(7)]      # output o = 7j + b
def bits(v):
    while v:
        b = v & -v; yield b.bit_length() - 1; v ^= b
ADDR = [sum(((a >> i) & 1) << a for a in range(NA)) for i in range(NSEL)]   # truth tables as ints over addresses
FULL = (1 << NA) - 1
def anf_valid(tt):
    """ANF over valid masks (0..NA-1) of a truth table int over valid addresses; returns int bitset over masks."""
    v = np.array([(tt >> a) & 1 for a in range(NA)], dtype=np.uint8)
    pad = np.zeros(2048, dtype=np.uint8); pad[:NA] = v
    for b in range(11):
        idx = np.arange(2048); sel = (idx >> b) & 1 == 1
        pad[sel] ^= pad[idx[sel] ^ (1 << b)]
    c = pad[:NA]
    return c
class Emit:
    def __init__(self):
        self.ops = []; self.tof = 0
    def cx(self, a, b): self.ops.append(('CX', a, b))
    def x(self, a): self.ops.append(('X', a))
    def ccx(self, a, b, c): self.ops.append(('CCX', a, b, c)); self.tof += 1
    def dand(self, a, b, c): self.ops.append(('DAND', a, b, c))
def simulate(ops, z=None):
    v = [0] * 128
    for i in range(NSEL): v[i] = ADDR[i]
    if z is not None:
        for q, t in z.items(): v[q] = t
    for op in ops:
        if op[0] == 'CX': v[op[2]] ^= v[op[1]]
        elif op[0] == 'X': v[op[1]] ^= FULL
        elif op[0] == 'CCX': v[op[3]] ^= v[op[1]] & v[op[2]]
        elif op[0] == 'DAND':
            a, b, c = op[1:]
            assert v[c] == v[a] & v[b], ('bad uncompute', op)
            v[c] = 0
    return v
def layout():
    high = {}; cache = []; free = list(B7) + list(range(51, 124)); slots = [124, 125, 126, 127]
    for mask in range(1, 86):
        top = mask.bit_length() - 1
        if mask & (mask - 1) == 0: high[mask] = 4 + top
        else:
            q = free.pop(0); high[mask] = q; cache.append((high[mask ^ (1 << top)], 4 + top, q))
    assert not free
    return high, cache, slots
# low cache plan per stage: (mask, parent qubit spec) - parents are low masks
STAGE_LOW = {1: [1, 2, 3, 4, 5, 6, 7], 2: [8, 9, 10, 11], 3: [12, 13, 14, 15]}
LOW_BUILD = {1: [(3, 1, 2), (5, 1, 4), (6, 2, 4), (7, 6, 1)], 2: [(9, 1, 8), (10, 2, 8), (11, 9, 2)],
             3: [(12, 4, 8), (13, 12, 1), (14, 12, 2), (15, 13, 2)]}
def build(delta, stage_terms, outs, extra=(), pure=None):
    """delta: (NA, J) ints.  stage_terms: {stage: terms (planner format, directions over `outs`)}.
    extra: products (f40, a1, b1, a2, b2) in v47 extract format (f over 8j+b, a* low ANF masks, b* high masks);
    their low factors may use only low masks 1,2,4,8.  pure: precomputed pure corrections (None = pass 1)."""
    E = Emit(); high, cache, slots = layout()
    H = 85
    def targets(direction_full):
        return [OUTQ[o] for o in bits(direction_full)]
    def full_dir(d):
        return sum(1 << outs[i] for i in bits(d))
    def product(left, right, dfull, basis):
        if not left or not right or not dfull: return
        tg = targets(dfull)
        if left == right:
            for i in bits(left):
                for q in tg: E.cx(basis[i], q)
            return
        p = (left & -left).bit_length() - 1
        first = list(bits(left ^ (1 << p)))
        for i in first: E.cx(basis[i], basis[p])
        if (right >> p) & 1: right ^= left ^ (1 << p)
        choices = right & ~(1 << p)
        if not choices: raise AssertionError('dependent controls')
        q = (choices & -choices).bit_length() - 1
        second = list(bits(right ^ (1 << q)))
        for i in second: E.cx(basis[i], basis[q])
        pivot, *others = tg
        for o in others: E.cx(pivot, o)
        E.ccx(basis[p], basis[q], pivot)
        for o in others: E.cx(pivot, o)
        for i in reversed(second): E.cx(basis[i], basis[q])
        for i in reversed(first): E.cx(basis[i], basis[p])
    for a, b in zip(B6, B7): E.cx(a, b)
    for a, b, c in cache: E.ccx(a, b, c)
    hbasis = [high[h] for h in range(1, 86)]
    lowq = {1: 0, 2: 1, 4: 2, 8: 3}
    # extra products (address-bit low factors only): emit first, basis = high + low address bits
    xb = hbasis + [0, 1, 2, 3]
    for (f, a1, b1, a2, b2) in extra:
        def form(lo, hi):
            v = 0
            for h in bits(hi >> 1): v |= 1 << h               # high masks 1..85 -> index h-1
            for l in bits(lo >> 1):
                l += 1; assert l in lowq, 'extra product uses a cached low monomial'
                v |= 1 << (H + [1, 2, 4, 8].index(l))
            return v
        fo = 0
        for o in bits(f):
            j, b = divmod(o, 8); assert b < 7
            fo |= 1 << (7 * j + b)
        product(form(a1, b1), form(a2, b2), fo, xb)
    for st in (1, 2, 3):
        built = []
        for mask, pa, pb in LOW_BUILD[st]:
            q = slots[len(built)]
            E.ccx(lowq[pa], lowq[pb], q); lowq[mask] = q; built.append((mask, lowq[pa], lowq[pb], q))
        basis = hbasis + [lowq[l] for l in STAGE_LOW[st]]
        for term in stage_terms.get(st, []):
            fs = term['factors']; d = full_dir(term['target_direction'])
            for i in range(0, len(fs), 2):
                h1, l1 = fs[i]
                if i + 1 == len(fs): product(h1, l1 << H, d, basis)
                else:
                    h2, l2 = fs[i + 1]
                    product(h1 ^ (l2 << H), h2 ^ (l1 << H), d, basis)
        if pure is not None:
            for l in STAGE_LOW[st]:
                for q in targets(pure['low'][l]): E.cx(lowq[l], q)
        for mask, a, b, q in reversed(built):
            E.dand(a, b, q); del lowq[mask]
    if pure is not None:
        for q in targets(pure['const']): E.x(q)
        for h in range(1, 86):
            for q in targets(pure['high'][h]): E.cx(high[h], q)
    for a, b, c in reversed(cache): E.dand(a, b, c)
    for a, b in zip(B6, B7): E.cx(a, b)
    return E
def delta_tt(delta):
    """truth tables (ints over addresses) of the 35 output bits o = 7j+b."""
    out = []
    for j in range(J):
        col = delta[:, j]
        for b in range(7):
            out.append(sum(int((col[a] >> b) & 1) << a for a in range(NA)))
    return out
def compile_circuit(delta, stage_terms, outs, extra=()):
    target = delta_tt(delta)
    E1 = build(delta, stage_terms, outs, extra, None)
    v = simulate(E1.ops)
    res = [target[o] ^ v[OUTQ[o]] for o in range(35)]
    coef = [anf_valid(r) for r in res]            # per output: coefficient array over masks
    pure = {'const': 0, 'low': {l: 0 for l in range(1, 16)}, 'high': {h: 0 for h in range(1, 86)}}
    mixed = 0
    for o in range(35):
        c = coef[o]
        for m in np.nonzero(c)[0]:
            m = int(m); lo, hi = m & 15, m >> 4
            if lo and hi: mixed += 1
            elif lo: pure['low'][lo] |= 1 << o
            elif hi: pure['high'][hi] |= 1 << o
            else: pure['const'] |= 1 << o
    if mixed: raise AssertionError(f'{mixed} mixed residual monomials')
    E2 = build(delta, stage_terms, outs, extra, pure)
    v = simulate(E2.ops)
    for o in range(35): assert v[OUTQ[o]] == target[o], ('output mismatch', o)
    for j in range(J): assert v[B7[j]] == target[7 * j + 6]
    for q in range(51, 128): assert v[q] == 0
    for i in range(NSEL): assert v[i] == ADDR[i]
    return E2
def to_kickmix(E):
    import kickmix as km        # from the competition data (kickmix/kickmix.so)
    b = km.CircuitBuilder()
    qs = list(b.create_quantum_register(NSEL, 'selection'))
    for j in range(J): qs += list(b.create_quantum_register(BROT, f'word_{j}'))
    qs += list(b.alloc_qubits(128 - len(qs)))
    for op in E.ops:
        if op[0] == 'CX': b.cx(qs[op[1]], qs[op[2]])
        elif op[0] == 'X': b.x(qs[op[1]])
        elif op[0] == 'CCX': b.ccx(qs[op[1]], qs[op[2]], qs[op[3]])
        elif op[0] == 'DAND': b.del_and(qs[op[1]], qs[op[2]], qs[op[3]])
    c = b.finish_circuit()
    assert c.operation_statistics().num_toffoli_like == E.tof
    return c
