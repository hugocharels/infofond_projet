from utils import *
from tests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


vpool = IDPool(start_from=1)


# Les variables
P_ID = 0 # si l'état est présent dans l'automate
A_ID = 1 # si l'état est accpetant
T_ID = 2 # les transitions


def p(n: int) -> int:
    return vpool.id((P_ID, n))

def a(n: int) -> int:
    return vpool.id((A_ID, n))

def t(i: int, j: int, l: str) -> int:
    return vpool.id((T_ID, i, j, l))



# Les contraintes

def _at_least_one_state(k: int):
    """ Il y a au moins un état dans l'automate"""
    yield [p(n) for n in range(k)]

def _at_least_one_ac_state(k: int):
    """ Il y a au moins un état acceptant dans l'automate"""
    yield [a(n) for n in range(k)]

def _ac_state_is_present(k: int):
    """ Si un état est acceptant, il est présent dans l'automate"""
    for n in range(k): yield [-a(n), p(n)]




# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    # À COMPLÉTER
    return None

# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA:
    # À COMPLÉTER
    return None

# Q4
def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    # À COMPLÉTER
    return None

# Q5
def gen_autr(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    # À COMPLÉTER
    return None

# Q6
def gen_autcard(alphabet: str, pos: list[str], neg: list[str], k: int, ell: int) -> DFA:
    # À COMPLÉTER
    return None

# Q7
def gen_autn(alphabet: str, pos: list[str], neg: list[str], k: int) -> NFA:
    # À COMPLÉTER
    return None

def main():
    test_aut()
    test_minaut()
    test_autc()
    test_autr()
    test_autcard()
    test_autn()

if __name__ == '__main__':
    main()
