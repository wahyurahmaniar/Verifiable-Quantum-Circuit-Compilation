def external_node_chain(b, words, gi, reverse=False, token=None, normalizer=None):
    if not reverse or gi not in SELECT:
        result = forward_original(b, words, gi, reverse, token, normalizer)
        if not reverse and gi >= _carry_start and gi in SELECT:
            _carry_manager.push(b, result, gi)
        elif not reverse and gi == 6 and gi in SELECT:
            m6 = b.alloc_bits(1)
            b.hmr(result['pole'], m6[0])
            b.free(result['pole'])
            result['pole'] = None
            _p6_state[id(b)] = dict(mask=m6)
        return result
    gn = ref.groups[gi]
    N = combine(words[gn['word']:gn['word']+2])
    L = combine(words[gn['word']+2:gn['word']+4])
    heads = [words[2*i:2*i+2] for i in range(2*gi)]
    params = []
    c = 0
    for i in range(2*gi):
        q = ref.ks[i] ^ gn['kap']
        params.append((q, c))
        c ^= inv(q)
    assert c == 0
    bank = token['carry_bank'] if gi >= _carry_start else None
    if bank is not None:
        pole = bank.take(gi)
    elif gi == 6:
        st = _p6_state.pop(id(b))
        pole = st['pole']
        b.cz(pole, st['mask'][0])
        b.free(st['mask'])
    else:
        pole = None
    R = b.alloc_qubits(24)
    b.cx(N, R)
    D = b.alloc_qubits(24)
    b.x(D[0])
    if pole is not None:
        b.cx(pole, N[0])
        b.cx(pole, D[0])
    for head, (q, c) in reversed(list(zip(heads, params))[1:]):
        ref.external_chain_step(b, head, N, D, L, q, gn['c'], c, True)
    q0 = params[0][0]
    scalepair(b, N, inv(q0))
    b.swap(N, D)
    scalepair(b, L, inv(q0))
    with b.mark('companion_normalize'):
        norm, F = normalize_three(b,N,D,L,R)
    with b.mark('companion_fused_chart'):
        original = finish_fused(b,D,F,token['norm'],norm,N,L,R,heads[0],gn['c'])
    if pole is not None:
        b.cswap(pole, N, D)
    if bank is not None:
        next_pole = _previous_pole_bits(b, pole, _pole_bits(gi, combine(words[4*(gi-1):4*(gi-1)+2]))) if gi > _carry_start else None
        bank.advance(gi, next_pole)
    if gi == 7:
        _p6_state[id(b)]['pole'] = _zero_pole(b, combine(words[4*(gi-1):4*(gi-1)+2]))
    if pole is not None:
        fm = b.alloc_bits(1)
        b.hmr(pole, fm[0])
        b.free(pole)
        b.push_condition(fm[0])
        clean_zero_phase24(b, D)
        b.pop_condition()
        b.free(fm)
    with b.mark('companion_return'):
        for i in reversed(range(len(heads))):
            if i == 1:
                scalar_erase_second24(b, heads[i], N, D, params[i][0], gn['c'], q0)
            else:
                ref.external_scalar_step(b, heads[i], N, D, params[i][0], gn['c'], True, first=i == 0)
    b.x(D[0])
    b.free(D)
    b.cz(N, original)
    b.free(original)
