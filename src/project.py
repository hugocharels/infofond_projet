from utils import *
from tests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool


################### VARIABLES ####################


class ID:
    P = 0  # les états présents
    A = 1  # les états acceptants
    T = 2  # les transitions
    V = 3  # les états visiter lors de l'exécution

    # Pour transformation de Tseitin
    X = 4
    Y = 5

    vpool = IDPool(start_from=1)

    def __init__(self, id: int):
        self.id = id

    @staticmethod
    def p(x: int):
        """Si l'état 'x' est présent dans l'automate"""
        return ID.vpool.id((ID.P, x))

    @staticmethod
    def a(x: int):
        """Si l'état 'x' est accpetant"""
        return ID.vpool.id((ID.A, x))

    @staticmethod
    def t(x: int, y: int, l: str):
        """Si il y a une transitions de l'état 'x' à 'y' avec la lettre 'l'"""
        return ID.vpool.id((ID.T, x, y, l))

    @staticmethod
    def v(x: int, i: int, w: str):
        """Si l'état 'x' est visité à la 'i' lettre du mot 'w'"""
        return ID.vpool.id((ID.V, x, i, w))

    @staticmethod
    def x(x, s, w):
        return ID.vpool.id((ID.X, x, s, w))

    @staticmethod
    def y(x, y, i, w):
        return ID.vpool.id((ID.Y, x, y, i, w))


##################################################

################### GENERATORS ###################


class AutGenerator:
    def __init__(self, alphabet: str, pos: list[str], neg: list[str], k: int):
        self.alphabet = alphabet
        self.pos = pos
        self.neg = neg
        self.k = k

    ########## CONSTRAINTS ##########

    def _coherence(self):
        """
        Représente les contraintes de cohérence de l'automate.
        C'est à dire qu'il soit correctement contruit.
        """

        # La source est dans l'automate
        yield [ID.p(0)]

        # Tous les états acceptants sont dans l'automate
        for x in range(self.k):
            yield [-ID.a(x), ID.p(x)]

        # Toutes les transitions sont valides
        for x in range(self.k):
            for y in range(self.k):
                for l in self.alphabet:
                    if x != 0:
                        yield [-ID.t(x, y, l), ID.p(x)]
                    if x != y:
                        yield [-ID.t(x, y, l), ID.p(y)]

    def _consistence(self):
        """
        Représente la consistence de l'automate.
        C'est à dire qu'il accepte tous les mots de pos et rejette tous les mots de neg.
        """

        # Toutes les exécutions commencent uniquement à la source
        for w in self.pos + self.neg:
            yield [ID.v(0, 0, w)]
            for x in range(1, self.k):
                yield [-ID.v(x, 0, w)]

        # Il existe une exécution acceptante pour tous les mots de pos
        for w in self.pos:
            yield [ID.x(x, len(w), w) for x in range(self.k)]
            for x in range(self.k):
                # yield [-ID.v(x, len(w), w), ID.a(x)]
                yield [-ID.x(x, len(w), w), ID.v(x, len(w), w)]
                yield [-ID.x(x, len(w), w), ID.a(x)]
                yield [-ID.v(x, len(w), w), -ID.a(x), ID.x(x, len(w), w)]

        # Il n'existe pas d'exécution acceptante pour tous les mots de neg
        for w in self.neg:
            for x in range(self.k):
                yield [-ID.v(x, len(w), w), -ID.a(x)]

        # Les exécutions sont valides
        for w in self.pos + self.neg:
            for i in range(len(w)):
                for x in range(self.k):
                    for y in range(self.k):
                        if i == 0 and x != 0:
                            continue
                        yield [-ID.v(x, i, w), -ID.t(x, y, w[i]), ID.v(y, i + 1, w)]
                        # yield [-ID.v(x, i, w), -ID.v(y, i+1, w), ID.t(x, y, w[i])]

        for w in self.pos + self.neg:
            for i in range(len(w)):
                for x in range(self.k):
                    yield [-ID.v(x, i + 1, w)] + [ID.y(x, y, i, w) for y in range(self.k)]
                    for y in range(self.k):
                        yield [-ID.y(x, y, i, w), ID.t(y, x, w[i])]
                        yield [-ID.y(x, y, i, w), ID.v(y, i, w)]
                        yield [-ID.t(y, x, w[i]), -ID.v(y, i, w), ID.y(x, y, i, w)]

    #################################

    def _get_constraints(self) -> list:
        return [
            self._coherence,
            self._consistence,
        ]

    def _get_clauses(self):
        for constraint in self._get_constraints():
            for clause in constraint():
                yield clause

    def _generate(self, *args) -> CNF:
        cnf = CNF() if "cnfplus" not in args else CNFPlus()
        for clause in self._get_clauses():
            cnf.append(clause)
        return cnf

    def _solve(self, cnf: CNF) -> tuple[bool, list[int]]:
        solver = Minisat22() if not isinstance(cnf, CNFPlus) else Minicard()
        solver.append_formula(cnf)
        return solver.solve(), solver.get_model()

    def generate(self, *args) -> list[int]:
        cnf = self._generate(*args)
        sat, model = self._solve(cnf)
        if sat and "verbose" in args:
            pass
        return sat, model


class DetAutGenerator(AutGenerator):
    def __init__(self, alphabet: str, pos: list[str], neg: list[str], k: int):
        super().__init__(alphabet, pos, neg, k)

    def _determinism(self):
        """
        Représente le déterminisme de l'automate.
        C'est à dire qu'il n'y a pas de deux transitions sortant d'un même état avec la même lettre.
        """
        for x in range(self.k):
            for l in self.alphabet:
                for y in range(self.k):
                    for z in range(self.k):
                        if y != z:
                            yield [-ID.t(x, y, l), -ID.t(x, z, l)]

    def _get_constraints(self) -> list:
        return super()._get_constraints() + [
            self._determinism,
        ]


class MinAutGenerator(DetAutGenerator):
    def __init__(self, alphabet: str, pos: list[str], neg: list[str]):
        super().__init__(alphabet, pos, neg, 1)

    def generate(self, *args) -> list[int]:
        self.k += 1
        sat, model = super().generate(*args)
        return (sat, model, self.k) if sat else self.generate(*args)


class CompAutGenerator(DetAutGenerator):
    def __init__(self, alphabet: str, pos: list[str], neg: list[str], k: int):
        super().__init__(alphabet, pos, neg, k)

    def _completeness(self):
        """
        Représente la complétude de l'automate.
        C'est à dire qu'il y a une transition sortant de chaque état avec chaque lettre.
        """

        # Pour chaque état il y a une transition sortant avec chaque lettre
        for x in range(self.k):
            for l in self.alphabet:
                yield [ID.t(x, y, l) for y in range(self.k)]

    def _get_constraints(self) -> list:
        return super()._get_constraints() + [
            self._completeness,
        ]


class RevAutGenerator(DetAutGenerator):
    def __init__(self, alphabet: str, pos: list[str], neg: list[str], k: int):
        super().__init__(alphabet, pos, neg, k)

    def _reversibility(self):
        """
        Représente la réversibilité de l'automate.
        C'est à dire que l'automate accepte et rejete les même mot en inversant les transitions.
        """
        for w in self.pos + self.neg:
            for i in range(len(w)):
                for x in range(self.k):
                    for y in range(self.k):
                        if i == 0 and x != 0:
                            continue
                        yield [-ID.v(y, i, w), -ID.t(y, x, w[i]), ID.v(x, i + 1, w)]
                        yield [-ID.v(y, i, w), -ID.v(x, i + 1, w), ID.t(y, x, w[i])]

    def _get_constraints(self) -> list:
        return super()._get_constraints() + [
            self._reversibility,
        ]


class CardAutGenerator(DetAutGenerator):
    def __init__(self, alphabet: str, pos: list[str], neg: list[str], k: int, ell: int):
        super().__init__(alphabet, pos, neg, k)
        self.ell = ell

    def _generate(self, *args) -> CNF:
        cnf = super()._generate("cnfplus", *args)
        cnf.append([[ID.a(x) for x in range(self.k)], self.ell], is_atmost=True)
        return cnf


##################################################

#################### BUILDER #####################


class AutBuilder:
    def __init__(self, alphabet: str, pos: list[str], neg: list[str], k: int):
        self.alphabet = alphabet
        self.pos = pos
        self.neg = neg
        self.k = k

    def _get_states(self, model: list[int]) -> list[int]:
        return {f"q{x}" for x in range(self.k) if ID.p(x) in model}

    def _get_final_states(self, model: list[int]) -> list[int]:
        return {f"q{x}" for x in range(self.k) if ID.a(x) in model}

    def _get_d_transitions(self, model: list[int]) -> dict[int, dict[str, int]]:
        transitions = {f"q{x}": dict() for x in range(self.k) if ID.p(x) in model}
        for x in range(self.k):
            for y in range(self.k):
                for l in self.alphabet:
                    if ID.t(x, y, l) in model:
                        transitions[f"q{x}"][l] = f"q{y}"
        return transitions

    def _get_nd_transitions(self, model: list[int]) -> dict[int, dict[str, list[int]]]:
        transitions = {f"q{x}": dict() for x in range(self.k) if ID.p(x) in model}
        for x in range(self.k):
            for y in range(self.k):
                for l in self.alphabet:
                    if ID.t(x, y, l) in model:
                        if l not in transitions[f"q{x}"]:
                            transitions[f"q{x}"][l] = {f"q{y}"}
                        else:
                            transitions[f"q{x}"][l].add(f"q{y}")
        return transitions

    def _get_transitions(self, model: list[int], *args):
        return self._get_nd_transitions(model) if "nfa" else self._get_d_transitions(model)

    def build(self, model: list[int], *args) -> FA:
        return (
            DFA(
                states=self._get_states(model),
                input_symbols=set(self.alphabet),
                transitions=self._get_transitions(model, *args),
                initial_state="q0",
                final_states=self._get_final_states(model),
                allow_partial=True,
            )
            if FA == "DFA"
            else NFA(
                states=self._get_states(model),
                input_symbols=set(self.alphabet),
                transitions=self._get_transitions(model, *args),
                initial_state="q0",
                final_states=self._get_final_states(model),
            )
        )


##################################################

################### QUESTIONS ####################


# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    sat, result = DetAutGenerator(alphabet, pos, neg, k).generate()
    return AutBuilder(alphabet, pos, neg, k).build(result) if sat else None


# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA:
    sat, result, k = MinAutGenerator(alphabet, pos, neg).generate()
    return AutBuilder(alphabet, pos, neg, k).build(result) if sat else None


# Q4
def gen_autc(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    sat, result = CompAutGenerator(alphabet, pos, neg, k).generate()
    return AutBuilder(alphabet, pos, neg, k).build(result) if sat else None


# Q5
def gen_autr(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
    sat, result = RevAutGenerator(alphabet, pos, neg, k).generate()
    return AutBuilder(alphabet, pos, neg, k).build(result) if sat else None


# Q6
def gen_autcard(alphabet: str, pos: list[str], neg: list[str], k: int, ell: int) -> DFA:
    sat, result = CardAutGenerator(alphabet, pos, neg, k, ell).generate()
    return AutBuilder(alphabet, pos, neg, k).build(result) if sat else None


# Q7
def gen_autn(alphabet: str, pos: list[str], neg: list[str], k: int) -> NFA:
    sat, result = AutGenerator(alphabet, pos, neg, k).generate()
    return AutBuilder(alphabet, pos, neg, k).build(result) if sat else None


##################################################


def main():
    test_aut()
    test_minaut()
    test_autc()
    test_autr()
    test_autcard()
    test_autn()


if __name__ == "__main__":
    main()

