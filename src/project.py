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

# Est vrai si l'état n est présent dans l'automate
p_id = lambda n: vpool.id((P_ID, n))

# Est vrai si l'état n est acceptant
a_id = lambda n: vpool.id((A_ID, n))

# Est vrai si la transition qui va de l'état i à j avec la lettre l existe
t_id = lambda i, j, l: vpool.id((T_ID, i, j, l))

# Est vrai si l'état n à été visité pour la ième lettre du mot w
v_id = lambda n, i, w: vpool.id((V_ID, n, i, w))


def reverse(v: int) -> tuple:
    """ Retourne la variable sous forme de tuple """
    tup = vpool.obj(v) if vpool.obj(v) is not None else vpool.obj(-v)
    ret = "" if v > 0 else "-"
    if tup[0] == P_ID: ret += f"p[{tup[1]}]"
    elif tup[0] == A_ID: ret += f"a[{tup[1]}]"
    elif tup[0] == T_ID: ret += f"t[{tup[1]},{tup[2]},{tup[3]}]"
    elif tup[0] == V_ID: ret += f"v[{tup[1]},{tup[2]},{tup[3]}]"
    #elif tup[0] == X_ID: ret += f"x[{tup[1]},{tup[2]},{tup[3]},{tup[4]}]"
    return ret

#####################################################


#################### CONSTRAINTS ####################

def __source_in_aut(**args):
    """ La source est présente dans l'automate """
    yield [p_id(0)]

def __min_one_accepting_state(**args):
    """ Il y a au moins un état acceptant dans l'automate """
    yield [a_id(n) for n in range(args["k"])]

def __states_are_in_aut(**args):
    """ Tous les états acceptant sont dans l'automate """
    for n in range(args["k"]): yield [-a_id(n), p_id(n)]

def __transitions_are_valids(**args):
    """ Toutes les transitions sont valides """
    for i in range(args["k"]):
        for j in range(args["k"]):
            for l in args["alphabet"]:
                yield [-t_id(i,j,l), p_id(i)]
                if i == j: continue
                yield [-t_id(i,j,l), p_id(j)]

def _construction(**args):
    """ L'automate est construit de manière correcte. """
    constraints = [
        __source_in_aut,
        #__min_one_accepting_state,
        __states_are_in_aut,
        __transitions_are_valids,
    ]
    for constraint in constraints:
        for clause in constraint(**args):
            yield clause


def __all_exec_start_at_q0(**args):
    """ Toutes les exécutions commencent à la source """
    for w in args["pos"] + args["neg"]:
        yield [v_id(0, 0, w)]

def __all_pos_exec_are_ac(**args):
    """ Toutes les exécutions des mots de P sont acceptantes """
    for w in args["pos"]:
        for n in range(args["k"]):
            yield [-v_id(n, len(w), w), a_id(n)]

def __all_neg_exec_are_not_ac(**args):
    """ Toutes les exécutions des mots de N sont non acceptantes """
    for w in args["neg"]:
        for n in range(args["k"]):
            yield [-v_id(n, len(w), w), -a_id(n)]

def __only_one_visit_at_a_time(**args):
    """ Un seul état peut être visité à la fois """
    for w in args["pos"] + args["neg"]:
        for x in range(len(w)+1):
            for i in range(args["k"]):
                for j in range(args["k"]):
                    if i >= j: continue
                    yield [-v_id(i, x, w), -v_id(j, x, w)]

def __all_pos_exec_exists(**args):
    """ Il existe une exécution pour chaque mot de P """
    for w in args["pos"]:
        for x in range(1, len(w)+1):
            yield [v_id(i, x, w) for i in range(args["k"])]

def __all_exec_follow_transitions(**args):
    """ Toutes les exécutions suivent les transitions """
    for w in args["pos"] + args["neg"]:
        for x in range(len(w)):
            for i in range(args["k"]):
                for j in range(args["k"]):
                    yield [-v_id(i, x, w), -t_id(i, j, w[x]), v_id(j, x+1, w)]
                    yield [-v_id(i, x, w), -v_id(j, x+1, w), t_id(i,j,w[x])]

def _aut_is_consistent(**args):
    """ L'automate est consistant."""
    constraints = [
        __all_exec_start_at_q0,
        __all_pos_exec_are_ac,
        __all_neg_exec_are_not_ac,
        __only_one_visit_at_a_time,
        __all_pos_exec_exists,
        __all_exec_follow_transitions,
    ]
    for constraint in constraints:
        for clause in constraint(**args):
            yield clause


def __all_neg_exec_exists(**args):
    """ Il existe une exécution pour chaque mot de P """
    for w in args["neg"]:
        yield [v_id(i, len(w), w) for i in range(args["k"])]

def __all_states_has_outgoing_transitions(**args):
    """ Pour chaque état il y a une transition sortante pour chaque lettre de l'alphabet """
    for i in range(args["k"]):
        for l in args["alphabet"]:
            yield [t_id(i, j, l) for j in range(args["k"])]

def __all_states_has_incoming_transitions(**args):
    """ Pour chaque état il y a une transition entrante pour au moins une lettre de l'alphabet """
    for i in range(args["k"]):
        yield [t_id(j, i, l) for j in range(args["k"]) for l in args["alphabet"]]

def _aut_is_complete(**args):
    """ L'automate est complet. """
    constraints = [
        __all_neg_exec_exists,
        __all_states_has_outgoing_transitions,
        __all_states_has_incoming_transitions,
    ]
    for constraint in constraints:
        for clause in constraint(**args):
            yield clause


def __all_exec_follow_reverse_transitions(**args):
    """ Toutes les exécutions suivent les transitions """
    for w in args["pos"] + args["neg"]:
        for x in range(len(w)):
            for i in range(args["k"]):
                for j in range(args["k"]):
                    yield [-v_id(i, x, w), -t_id(j, i, w[x]), v_id(j, x+1, w)]
                    yield [-v_id(i, x, w), -v_id(j, x+1, w), t_id(j, i, w[x])]

def _aut_is_reverse(**args):
    """ L'automate est réversible. """
    constraints = [
        __all_exec_follow_reverse_transitions,
    ]
    for constraint in constraints:
        for clause in constraint(**args):
            yield clause

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
        allow_partial=True
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

verbose = lambda **args: "verbose" in args and args["verbose"]
cnfplus = lambda **args: "cnfplus" in args and args["cnfplus"]

def _gen_cnf(constraints: list, alphabet: str, pos: list[str], neg: list[str], k: int, **args) -> CNF:
    """ Génère une CNF à partir d'une liste de contraintes"""
    cnf = CNF()
    for constraint in constraints:
        for clause in constraint(alphabet=alphabet, pos=pos, neg=neg, k=k, **args):
            #print([reverse(prop) for prop in clause])
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

def _gen_aut(constraints : list, alphabet: str, pos: list[str], neg: list[str], k: int, **args) -> DFA:
    """ Génère un automate à partir d'une liste de contraintes"""
    if verbose(**args): print(f"-----------------------------------------\nE={set(alphabet)}, P={pos}, N={neg}, k={k}")
    if cnfplus(**args): cnf = __gen_cnfplus(constraints, alphabet, pos, neg, k, **args)
    else: cnf = cnf = _gen_cnf(constraints, alphabet, pos, neg, k, **args)
    result, model = _solve(cnf)
    if result and verbose(**args): _print_model(model, alphabet, k)
    #show_automaton(_from_model_to_dfa(model, alphabet, k))
    return _from_model_to_dfa(model, alphabet, k) if result else None

###############################################

#################### QUESTIONS ####################

# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    constraints = [
        _construction,
        _aut_is_consistent,
    ]
    return _gen_aut(constraints, alphabet, pos, neg, k)

# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str], k: int=1) -> DFA:
    aut = gen_aut(alphabet, pos, neg, k)
    return aut if aut is not None else gen_minaut(alphabet, pos, neg, k+1)

# Q4
def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    constraints = [
        _construction,
        _aut_is_consistent,
        _aut_is_complete,
    ]
    return _gen_aut(constraints, alphabet, pos, neg, k)

# Q5
def gen_autr(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    constraints = [
        _construction,
        _aut_is_consistent,
        _aut_is_reverse,
    ]
    return _gen_aut(constraints, alphabet, pos, neg, k)

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
    test_minaut()
    test_autc()
    test_autr()
    #test_autcard()
    #test_autn()

if __name__ == '__main__':
    main()
