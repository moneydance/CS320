#Collaboration with Jasper Burns, Kevin Mannix

from math import log, floor
import re
from parse import program



'''
#	[Term-Number]		________
# 						Σ, n ⇓ n
#
#	This means that within environment Σ, n evaluates to n

#	[Term-Variable]		Σ(x) = v
#					 	Σ, x ⇓ v
#
#	This means that within environment Σ, x evaluates to v

#	[Term-Parens]		Σ, t ⇓ v
#						Σ, ( t ) ⇓ v
#
#	This means that within environment Σ, if t evaluates to v, then (t) evaluates to v


#	[Term-Log]			Σ, t ⇓ v
#						Σ, log ( t ) ⇓ ⌊ log2 (v) ⌋
#
#	This means that within environment Σ, if t evaluates to v, then log(t) evaluates to the floor of log(v)


#	[Term-Plus]			Σ, t1 ⇓ v1    Σ, t2 ⇓ v2
#						Σ, t1 + t2 ⇓ v1 + v2
#
#	This means that within environment Σ, if t1 evaluates to v1 and t2 evaluates to v2, then t1+t2 evaluates to v1+v2


#	[Term-Mult]			Σ, t1 ⇓ v1    Σ, t2 ⇓ v2
#						Σ, t1 * t2 ⇓ v1 ⋅ v2
#
#	This means that within environment Σ, if t1 evaluates to v1 and t2 evaluates to v2, then t1*t2 evaluates to v1*v2
'''

#2a
def evalTerm(env, t):
	if type(t) == dict:
		for label in t:

			children = t[label]

			if label == "Number":
				e1 = children[0]
				return e1

			elif label == "Variable":
				e1 = children[0]
				return env[e1]

			elif label == "Parens":
				e1 = children[0]
				return evalTerm(env, e1)

			elif label == "Log":
				e1 = children[0]
				return log(evalTerm(env, e1), 2)

			elif label == "Plus":
				e1, e2 = children[0], children[1]
				return evalTerm(env, e1) + evalTerm(env, e2)

			elif label == "Mult":
				e1, e2 = children[0], children[1]
				return evalTerm(env, e1) * evalTerm(env, e2)



#2b

'''
#	[Formula-True]		______________
#						Σ, true ⇓ true
#
#	This means that within environment Σ, true evaluates to true

#	[Formula-False]		________________
# 						Σ, false ⇓ false
#
#	This means that within environment Σ, false evaluates to false

#	[Formula-Variable]	Σ(x) = v
#						Σ, x ⇓ v
#
#	This means that within environment Σ, x evaluates to v

#	[Formula-Parens]	Σ, f ⇓ v
#						Σ, ( f ) ⇓ v
#
#	This means that within environment Σ, if f evaluates to v, then (f) also evaluates to v

#	[Formula-Not]		Σ, f ⇓ v
#						Σ, not f ⇓ ¬ v
#
#	This means that within environment Σ, if f evaluates to v, then not f  evaluates to not v

#	[Formula-Xor]		Σ, f1 ⇓ v1    Σ, f2 ⇓ v2
#						Σ, f1 xor f2 ⇓ v1 ⊕ v2
#
#	This means that within environment Σ, if f1 evaluates to v1 and f2 evaluates to v2,
# 										  then f1 xor f2 evaluates to (v1 != v2)
'''

def evalFormula(env, f):

	if type(f) == dict:

		for label in f:
			children = f[label]

			if (label == 'Parens'):
				e1 = children[0]
				return evalFormula(env, e1)

			elif (label == 'Not'):
				e1 = children[0]
				return not evalFormula(env, e1)

			elif (label == 'Xor'):
				e1, e2 = children[0], children[1]
				return (evalFormula(env, e1) != evalFormula(env, e2))

			elif (label == 'Variable'):
				e1 = children[0]
				if (e1 in env):
					return env[e1]
				else:
					print(e1 + " is unbound.")
					exit()

	else:
		if (f == 'True'):
			return True
		if (f == 'False'):
			return False


#2c

def execProgram(env,s):
	if type(s) == str:
		if s == "End":
			return (env, [])

	elif type(s) == dict:
		for label in s:
			if label == "Print":
				children = s[label]
				c1, c2 = children[0], children[1]
				exp = execExpression(env, c1)
				env2, s2 = execProgram(env, c2)
				return (env2, [exp]+s2)
			elif label == "Assign":
				children = s[label]
				c1, c2, c3 = children[0]["Variable"][0], children[1], children[2]
				exp = execExpression(env, c2)
				env[c1] = exp
				env2, s2 = execProgram(env, c3)
				return (env2, s2)
			elif label == "If":
				children = s[label]
				c1, c2, c3 = children[0], children[1], children[2]
				conditional = execExpression(env, c1)

				#if exp is True
				if conditional:
					env2, trueresult = execProgram(env, c2)
					env3, remaining = execProgram(env2, c3)
					return env3, trueresult + remaining
				#if exp is False
				else:
					env2, remaining = execProgram(env, c3)
					return env2, remaining

			#similar to if
			elif label == "While":
				children = s[label]
				c1, c2, c3 = children[0], children[1], children[2]
				conditional = execExpression(env, c1)

				#if conditional is True
				if conditional:
					#do c2 return new environment and result from passed loop
					env2, statement = execProgram(env, c2)
					#check if env2 changed and the loop will continue, return remaining result
					env3, remaining = execProgram(env2, s)
					return env3, statement + remaining
				else:
					env2, remaining = execProgram(env, c3)
					return env2, remaining

#Helper
def execExpression(env, e):
	eT = evalTerm(env, e)
	eF = evalFormula(env, e)

	if eF != None:
		return eF
	elif eT != None:
		return eT

#2d

def tokenize(tm,s):
	#creates a tokenize string
	specials = ["\\", "^", "$", ".", "|", "?", "*", "+", "(", ")", "[", "]", "{", "}"]

	terminals = "\s+"
	for t in tm:
		if t in specials:
			t = '\\' + t

		terminals += "|" + t

	tokens = [token for token in re.split(r"("+terminals+")", s)]

	# Throw out the spaces and return the result.
	return [t for t in tokens if not t.isspace() and not t == ""]

def interpret(s):
	tm = ['not','true','false','+', '*', '(', ')', 'log', 'print', 'assign', 'if', 'while', ';', ':=', '{', '}', 'xor']
	ts = tokenize(tm,s)
	parse = program(ts)[0]
	if parse is not None:
		exp = execProgram({}, parse)[1]
		if exp is not None:
			return exp


