from utils import *
from tests import *

from automata.fa.fa import FA
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from pysat.solvers import Minisat22, Minicard
from pysat.formula import CNF, CNFPlus, IDPool
from pysat.card import CardEnc


#########################

################### VARIABLES ####################

class ID:

	P = 0 # si l'état est présent dans l'automate
	A = 1 # si l'état est accpetant
	T = 2 # les transitions
	V = 3 # les états visiter lors de l'éxécution

	# Pour transformation de Tseitin
	X = 4
	Y = 5

	vpool = IDPool(start_from=1)

	def __init__(self, id: int):
		self.id = id

	def __str__(self):
		string = ""
		# TODO
		return string

	@staticmethod
	def p(x): return ID.vpool.id((ID.P, x))

	@staticmethod
	def a(x): return ID.vpool.id((ID.A, x))

	@staticmethod
	def t(x, y, l): return ID.vpool.id((ID.T, x, y, l))

	@staticmethod
	def v(x, i, w): return ID.vpool.id((ID.V, x, i, w))

	@staticmethod
	def x(x, s, w): return ID.vpool.id((ID.X, x, s, w))

	@staticmethod
	def y(x, y, i, w): return ID.vpool.id((ID.Y, x, y, i, w))

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
		Yo
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
					if x!=0: yield [-ID.t(x, y, l), ID.p(x)]
					if x!=y: yield [-ID.t(x, y, l), ID.p(y)]

	def _consistence(self):
		"""
		Yo
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
				#yield [-ID.v(x, len(w), w), ID.a(x)]
				yield [-ID.x(x, len(w), w), ID.v(x, len(w), w)]
				yield [-ID.x(x, len(w), w), ID.a(x)]
				yield [-ID.v(x, len(w), w), -ID.a(x), ID.x(x, len(w), w)]

		# Il n'existe pas d'exécution acceptante pour tous les mots de neg
		for w in self.neg:
			for x in range(self.k):
				yield [-ID.v(x, len(w), w), -ID.a(x)]

		# Il existe une exec ??

		# Les exécutions sont valides
		for w in self.pos + self.neg:
			for i in range(len(w)):
				for x in range(self.k):
					for y in range(self.k):
						if i==0 and x!=0: continue
						yield [-ID.v(x, i, w), -ID.t(x, y, w[i]), ID.v(y, i+1, w)]
						#yield [-ID.v(x, i, w), -ID.v(y, i+1, w), ID.t(x, y, w[i])]

		for w in self.pos + self.neg:
			for i in range(len(w)):
				for x in range(self.k):
					yield [-ID.v(x, i+1, w)] + [ID.y(x, y, i, w) for y in range(self.k)]
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
		Yo
		"""

		# 
		for x in range(self.k):
			for l in self.alphabet:
				for y in range(self.k):
					for z in range(self.k):
						if y!=z: yield [-ID.t(x, y, l), -ID.t(x, z, l)]

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
		Yo
		"""

		# 
		for x in range(self.k):
			for l in self.alphabet:
				yield [ID.t(x, y, l) for y in range(self.k)]

		# 
		for x in range(self.k):
			yield [ID.t(y, x, l) for y in range(self.k) for l in self.alphabet]
			

	def _get_constraints(self) -> list:
		return super()._get_constraints() + [
			self._completeness,
		]


class RevAutGenerator(DetAutGenerator):

	def __init__(self, alphabet: str, pos: list[str], neg: list[str], k: int):
		super().__init__(alphabet, pos, neg, k)

	def _reversibility(self):
		"""
		Yo
		"""

		# 
		for w in self.pos + self.neg:
			for i in range(len(w)):
				for x in range(self.k):
					for y in range(self.k):
						if i==0 and x!=0: continue
						yield [-ID.v(y, i, w), -ID.t(y, x, w[i]), ID.v(x, i+1, w)]
						yield [-ID.v(y, i, w), -ID.v(x, i+1, w), ID.t(y, x, w[i])]

	def _get_constraints(self) -> list:
		return super()._get_constraints() + [
			self._reversibility,
		]

class CardAutGenerator(DetAutGenerator):

	def __init__(self, alphabet: str, pos: list[str], neg: list[str], k: int, ell: int):
		super().__init__(alphabet, pos, neg, k)
		self.ell = ell

	def _generate(self, *args) -> CNFPlus:
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
		transitions = {f"q{x}" : dict() for x in range(self.k) if ID.p(x) in model}
		for x in range(self.k):
			for y in range(self.k):
				for l in self.alphabet:
					if ID.t(x, y, l) in model:
						transitions[f"q{x}"][l] = f"q{y}"
		return transitions

	def _get_nd_transitions(self, model: list[int]) -> dict[int, dict[str, list[int]]]:
		transitions = {f"q{x}" : dict() for x in range(self.k) if ID.p(x) in model}
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
		return DFA (
			states=self._get_states(model),
			input_symbols=set(self.alphabet),
			transitions=self._get_transitions(model, *args),
			initial_state="q0",
			final_states=self._get_final_states(model),
			allow_partial=True
		) if FA == "DFA" else \
				NFA (
			states=self._get_states(model),
			input_symbols=set(self.alphabet),
			transitions=self._get_transitions(model, *args),
			initial_state="q0",
			final_states=self._get_final_states(model)
		)

##################################################

################### QUESTIONS ####################

# Q2
def gen_aut(alphabet: str, pos: list[str], neg: list[str], k: int) -> DFA:
	sat, result = DetAutGenerator(alphabet, pos, neg, k).generate()
	return AutBuilder(alphabet, pos, neg, k).build(result) if sat else None

# Q3
def gen_minaut(alphabet: str, pos: list[str], neg: list[str]) -> DFA:
	sat, result, k = MinAutGenerator(alphabet, pos, neg).generate("verbose")
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

if __name__ == '__main__':
	main()
