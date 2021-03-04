from typing import Dict, List, TypeVar, Generic
from graphviz import Digraph
from exprAnalysis import Node, TokenType

T = TypeVar("T")

class FA(Generic[T]):
	states:			int
	finalStates:	List[int]
	aplhabet:		set
	transitions:	List[Dict[str, T]]

	"""
	Class defining finite state automaton, either DFA or NFA
	states = number of states
	finalStates = list of final states
	alphabet = set of characters accepted by machine
	transitions = for a dfa a transition is stored as self.transitions[state][chr] = nextState
				| for a nfa a transition is stored as self.transitions[state][chr] = [nextStates]
	"""
	def __init__(self, s: int, fs: List[int]):
		self.states = s
		self.finalStates = fs
		self.alphabet = set()
		self.transitions = [{} for i in range(0, s)]

	"""
	Method returning the DFA/NFA in text format
	"""
	def toText(self) -> str:
		automatonText = str(self.states) + "\n"
		for s in self.finalStates:
			automatonText += str(s) + " "
		automatonText += "\n"
		for s in range(0, self.states):
			for l in self.transitions[s]:
				try:
					it = iter(self.transitions[s][l])
					automatonText += str(s) + " " + l + " "
					for ns in it:		# for next state in iterator
						automatonText += str(ns) + " "
					automatonText += "\n"
				except TypeError:		# non iterable data type
					automatonText += str(s) + " " + l + " " + str(self.transitions[s][l]) + "\n"
		return automatonText

	"""
	Method returning the DFA/NFA in Digraph format
	"""
	def toGraphViz(self) -> Digraph:
		dot = Digraph(comment='automata')

		for i in range(0, self.states):
			if i in self.finalStates:
				if i == 0:
					dot.node(str(i), str(i), shape='doubleoctagon')
				else:
					dot.node(str(i), str(i), shape='doublecircle')
			else:
				if i == 0:
					dot.node(str(i), str(i), shape='octagon')
				else:
					dot.node(str(i), str(i), shape='circle')

		for s in range(0, len(self.transitions)):
			for l in self.transitions[s]:
				try:
					it = iter(self.transitions[s][l])
					for ns in it:
						dot.edge(str(s), str(ns), label=l)
				except TypeError:
					dot.edge(str(s), str(self.transitions[s][l]), label=l)

		return dot

class NFA(FA[list]):
	def __init__(self, states: int, finalStates: List[int], transitions: List[Dict[str, list]], alphabet: set):
		super().__init__(states, finalStates)
		self.transitions = transitions
		self.alphabet = alphabet

	@staticmethod
	def fromText(text: str):
		lines = text.splitlines()
		states = int(lines.pop(0))
		finalStates = [int(fs) for fs in lines.pop(0).split()]
		transitions = [{} for i in range(0, states)]
		alphabet = set()
		for transition in lines:
			elems = transition.split()
			alphabet.add(elems[1])
			transitions[int(elems[0])] = {elems[1]: elems[2:]}
		return NFA(states, finalStates, transitions, alphabet)

	"""
	Method that adds a transition form state startState upon finidng character l
	"""
	def addTransition(self, startState: int, l: str, endState: int):
		self.alphabet.add(l)
		if startState >= len(self.transitions):
			self.transitions += [{} for i in range (len(self.transitions) - 1, startState)] 
		if not l in self.transitions[startState]:
			self.transitions[startState][l] = []
		self.transitions[startState][l].append(endState)

	"""
	Method that recursively builds all the epsilon enclosures for every state of the NFA
	Returns a list of length self.states, such that each index represents the epsilon enclosure of that state
	"""
	def buildEpsilonEncapsiulation(self) -> List[set]:
		# recursive function that finds epsilon enclosure for state i
		def explore(i, stateEnc):
			stateEnc.add(i)

			if not "eps" in self.transitions[i]:
				return stateEnc

			for s in self.transitions[i]["eps"]:
				if not s in stateEnc:
					stateEnc |= explore(s, stateEnc)

			return stateEnc

		epsEnc = []
		for i in range(0, self.states):
			epsEnc.append(explore(i, set()));
		return epsEnc

	"""
	Static method that takes a syntax tree of an expression and converts it into a NFA
	Traverses syntax tree Root-Left-Right and build appropriate states and transitions for each TokenType encountered
	"""
	@staticmethod
	def convert(syntaxTree: Node):
		nfa = NFA(0, [], [{}], set())

		"""
		accepting a letter in the syntax tree
		creates a new state and links last nfa state with the new one with a transition on the letter
		increments the number of states in nfa
		"""
		def acceptLetter(node: Node, nfa: NFA):
			nfa.addTransition(nfa.states, node.value, nfa.states + 1)
			nfa.states += 1

		"""
		accepting a concatenation in the syntax tree
		accepts each of the node children in sequence
		"""
		def acceptConcat(node: Node, nfa: NFA):
			for child in node.children:
				accept(child, nfa)

		"""
		accepting a reunion in the syntax tree
		creates a start state that is linked through an eps transition to the sub-NFAs that accept the children of the node
		links all lose ends of the sub-NFAs to a new end state through eps transitions
		"""
		def acceptReunion(node: Node, nfa: NFA):
			startReunionState = nfa.states		# start state of reunion
			ends = []							# ends of sub-NFAs
			for child in node.children:
				nfa.states += 1
				nfa.addTransition(startReunionState, 'eps', nfa.states)
				accept(child, nfa)
				ends.append(nfa.states)
			
			# new end state
			nfa.states += 1
			for s in ends:
				nfa.addTransition(s, 'eps', nfa.states)

		"""
		accepting a kleene star in the syntax tree
		creates start and end states to make a loop for sub-NFA that acceps its child
		"""
		def acceptKleene(node: Node, nfa: NFA):
			start = nfa.states		# start state
			nfa.states += 1
			nfa.addTransition(start, 'eps', nfa.states)
			accept(node.children[0], nfa)		# kleene star always has only 1 child
			end = nfa.states + 1	# end state
			# adding all transitions for the loop
			nfa.addTransition(nfa.states, 'eps', end)
			nfa.addTransition(nfa.states, 'eps', start + 1)
			nfa.addTransition(start, 'eps', end)
			nfa.states += 1

		"""
		acceps a node of any type
		the accepting process uses the number of states of the NFA as a starting point
		basically a DFS with extra steps
		"""
		def accept(node: Node, nfa: NFA):
			if node.tokentype == TokenType.T_LETTER:
				acceptLetter(node, nfa)
			elif node.tokentype == TokenType.T_CON:
				acceptConcat(node, nfa)
			elif node.tokentype == TokenType.T_REUN:
				acceptReunion(node, nfa)
			else:
				acceptKleene(node, nfa)

		accept(syntaxTree, nfa)
		# adding the final state of the NFA, an empty transtions list for it and incrementing states number
		nfa.finalStates = [nfa.states]
		nfa.transitions.append({})
		# the increment is needed because throughout the process we use nfa.states as an index of the last state
		# but in the final NFA we need the number of states as len() type number
		nfa.states += 1
		return nfa


	

class DFA(FA[int]):
	def __init__(self, states: int, finalStates: List[int], transitions: List[Dict[str, int]], alphabet: set):
		super().__init__(states, finalStates)
		self.transitions = transitions
		self.alphabet = alphabet

	@staticmethod
	def fromText(text: str):
		lines = text.splitlines()
		states = int(lines.pop(0))
		finalStates = [int(fs) for fs in lines.pop(0).split()]
		transitions = [{} for i in range(0, states)]
		alphabet = set()
		for transition in lines:
			elems = transition.split()
			alphabet.add(elems[1])
			transitions[int(elems[0])] = {elems[1]: elems[2]}
		return DFA(states, finalStates, transitions, alphabet)

	"""
	Static method that takes a NFA and returns the DFA that acceps the same language
	"""
	@staticmethod
	def convert(nfa: NFA):
		epsEnc = nfa.buildEpsilonEncapsiulation();	# list of epsilon enlcosures for each state of the NFA
		alphabet = nfa.alphabet.copy()				# alphabet of the new DFA
		transitions = [{}]							# transitions of the new DFA
		statesDefinition = [epsEnc[0]]				# defines each state of the DFA as a subset of the state of the NFA
		currentState = 0							# state from whitch we are currently adding transitions in DFA
		finalStates = []							# final states of the new DFA
		
		# removing epsilon as a character from DFA's alphabet
		if "eps" in alphabet:
			alphabet.remove("eps")

		while currentState < len(statesDefinition):
			# for each current state we are going through the letters of the alphabet
			for l in alphabet:
				# constructing the definition of a new state as a subset of of the states of the NFA
				newStateDefinition = set()
				for inState in statesDefinition[currentState]:
					if l in nfa.transitions[inState]:
						for s in nfa.transitions[inState][l]:
							newStateDefinition.update(epsEnc[s])

				if newStateDefinition in statesDefinition:
					# if the definition of the state is already recorded, we are just adding the transition
					transitions[currentState][l] = statesDefinition.index(newStateDefinition)
				else:
					# recordind the definition of the new state in statesDefinition
					statesDefinition.append(newStateDefinition)
					# adding a new possible start state in transitions
					transitions.append({})
					# adding the transition
					transitions[currentState][l] = statesDefinition.index(newStateDefinition)

			# going to the next state
			currentState += 1

		# recoding the final states in variable finalStates
		for i in range(0, len(statesDefinition)):
			for state in statesDefinition[i]:
				if state in nfa.finalStates:
					finalStates.append(i)
					break

		# returning the constructed DFA
		return DFA(currentState, finalStates, transitions, alphabet)