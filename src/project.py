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
V_ID = 3 # les états visiter lors de l'éxécution

# transformation de tseitin
Z_ID = 4


def p_id(n: int) -> int:
    """ Est vrai si l'état n est présent dans l'automate """
    return vpool.id((P_ID, n))

def a_id(n: int) -> int:
    """ Est vrai si l'état n est acceptant """
    return vpool.id((A_ID, n))

def t_id(i: int, j: int, l: str) -> int:
    """ Est vrai si la transition qui va de l'état i à j avec la lettre l existe """
    return vpool.id((T_ID, i, j, l))

def v_id(n: int, i: int, w: int) -> int:
    """ Est vrai si l'état n à été visité pour la ième lettre du mot w """
    return vpool.id((V_ID, n, i, w))

def z_id(i: int, j: int, l: str):
    return vpool.id((Z_ID, i, j, l))


#####################################################


#################### CONSTRAINTS ####################

def _source_state_is_in_aut(**args):
    """ La source est présente dans l'automate"""
    yield [p_id(0)]
    for l in args["alphabet"]: yield [t_id(0, n, l) for n in range(args["k"])]

def _at_least_one_ac_state(**args):
    """ Il y a au moins un état acceptant dans l'automate"""
    yield [a_id(n) for n in range(args["k"])]

def _ac_states_are_in_aut(**args):
    """ Tout les états acceptant sont dans l'automate"""
    for n in range(args["k"]): yield [-a_id(n), p_id(n)]

def _transitions_are_valid(**args):
    """ Toutes les transitions sont valides"""
    for i in range(args["k"]):
        for j in range(args["k"]):
            for l in args["alphabet"]:
                yield [-t_id(i,j,l), p_id(i)]
                yield [-t_id(i,j,l), p_id(j)]

def _aut_is_consistent(**args):
    """ L'automate est consistant."""
    # Toutes les exécutions commencent à la source
    for w in args["pos"] + args["neg"]:
        yield [v_id(0, 0, w)]

    # Toutes les exécutions finissent sur un état acceptant
    for w in args["pos"]:
        for n in range(args["k"]):
            yield [-v_id(n, len(w), w), a_id(n)]
    for w in args["neg"]:
        for n in range(args["k"]):
            yield [-v_id(n, len(w), w), -a_id(n)]

    # Un seul état peut être visité en même temps
    for w in args["pos"] + args["neg"]:
        for x in range(len(w)):
            for i in range(args["k"]):
                for j in range(args["k"]):
                    if i==j : continue
                    yield [-v_id(i, x, w), -v_id(j, x+1, w)]

    # Toutes les exécutions suivent les transitions
    for w in args["pos"] + args["neg"]:
        for x in range(len(w)-1):
            for i in range(args["k"]):
                for j in range(args["k"]):
                    yield [-v_id(i, x, w), -t_id(i, j, w[x]), v_id(j, x+1, w)]

def _aut_is_complete(**args):
    """ L'automate est complet. Pour chaque état il y a une transition pour chaque lettre de l'alphabet """
    for i in range(args["k"]):
        for l in args["alphabet"]:
            yield [-p_id(i)] + [z_id(i, j, l) for j in range(args["k"])]
            for j in range(args["k"]):
                yield [-z_id(i, j, l), p_id(j)]
                yield [-z_id(i, j, l), t_id(i, j, l)]
                yield [-p_id(j), -t_id(i, j, l), z_id(i, j, l)]
            yield [p_id(i)] + [-p_id(j) for j in range(args["k"])] + [-t_id(i,j,l) for j in range(args["k"])]

#####################################################


#################### MODEL -> DFA ####################

def _from_model_to_dfa(model: list[int], alphabet: str, k: int) -> DFA:
    """ Convertit un modèle SAT en un DFA"""
    return DFA(
        states=_get_states_from_model(model, k),
        input_symbols=set(alphabet),
        transitions=_get_transitions_from_model(model, alphabet, k),
        initial_state="q0",
        final_states=_get_final_states_from_model(model, k),
    )

def _get_states_from_model(model: list[int], k: int) -> set[int]:
    """ Retourne l'ensemble des états présents dans le modèle"""
    return {f"q{i}" for i in range(k) if p_id(i) in model}

def _get_final_states_from_model(model: list[int], k) -> set[int]:
    """ Retourne l'ensemble des états acceptants présents dans le modèle"""
    return {f"q{i}" for i in range(k) if a_id(i) in model}

def _get_transitions_from_model(model: list[int], alphabet: str, k: int) -> dict[tuple[int, str], int]:
    """ Retourne l'ensemble des transitions présentes dans le modèle"""
    transitions = {f"q{i}" : {} for i in range(k) if p_id(i) in model}
    for i in range(k):
        for j in range(k):
            for l in alphabet:
                if t_id(i, j, l) in model:
                    transitions[f"q{i}"][l] = f"q{j}"
    return transitions

######################################################

#################### UTILS ####################

def _gen_cnf(constraints: list[list[int]], alphabet: str, pos: list[str], neg: list[str], k: int) -> CNF:
    """ Génère une CNF à partir d'une liste de contraintes"""
    cnf = CNF()
    for c in constraints:
        for clause in c(alphabet=alphabet, pos=pos, neg=neg, k=k):
            #print(clause)
            cnf.append(clause)
    return cnf

def _solve(cnf: CNF) -> (bool, list[int]):
    """ Résoud une CNF"""
    solver = Minisat22(use_timer=True)
    #solver = Minicard(use_timer=True)
    solver.append_formula(cnf)
    return solver.solve(), solver.get_model()

def _print_model(model: list[int], alphabet: str, k: int) -> None:
    """ Affiche un modèle"""
    print(f"states={_get_states_from_model(model, k)}")
    print(f"final_states={_get_final_states_from_model(model, k)}")
    print(f"transitions={_get_transitions_from_model(model, alphabet, k)}")


###############################################

#################### QUESTIONS ####################

def _gen_aut(constraints : list, alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    """ Génère un automate à partir d'une liste de contraintes"""
    print("--------------------------")
    print(f"E={set(alphabet)}, P={pos}, N={neg}, k={k}")
    cnf = _gen_cnf(constraints, alphabet, pos, neg, k)
    result, model = _solve(cnf)
    if result:
        _print_model(model, alphabet, k)
        #show_automaton(_from_model_to_dfa(model, alphabet, k))
    return _from_model_to_dfa(model, alphabet, k) if result else None

# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    constraints = [
        _source_state_is_in_aut,
        _at_least_one_ac_state,
        _ac_states_are_in_aut,
        _transitions_are_valid,
        _aut_is_consistent,
        #_aut_is_complete,
    ]
    return _gen_aut(constraints, alphabet, pos, neg, k)

# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA:
    # TODO
    return None

# Q4
def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    constraints = [
        _source_state_is_in_aut,
        _at_least_one_ac_state,
        _ac_states_are_in_aut,
        _transitions_are_valid,
        _aut_is_consistent,
        _aut_is_complete,
    ]
    return _gen_aut(constraints, alphabet, pos, neg, k)

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
    gen_aut('a',  ['', 'aa', 'aaaaaa'], ['a', 'aaa', 'aaaaa'], 2)
    #gen_aut("ab", ["", "a", "aa", "aaa", "aaaa"], ["b", "ab", "ba", "bab", "aba"], 1)
    #gen_aut("ab", ["b", "ab", "ba", "abba", "abbb"], ["", "a", "aa", "aaa"], 2)
    #test_aut()
    #test_minaut()
    #test_autc()
    #test_autr()
    #test_autcard()
    #test_autn()

if __name__ == '__main__':
    main()
