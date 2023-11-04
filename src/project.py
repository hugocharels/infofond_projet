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
X_ID = 4


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

def x_id(i: int, j: int, x: int, w: str):
    """  """
    return vpool.id((X_ID, i, j, x, w))

def reverse(v: int) -> tuple:
    """ Retourne la variable sous forme de tuple """
    tup = vpool.obj(v) if vpool.obj(v) is not None else vpool.obj(-v)
    ret = "" if v > 0 else "-"
    if tup[0] == P_ID: ret += f"p[{tup[1]}]"
    elif tup[0] == A_ID: ret += f"a[{tup[1]}]"
    elif tup[0] == T_ID: ret += f"t[{tup[1]},{tup[2]},{tup[3]}]"
    elif tup[0] == V_ID: ret += f"v[{tup[1]},{tup[2]},{tup[3]}]"
    elif tup[0] == X_ID: ret += f"x[{tup[1]},{tup[2]},{tup[3]},{tup[4]}]"
    return ret


#####################################################


#################### CONSTRAINTS ####################

def _construction(**args):
    """ L'automate est construit de manière correcte. """
    #print("-----------------------------------------")
    #print("----------------- BUILD -----------------")
    # La source est présente dans l'automate
    yield [p_id(0)]

    # Il y a au moins un état acceptant dans l'automate
    yield [a_id(n) for n in range(args["k"])]

    # Tout les états acceptant sont dans l'automate
    for n in range(args["k"]): yield [-a_id(n), p_id(n)]

    # Les transitions sont valides
    for i in range(args["k"]):
        for j in range(args["k"]):
            for l in args["alphabet"]:
                yield [-t_id(i,j,l), p_id(i)]
                if i == j: continue
                yield [-t_id(i,j,l), p_id(j)]

def _aut_is_consistent(**args):
    """ L'automate est consistant."""

    #print("-----------------------------------------")
    #print("--------------- CONSISTANT ---------------")
    
    #print("------- SOURCE -------")
    # Toutes les exécutions commencent à la source
    for w in args["pos"] + args["neg"]:
        yield [v_id(0, 0, w)]
        #if len(w) == 0: yield [v_id(0, 0, w)]
        #else: yield [-t_id(0, n, w[0]) for n in range(args["k"])] + [v_id(n, 0, w) for n in range(args["k"])]

    #print("----- ACCEPTANTES ------")
    # Toutes les exécutions des mots de P sont acceptantes
    for w in args["pos"]:
        for n in range(args["k"]):
            yield [-v_id(n, len(w), w), a_id(n)]
            #yield [-a_id(n), v_id(n, len(w), w)]

    #print("--- NON ACCEPTANTES ----")
    # Toutes les exécutions des mots de N sont non acceptantes
    for w in args["neg"]:
        for n in range(args["k"]):
            yield [-v_id(n, len(w), w), -a_id(n)]
            #yield [a_id(n), v_id(n, len(w), w)]

    #print("------ VISITES -------")
    # Un seul état peut être visité en même temps
    for w in args["pos"] + args["neg"]:
        for x in range(len(w)+1):
            for i in range(args["k"]):
                for j in range(args["k"]):
                    if i >= j: continue
                    yield [-v_id(i, x, w), -v_id(j, x, w)]
    
    #print("------ EXISTENCE -------")
    # Chaque mot doit avoir une exécution
    for w in args["pos"] + args["neg"]:
        for x in range(1, len(w)+1):
            yield [v_id(i, x, w) for i in range(args["k"])]
    
    #print("------ TRANSITIONS -------")
    # Toutes les exécutions suivent les transitions
    for w in args["pos"] + args["neg"]:
        for x in range(len(w)):
            for i in range(args["k"]):
                #yield [-v_id(i, x, w)] + [x_id(i, j, x, w) for j in range(args["k"])]
                for j in range(args["k"]):
                    #yield [-x_id(i, j, x, w), v_id(j, x+1, w)]
                    #yield [-x_id(i, j, x, w), t_id(i, j, w[x])]
                    #yield [-v_id(j, x+1, w), -t_id(i, j, w[x]), x_id(i, j, x, w)]
                    yield [-v_id(i, x, w), -t_id(i, j, w[x]), v_id(j, x+1, w)]
                    yield [-v_id(i, x, w), -v_id(j, x+1, w), t_id(i,j,w[x])]

def _aut_is_complete(**args):
    """ L'automate est complet. """

    #print("-----------------------------------------")
    #print("--------------- COMPLETE ---------------")
    
    #print("----- 2 SORTANTES ------")
    # Pour chaque état il y a une transition sortante pour chaque lettre de l'alphabet
    for i in range(args["k"]):
        for l in args["alphabet"]:
            yield [t_id(i, j, l) for j in range(args["k"])]

    #print("----- 1 ENTRANTE ------")
    # Pour chaque état il y a une transition entrante pour au moins une lettre de l'alphabet
    for i in range(args["k"]):
        yield [t_id(j, i, l) for j in range(args["k"]) for l in args["alphabet"]]


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

def _gen_cnf(constraints: list, alphabet: str, pos: list[str], neg: list[str], k: int) -> CNF:
    """ Génère une CNF à partir d'une liste de contraintes"""
    cnf = CNF()
    for constraint in constraints:
        for clause in constraint(alphabet=alphabet, pos=pos, neg=neg, k=k):
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


###############################################

#################### QUESTIONS ####################

def _gen_aut(constraints : list, alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    """ Génère un automate à partir d'une liste de contraintes"""
    #print("-----------------------------------------")
    #print(f"E={set(alphabet)}, P={pos}, N={neg}, k={k}")
    cnf = _gen_cnf(constraints, alphabet, pos, neg, k)
    result, model = _solve(cnf)
    if result:
        pass
        #_print_model(model, alphabet, k)
        #show_automaton(_from_model_to_dfa(model, alphabet, k))
    return _from_model_to_dfa(model, alphabet, k) if result else None

# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    constraints = [
        _construction,
        _aut_is_consistent,
        #_aut_is_complete,
    ]
    return _gen_aut(constraints, alphabet, pos, neg, k)

# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA:
    constraints = [
        _construction,
        _aut_is_consistent,
        #_aut_is_complete,
    ]

    k = 0
    aut = None
    while aut is None:
        k += 1
        aut = _gen_aut(constraints, alphabet, pos, neg, k)
    return aut

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
    #gen_aut('a',  ['', 'aa', 'aaaaaa'], ['a', 'aaa', 'aaaaa'], 2)
    #gen_aut("ab", ["", "a", "aa", "aaa", "aaaa"], ["b", "ab", "ba", "bab", "aba"], 1)
    #gen_aut("ab", ["b", "ab", "ba", "abba", "abbb"], ["", "a", "aa", "aaa"], 2)
    test_aut()
    #test_minaut()
    #gen_autc('ab', ['', 'aa', 'aaaa', 'a', 'abb', 'bb', 'abba', 'bbbb', 'bbba', 'abbb'], ['b', 'aba', 'ba', 'ab', 'abbab', 'bbabbab', 'babba'], 4)
    #test_autc()
    #test_autr()
    #test_autcard()
    #test_autn()

if __name__ == '__main__':
    main()
