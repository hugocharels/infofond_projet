from utils import *
from tests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool



#################### VARIABLES ####################

vpool = IDPool(start_from=1)

P_ID = 0 # si l'état est présent dans l'automate
A_ID = 1 # si l'état est accpetant
T_ID = 2 # les transitions

def p(n: int) -> int:
    return vpool.id((P_ID, n))

def a(n: int) -> int:
    return vpool.id((A_ID, n))

def t(i: int, j: int, l: str) -> int:
    return vpool.id((T_ID, i, j, l))

#####################################################


#################### CONSTRAINTS ####################

def _source_state_is_in_aut(**args):
    """ La source est présente dans l'automate"""
    yield [p(0)]

def _at_least_one_ac_state(**args):
    """ Il y a au moins un état acceptant dans l'automate"""
    yield [a(n) for n in range(args['k'])]

def _ac_states_are_in_aut(**args):
    """ Tout les états acceptant sont dans l'automate"""
    for n in range(args['k']): yield [-a(n), p(n)]

def _aut_is_complete(**args):
    """ L'automate est complet. Pour chaque état il y a une transition pour chaque lettre de l'alphabet """
    for i in range(args['k']):
        for l in args["alphabet"]:
            clause = [-p(i)]
            for j in range(args['k']):
                clause.append(t(i, j, l))
            yield clause

def _transitions_are_valid(**args):
    """ Si il existe une transition alors les états sont dans l'automates"""
    for i in range(args['k']):
        for j in range(args['k']):
            clause = []
            for l in args["alphabet"]:
                clause.append(-t(i, j, l))
            yield [p(i)] + clause
            yield [p(j)] + clause


# TODO


#####################################################


#################### MODEL -> DFA ####################

def _from_model_to_dfa(model: list[int], alphabet: str, k: int) -> DFA:
    """ Convertit un modèle SAT en un DFA"""
    return DFA(
        states=_get_states_from_model(model),
        input_symbols=set(alphabet),
        transitions=_get_transitions_from_model(model, alphabet, k),
        initial_state="q0",
        final_states=_get_final_states_from_model(model),
    )


def _get_states_from_model(model: list[int]) -> set[int]:
    """ Retourne l'ensemble des états présents dans le modèle"""
    ret = set()
    for var in model:
        if vpool.obj(var) is None: continue
        if vpool.obj(var)[0] == P_ID:
            ret.add(f"q{vpool.obj(var)[1]}")
    return ret

def _get_final_states_from_model(model: list[int]) -> set[int]:
    """ Retourne l'ensemble des états acceptants présents dans le modèle"""
    ret = set()
    for var in model:
        if vpool.obj(var) is None: continue
        if vpool.obj(var)[0] == A_ID:
            ret.add(f"q{vpool.obj(var)[1]}")
    return ret

def _get_transitions_from_model(model: list[int], alphabet: str, k: int) -> dict[tuple[int, str], int]:
    """ Retourne l'ensemble des transitions présentes dans le modèle"""
    transitions = {f"q{i}" : {} for i in range(k) if p(i) in model}
    for var in model:
        if vpool.obj(var) is None: continue
        if vpool.obj(var)[0] == T_ID:
            _, i, j, l = vpool.obj(var)
            transitions[f"q{i}"][l] = f"q{j}"
    return transitions


######################################################




#################### UTILS ####################


def _gen_cnf(constraints: list[list[int]], alphabet: str, pos: list[str], neg: list[str], k: int) -> CNF:
    """ Génère une CNF à partir d'une liste de contraintes"""
    cnf = CNF()
    for c in constraints:
        for clause in c(alphabet=alphabet, pos=pos, neg=neg, k=k):
            cnf.append(clause)
    return cnf


def _solve(cnf: CNF) -> (bool, list[int]):
    """ Résoud une CNF"""
    solver = Minisat22(use_timer=True)
    solver.append_formula(cnf, no_return=False)
    return solver.solve(), solver.get_model()



def _print_model(model: list[int]) -> None:
    """ Affiche un modèle"""
    for var in model:
        if vpool.obj(var) is None: continue
        if vpool.obj(var)[0] == P_ID:
            print(f"q{vpool.obj(var)[1]} est présent")
        if vpool.obj(var)[0] == A_ID:
            print(f"q{vpool.obj(var)[1]} est acceptant")
        if vpool.obj(var)[0] == T_ID:
            _, i, j, l = vpool.obj(var)
            print(f"q{i} --{l}--> q{j}")







#################### QUESTIONS ####################

# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    print("--------------------------")
    print(f"E={alphabet}, P={pos}, N={neg}, k={k}")
    constraints = [
        _source_state_is_in_aut,
        _at_least_one_ac_state,
        _ac_states_are_in_aut,
        _aut_is_complete,
        _transitions_are_valid,
        # TODO
    ]
    cnf = _gen_cnf(constraints, alphabet, pos, neg, k)
    result, model = _solve(cnf)
    print(f"Résultat : {result}")
    if result: _print_model(model)
    return _from_model_to_dfa(model, alphabet, k) if result else None


# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA:
    # TODO
    return None

# Q4
def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    # TODO
    return None

# Q5
def gen_autr(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    # TODO
    return None

# Q6
def gen_autcard(alphabet: str, pos: list[str], neg: list[str], k: int, ell: int) -> DFA:
    # TODO
    return None

# Q7
def gen_autn(alphabet: str, pos: list[str], neg: list[str], k: int) -> NFA:
    # TODO
    return None

######################################################


def main():
    test_aut()
    #test_minaut()
    #test_autc()
    #test_autr()
    #test_autcard()
    #test_autn()

if __name__ == '__main__':
    main()
