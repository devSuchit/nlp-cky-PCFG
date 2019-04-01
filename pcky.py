import re
import math

class ParseTree:
	def __init__(self, node):
		self.root = node

	def print(self, print_probs=False):
		if self.root != None: self.root.print(print_probs=print_probs)


class Node:
	def __init__(self, symbol, p, lnode=None, rnode=None):
		self.lnode = lnode
		self.rnode = rnode
		self.symbol = symbol
		self.p = p
	def print(self,offset="",print_probs=False):
		if print_probs:
			print( (offset[:-3]+"|--" if len(offset)>0 else "")+str(self.symbol)+" ("+str(math.exp(self.p)	)+")")
		else:
			print( (offset[:-3]+"|--" if len(offset)>0 else "")+str(self.symbol))
		if self.rnode != None: self.rnode.print(offset+"|  ", print_probs=print_probs)
		if self.lnode != None: self.lnode.print(offset+"   ", print_probs=print_probs)
	def __repr__(self):
		return "Node: "+self.symbol+", "+str(self.p)
	def getProb(self):
		return self.p

class Grammar:

	def __init__(self):
		self.rules = {}
		self.terminals = {}
		self.backrule = {}
		self.params = {'type-p':'p'}
		self.starts = ['S']

	def addRule(self, left_side, right_side, prob):
		if self.params['type-p'] == 'p':
			prob = math.log(prob)
		try:
			self.rules[left_side].append((right_side,prob))
		except KeyError:
			self.rules[left_side] = [(right_side,prob)]
		try:
			self.backrule[tuple(right_side)].append((left_side, prob))
		except KeyError:
			self.backrule[tuple(right_side)] = [(left_side, prob)]
		
	def addTerminal(self, left_side, right_side, prob):
		if self.params['type-p'] == 'p':
			prob = math.log(prob)
		try:
			self.terminals[right_side].append((left_side,prob))
		except KeyError:
			self.terminals[right_side] = [(left_side,prob)]		

	def print(self):
		print("Rules:\n"+str(self.rules))		
		print("Terminals:\n"+str(self.terminals))
		print("Backrules:\n"+str(self.backrule))
		
	def getTerminalRules(self, terminal):
		resp = ["OOV"]
		try:
			resp = self.terminals[terminal]
		except KeyError: pass 		
		return resp

	def getSymbolFromRule(self, rule):
		resp = []
		try:
			resp = self.backrule[tuple(rule)]
                        
		except KeyError: pass
			
		return resp

	def setParameter(self, name, value):
		if name == 'starts':
			self.starts = value.split(",")
		else:
			self.params[name] = value


def table_print(table):
	for row in table:
		line = ""
		for col in row:
			line+=str(col)+"\t"
		print(line)


def get_parse_tree(state, symbol, table):
	node = Node(symbol)

	state = state[0]
	lsym = state[0]
	rsym = state[1] 

	if lsym[0] != -1:
		node.lnode = get_parse_tree(table[lsym[0]][lsym[1]][lsym[2]],lsym[2],table)
	else:
		node.lnode = Node(lsym[2])

	if len(rsym) > 0:
		node.rnode = get_parse_tree(table[rsym[0]][rsym[1]][rsym[2]],rsym[2],table)

	return node

def pcky(grammar, sentence, debug=False):
	n = len(sentence)
	table = [[{} for i in range(n-j)] for j in range(n)]
	unaries = [[{} for i in range(n-j)] for j in range(n)]
	nodes_back = [[{} for i in range(n + 1)] for j in range(n + 1)]

	#Initialize table
	for w in range(1, n + 1):
		symbols = grammar.getTerminalRules(sentence[w-1])
		for S in symbols:
			try: 
				table[0][w-1][S[0]].append( Node(S[0], S[1], lnode=Node(sentence[w-1], 0)) )
			except KeyError:
				table[0][w-1][S[0]] = [Node(S[0], S[1], lnode=Node(sentence[w-1], 0))]
			rules = grammar.getSymbolFromRule([S[0]])

			for U in rules:	
				
				pr = U[1]+S[1]
				try: 
					table[0][w-1][U[0]].append( Node(U[0], pr, lnode=table[0][w-1][S[0]][0]) )
				except KeyError:
					table[0][w-1][U[0]] = [ Node(U[0], pr, lnode=table[0][w-1][S[0]][0]) ]
			
	if debug:
		print("Initial table: ") 
		table_print(table)
	for l in range(0, n-1):
		for s in range(n-l-1):
			for p in range(l+1):
				for X in table[p][s]:
					for Y in table[l-p][s+p+1]:
						symbols = grammar.getSymbolFromRule([X, Y])
						lnodes = table[p][s][X]
						rnodes = table[l-p][s+p+1][Y]

						for S in symbols:

							for ln in lnodes:
								for rn in rnodes:
									pr = ln.p + rn.p + S[1]
									
									try:
										table[l+1][s][S[0]].append( Node(S[0],pr,lnode=ln,rnode=rn) )
									except KeyError:
										table[l+1][s][S[0]] = [ Node(S[0],pr,lnode=ln,rnode=rn) ]

							rules = grammar.getSymbolFromRule([S[0]])
							for U in rules:			
								if U not in unaries[l+1][s] and U not in table[l+1][s]:
									for u in table[l+1][s][S[0]]:
										pr = u.p + U[1]	
										try:
											table[l+1][s][U[0]].append(Node(U[0],pr,lnode=u))
										except KeyError:
											table[l+1][s][U[0]] = [ Node(U[0],pr,lnode=u) ]
										unaries[l+1][s][U[0]] = True
							
		if debug:
			print()				
			table_print(table)


	resp = []
	for start in grammar.starts:
		if start in table[n-1][0]:
			for tree in table[n-1][0][start]:
				resp.append(tree)
	return resp

def find_best(forest):
	if len(forest) == 0: return None
	best = forest[0]
	for tree in forest[1:]:
		if best.p < tree.p:
			best = tree 
	return best

def load_grammar(grammar_filename):
	grammar = Grammar()
	pattern = re.compile(".+->.+( .+)?:\d+(\.\d+)?(|.+( .+)?:\d+(\.\d+)?)?")
	
	nline = 0
	with open(grammar_filename, 'r') as f:
		lines = f.readlines()
		for line in lines:
			nline+=1
			line = line.strip()
			if len(line) == 0 or line[0] == '#' : continue
			if line[0] == '@':
				vals = line[1:].split('=')
				grammar.setParameter(vals[0],vals[1])
				continue
			if not pattern.match(line):
				raise ValueError("Error reading grammar in file '"+grammar_filename+"', line "+str(nline)+": "+line)
				
			rule = [x.strip() for x in line.split('->')]

			for right_side in rule[1].split("|"):
				right_side = right_side.split(":")
				prob = float(right_side[1])
				right_side = right_side[0].split()
				if len(right_side) == 1 and right_side[0] == right_side[0].lower():
					grammar.addTerminal(rule[0],right_side[0], prob)	
				else:                        
					grammar.addRule(rule[0], right_side, prob)

	return grammar



def parse(grammar_filename, sentence, debug=False):
	grammar = load_grammar(grammar_filename)
	if debug: 
		print("Grammar loaded: ") 
		grammar.print()
		print("")
	
	return pcky(grammar, sentence.split(),debug=debug)


