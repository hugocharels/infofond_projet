from collections import defaultdict
from functools import wraps
from inspect import getfullargspec

from project import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

########################################
#                TESTS                 #
########################################

def test_function(fct):
    @wraps(fct)
    def wrapper(*args, **kwargs):
        marker = blue('='*10)
        print(marker, 'Entering test function:', fct.__name__.ljust(15), marker)
        fct(*args, *kwargs)
        print(marker, 'Exiting test function: ', fct.__name__.ljust(15), marker, end='\n\n')
    return wrapper

def verify(prefix: str, fa, pos: list[str], neg: list[str]) -> bool:
    is_ok = True
    for word in pos:
        if not fa.accepts_input(word):
            print(f'{prefix} Word "{word}" should be accepted')
            is_ok = False
    for word in neg:
        if fa.accepts_input(word):
            is_ok = False
            print(f'{prefix} Word "{word}" should be rejected')
    return is_ok

def test_positive(caller, callback, instances, additional_verif=None):
    nb_args = len(getfullargspec(callback).args)
    for counter, args in enumerate(instances, start=1):
        prefix = (f'[{caller}+:Test {counter}]').ljust(20)
        fa = callback(*args[:nb_args])
        if fa is None:
            print(f'\t{prefix} Test {red("failed")}: no solution found')
            continue
        pos, neg = args[1:3]
        is_ok = verify(prefix, fa, pos, neg)
        if additional_verif is not None:
            is_ok = is_ok and additional_verif(prefix, fa, args)
        print(f'\t{prefix} Test {green("passed") if is_ok else red("failed")}')

def test_negative(caller, callback, instances, additional_verif=None):
    nb_args = len(getfullargspec(callback).args)
    for counter, args in enumerate(instances, start=1):
        prefix = (f'[{caller}-:Test {counter}]').ljust(20)
        fa = callback(*args[:nb_args])
        if fa is None:
            print(f'\t{prefix} Test {green("passed")}')
            continue
        pos, neg = args[1:3]
        is_ok = verify(prefix, fa, pos, neg)
        if additional_verif is not None:
            additional_verif(prefix, fa, args)
        print(f'\t{prefix} Test {red("failed")}')

def verify_size(prefix: str, fa: FA, args: tuple) -> bool:
    k = args[3]
    Q = fa.states
    is_ok = len(Q) <= k
    if not is_ok:
        states = f'state{"s" if len(Q) > 1 else ""}'
        print(f'{prefix} Automaton has {len(Q)} {states}, which is > {k}')
    return is_ok

EMPTY_SET = frozenset()
def verify_complete(prefix: str, dfa: DFA, args: tuple) -> bool:
    is_ok = verify_size(prefix, dfa, args)
    Q = dfa.states
    delta = dfa.transitions
    Sigma = args[0]
    for q in Q:
        for sigma in Sigma:
            if sigma not in delta.get(q, EMPTY_SET):
                is_ok = False
                print(f'{prefix} no transition w/ symbol "{sigma}" from state "{q}"')
    return is_ok

def verify_reversible(prefix: str, dfa: DFA, args: tuple) -> bool:
    is_ok = verify_size(prefix, dfa, args)
    Sigma = args[0]
    Q = dfa.states
    delta = dfa.transitions
    reversed_delta = {q: defaultdict(int) for q in Q}
    for qprime in Q:
        for sigma in Sigma:
            for q, delta_q in delta.items():
                if sigma in delta_q and qprime == delta_q[sigma]:
                    reversed_delta[q][sigma] += 1
                    if reversed_delta[q][sigma] == 2:
                        is_ok = False
                        print(f'{prefix} Automaton not reversible: ' +
                              f'state "{qprime}" has >= 2 incoming transitions w/ symbol {sigma}')
    return is_ok

def verify_final_states(prefix: str, dfa: DFA, args: tuple) -> bool:
    is_ok = verify_size(prefix, dfa, args)
    ell = args[4]
    F = dfa.final_states
    is_ok_for_ell = len(F) <= ell
    if not is_ok_for_ell:
        print(f'{prefix} Automaton has too many final states: {len(F)}, which is > {ell}')
    return is_ok and is_ok_for_ell

@test_function
def test_aut():
    test_positive('test_aut', gen_aut, POSITIVE_DFA_INSTANCES, verify_size)
    test_negative('test_aut', gen_aut, NEGATIVE_DFA_INSTANCES, verify_size)

@test_function
def test_minaut():
    test_positive('test_minaut', gen_minaut, POSITIVE_MINDFA_INSTANCES, verify_size)

@test_function
def test_autc():
    test_positive('test_autc', gen_autc, POSITIVE_CDFA_INSTANCES, verify_complete)
    test_negative('test_autc', gen_autc, NEGATIVE_CDFA_INSTANCES, verify_complete)

@test_function
def test_autr():
    test_positive('test_autr', gen_autr, POSITIVE_RFA_INSTANCES, verify_reversible)
    test_negative('test_autr', gen_autr, NEGATIVE_RFA_INSTANCES, verify_reversible)

@test_function
def test_autcard():
    test_positive('test_autcard', gen_autcard, POSITIVE_CARD_DFA_INSTANCES, verify_final_states)
    test_negative('test_autcard', gen_autcard, NEGATIVE_CARD_DFA_INSTANCES, verify_final_states)

@test_function
def test_autn():
    test_positive('test_autn[DFA]', gen_autn, POSITIVE_DFA_INSTANCES, verify_size)
    test_positive('test_autn', gen_autn, POSITIVE_NFA_INSTANCES, verify_size)
    test_negative('test_autn', gen_autn, NEGATIVE_NFA_INSTANCES, verify_size)

# (\Sigma, P, N, k)
POSITIVE_DFA_INSTANCES = [
    # L(A) = words of even length
    ('a',  ['', 'aa', 'aaaaaa'], ['a', 'aaa', 'aaaaa'], 2),
    # L(A) = a^*
    ('ab', ['', 'a', 'aa', 'aaa', 'aaaa'], ['b', 'ab', 'ba', 'bab', 'aba'], 1),
    # L(A) = words with at least one b
    ('ab', ['b', 'ab', 'ba', 'abbb', 'abba'], ['', 'aaa', 'a', 'aa'], 2),
    # L(A) = words where every chain consecutive b's has length >= 2
    ('ab', ['', 'aa', 'aaaa', 'a', 'abb', 'bb', 'abba', 'bbbb', 'bbba', 'abbb'],
           ['b', 'aba', 'ba', 'ab', 'abbab', 'bbabbab', 'babba'], 3),
    # L(A) = {aa, ab, ba}
    ('ab', ['aa', 'ab', 'ba'], ['', 'a', 'b', 'bb', 'aaa', 'aba', 'bba'], 4),
    # L(A) = a^+ @ a^+ . a^+
    ('a@.', ['a@a.a', 'aa@a.a'],
            ['', '.', '..a', '.a', '@', '@.', '@.a', '@a', '@a.', '@a.a', '@aa', 'a', 'a.', 'a.a', 'a@',
            'a@.', 'a@.a', 'a@a', 'a@a.', 'a@aa', 'aa', 'aa.', 'aa.a', 'aaa'], 6),
]
# (\Sigma, P, N, min_k)
POSITIVE_MINDFA_INSTANCES = [
    # L(A) = a^*
    ('a', ['', 'a'], [], 1),
    # L(A) = \emptyset
    ('abc', [], ['', 'a'], 1),
    # L(A) = words whose 3rd last symbol (in the sense word[-3]) is b
    ('ab', ['abaa', 'baa', 'baaabba', 'baabbb', 'bab', 'babaa', 'babbab', 'babbb', 'bba', 'bbaa', 'bbab', 'bbabba', 'bbb', 'bbba', 'bbbab', 'bbbb', 'bbbba', 'bbbbab'],
           ['', 'a', 'aa', 'aaa', 'b', 'ba', 'baaa', 'baaaa', 'baab', 'baba', 'bababb', 'babb', 'bb', 'bbaaa', 'bbaaba', 'bbabb', 'bbbabb'], 8),
]
# (\Sigma, P, N, k)
POSITIVE_CDFA_INSTANCES = [
    # L(A) = a^*
    ('ab', ['', 'a', 'aa', 'aaa', 'aaaa'], ['b', 'ab', 'ba', 'bab', 'aba'], 2),
    # L(A) = words where every chain consecutive b's has length >= 2
    ('ab', ['', 'aa', 'aaaa', 'a', 'abb', 'bb', 'abba', 'bbbb', 'bbba', 'abbb'],
           ['b', 'aba', 'ba', 'ab', 'abbab', 'bbabbab', 'babba'], 4),
]
# (\Sigma, P, N, k)
POSITIVE_RFA_INSTANCES = [
    # L(A) = words with an odd number of b's
    ('ab', ['b', 'ab', 'ba', 'aba', 'abbba', 'bbababab'], ['', 'a', 'bba', 'aaa', 'aa', 'abab'], 2),
    # L(A) = {aa, ab, ba}
    ('ab', ['aa', 'ab', 'ba'], ['', 'a', 'b', 'bb', 'aaa', 'aba', 'bba'], 5),
]
# (\Sigma, P, N, k, ell)
POSITIVE_CARD_DFA_INSTANCES = [
    # L(A) = a^*
    ('a', ['', 'a', 'aa', 'aaa'], [], 3, 1)
]
# (\Sigma, P, N, k)
POSITIVE_NFA_INSTANCES = [
    # L(A) = words whose 3rd last symbol (in the sense word[-3]) is b
    ('ab', ['abaa', 'baa', 'baaabba', 'baabbb', 'bab', 'babaa', 'babbab', 'babbb', 'bba', 'bbaa', 'bbab', 'bbabba', 'bbb', 'bbba', 'bbbab', 'bbbb', 'bbbba', 'bbbbab'],
           ['', 'a', 'aa', 'aaa', 'b', 'ba', 'baaa', 'baaaa', 'baab', 'baba', 'bababb', 'babb', 'bb', 'bbaaa', 'bbaaba', 'bbabb', 'bbbabb'], 4),
]

# (\Sigma, P, N, k)
NEGATIVE_DFA_INSTANCES = [
    # L(A) = a^+
    ('a', ['a', 'aa', 'aaa'], [''], 1),
    # L(A) = {aa, ab, ba}
    ('ab', ['aa', 'ab', 'ba'], ['', 'a', 'b', 'bb', 'aaa', 'aba', 'bba'], 3),
    # L(A) = words whose 3rd last symbol (in the sense word[-3]) is b
    ('ab', ['abaa', 'baa', 'baaabba', 'baabbb', 'bab', 'babaa', 'babbab', 'babbb', 'bba', 'bbaa', 'bbab', 'bbabba', 'bbb', 'bbba', 'bbbab', 'bbbb', 'bbbba', 'bbbbab'],
           ['', 'a', 'aa', 'aaa', 'b', 'ba', 'baaa', 'baaaa', 'baab', 'baba', 'bababb', 'babb', 'bb', 'bbaaa', 'bbaaba', 'bbabb', 'bbbabb'], 7),
]
# (\Sigma, P, N, k)
NEGATIVE_CDFA_INSTANCES = [
]
# (\Sigma, P, N, k)
NEGATIVE_RFA_INSTANCES = [
]
# (\Sigma, P, N, k, ell)
NEGATIVE_CARD_DFA_INSTANCES = [
    # L(A) = words whose 3rd last symbol (in the sense word[-3]) is b
    ('ab', ['abaa', 'baa', 'baaabba', 'baabbb', 'bab', 'babaa', 'babbab', 'babbb', 'bba', 'bbaa', 'bbab', 'bbabba', 'bbb', 'bbba', 'bbbab', 'bbbb', 'bbbba', 'bbbbab'],
           ['', 'a', 'aa', 'aaa', 'b', 'ba', 'baaa', 'baaaa', 'baab', 'baba', 'bababb', 'babb', 'bb', 'bbaaa', 'bbaaba', 'bbabb', 'bbbabb'], 8, 3),
]
# (\Sigma, P, N, k)
NEGATIVE_NFA_INSTANCES = [
    # L(A) = a^+ @ a^+ . a^+
    ('a@.', ['a@a.a', 'aa@a.a'],
            ['', '.', '..a', '.a', '@', '@.', '@.a', '@a', '@a.', '@a.a', '@aa', 'a', 'a.', 'a.a', 'a@',
            'a@.', 'a@.a', 'a@a', 'a@a.', 'a@aa', 'aa', 'aa.', 'aa.a', 'aaa'], 2),
]
