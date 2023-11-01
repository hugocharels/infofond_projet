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
Y_ID = 5
Z_ID = 6


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

def x_id(i: int, j: int, x: int, z: int, l: str):
    """ hum """
    return vpool.id((X_ID, i, j, x, z, l))

def y_id(s: int, L: int, z: int):
    """ hum """
    return vpool.id((Y_ID, s, L, z))

def z_id(i: int, j: int, l: str):
    return vpool.id((Z_ID, i, j, l))


#####################################################


#################### CONSTRAINTS ####################

def _source_state_is_in_aut(**args):
    """ La source est présente dans l'automate"""
    yield [p_id(0)]

def _at_least_one_ac_state(**args):
    """ Il y a au moins un état acceptant dans l'automate"""
    yield [a_id(n) for n in range(args['k'])]

def _ac_states_are_in_aut(**args):
    """ Tout les états acceptant sont dans l'automate"""
    for n in range(args['k']): yield [-a_id(n), p_id(n)]

def _if_empty_word(**args):
    yield [a_id(0)] if '' in args["pos"] else []
    yield [-a_id(0)] if '' in args["neg"] else []


def _each_sate_is_reachable(**args):
    yield [t_id(0, j, l) for j in range (1, args['k']) for l in args["alphabet"]]
        

def _aut_is_complete(**args):
    """ L'automate est complet. Pour chaque état il y a une transition pour chaque lettre de l'alphabet """
    for i in range(args['k']):
        for l in args["alphabet"]:
            yield [-p_id(i)] + [z_id(i, j, l) for j in range(args['k'])]
            for j in range(args['k']):
                yield [-z_id(i, j, l), p_id(j)]
                yield [-z_id(i, j, l), t_id(i, j, l)]
                yield [-p_id(j), -t_id(i, j, l), z_id(i, j, l)]
            
            yield [p_id(i)] + [-p_id(j) for j in range(args['k']) if j != i] + [-t_id(i,j,l) for j in range(args['k']) if j != i]

def _ex_are_ac(**args):
    """ Toutes les exécutions des mots de pos sont acceptante """
    for z, w in enumerate(args["pos"]):
        for x in range(len(w)-1):

            for i in range(args['k']):
                yield [x_id(i, j, x, z, w[x]) for j in range(args['k'])]

        yield [y_id(s, len(w), z) for s in range(args['k'])]

        for x in range(len(w)-1):

            for i in range(args['k']):
                for j in range(args['k']):
                    yield [-x_id(i, j, x, z, w[x]), v_id(i, x, z)]
                    yield [-x_id(i, j, x, z, w[x]), v_id(j, x+1, z)]
                    yield [-x_id(i, j, x, z, w[x]), t_id(i, j, w[x])]
                    yield [-v_id(i, x, z), -v_id(j, x+1, z), -t_id(i, j, w[x]), x_id(i, j, x, z, w[x])]

        for s in range(args['k']):
            yield [-y_id(s, len(w), z), v_id(s, len(w), z)]
            yield [-y_id(s, len(w), z), a_id(s)]
            yield [-v_id(s, len(w), z), -a_id(s), y_id(s, len(w), z)]

def _ex_are_not_ac(**args):
    """ Toutes les exécutions des mots de neg sont non acceptante """
    for z, w in enumerate(args["neg"]):
        for x in range(len(w)-1):

            for i in range(args['k']):
                yield [x_id(i, j, x, z, w[x]) for j in range(args['k'])]

        yield [y_id(s, len(w), z) for s in range(args['k'])]

        for x in range(len(w)-1):

            for i in range(args['k']):
                for j in range(args['k']):
                    yield [-x_id(i, j, x, z, w[x]), v_id(i, x, z)]
                    yield [-x_id(i, j, x, z, w[x]), v_id(j, x+1, z)]
                    yield [-x_id(i, j, x, z, w[x]), t_id(i, j, w[x])]
                    yield [-v_id(i, x, z), -v_id(j, x+1, z), -t_id(i, j, w[x]), x_id(i, j, x, z, w[x])]

        for s in range(args['k']):
            yield [-y_id(s, len(w), z), v_id(s, len(w), z)]
            yield [-y_id(s, len(w), z), -a_id(s)]
            yield [-v_id(s, len(w), z), a_id(s), y_id(s, len(w), z)]


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
        #print(var, vpool.obj(abs(var)))
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
    transitions = {f"q{i}" : {} for i in range(k) if p_id(i) in model}
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
            #print(clause)
            cnf.append(clause)
    return cnf

def _solve(cnf: CNF) -> (bool, list[int]):
    """ Résoud une CNF"""
    solver = Minisat22(use_timer=True)
    solver.append_formula(cnf, no_return=False)
    return solver.solve(), solver.get_model()

def _print_model(model: list[int]) -> None:
    """ Affiche un modèle"""
    print("--> q0")
    for var in model:
        if vpool.obj(var) is None: continue
        if vpool.obj(var)[0] == P_ID:
            print(f"q{vpool.obj(var)[1]} est présent")
        if vpool.obj(var)[0] == A_ID:
            print(f"q{vpool.obj(var)[1]} est acceptant")
        if vpool.obj(var)[0] == T_ID:
            _, i, j, l = vpool.obj(var)
            print(f"q{i} --{l}--> q{j}")

###############################################

#################### QUESTIONS ####################

# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    print("--------------------------")
    print(f"E={set(alphabet)}, P={set(pos)}, N={set(neg)}, k={k}")
    constraints = [
        _source_state_is_in_aut,
        _at_least_one_ac_state,
        _ac_states_are_in_aut,
        _if_empty_word,
        _each_sate_is_reachable,
        _aut_is_complete,
        _ex_are_ac,
        _ex_are_not_ac,
    ]
    cnf = _gen_cnf(constraints, alphabet, pos, neg, k)
    #print(cnf.clauses)
    result, model = _solve(cnf)
    #print(result)
    if result:
        _print_model(model)
        show_automaton(_from_model_to_dfa(model, alphabet, k))
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
    
    gen_aut('a',  ['', 'aa', 'aaaaaa'], ['a', 'aaa', 'aaaaa'], 2)

    #test_aut()
    #test_minaut()
    #test_autc()
    #test_autr()
    #test_autcard()
    #test_autn()

if __name__ == '__main__':
    main()
