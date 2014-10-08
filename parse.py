import re

#Collaboration with Jasper Burns, Kevin Mannix

RESERVEDWORDS = ['true', 'false', 'xor', 'not', 'log']

# 1a
def variable(ts):
	if re.match("^([a-z][\w]*)$", ts[0]) and ts[0] not in RESERVEDWORDS:
		return ts[0], ts[1:]
	else:
		return None, None

def number(ts):
	if re.match("-?\d+$", ts[0]):
		return int(ts[0]), ts[1:]
	else:
		return None, None

#1b
def formula(ts):
	e1, ts = left(ts)

	if e1 is not None:
		if ts:
			if ts[0] == 'xor':
				e2, ts = formula(ts[1:])
				if e2 is not None:
					return {'Xor': [e1, e2]}, ts
				return None, None
		return e1, ts
	return None, None

def left(ts):
	if ts[0] == 'not':
		e1, ts = fparenthesis(ts[1:])
		return {'Not': [e1]}, ts

	if ts[0] == '(':
		e1, ts = fparenthesis(ts)
		return {'Parens': [e1]}, ts

	elif ts[0] == 'true':
		return 'True', ts[1:]

	elif ts[0] == 'false':
		return 'False', ts[1:]

	else:
		var, ts = variable(ts)
		if var is not None:
			return {'Variable': [var]}, ts
		return None, None

def fparenthesis(ts):
	if ts[0] == '(':
		e1, ts = formula(ts[1:])
		if ts[0] == ')':
			return e1, ts[1:]

#1c
def term(ts):
	e1, ts = factor(ts)

	if e1 is not None:
		if ts:
			if ts[0] == '+':
				e2, ts = term(ts[1:])
				if e2 is not None:
					return {'Plus': [e1, e2]}, ts
				return None, None
		return e1, ts
	return None, None

def factor(ts):
	e1, ts = leftfactor(ts)

	if e1 is not None:
		if ts:
			if ts[0] == '*':
				e2, ts = factor(ts[1:])
				if e2 is not None:
					return {'Mult': [e1, e2]}, ts
				return None, None
		return e1, ts
	return None, None

def leftfactor(ts):
	if ts[0] == 'log':
		e1, ts = parenthesis(ts[1:])
		return {'Log': [e1]}, ts

	if ts[0] == '(':
		e1, ts = parenthesis(ts)
		return {'Parens': [e1]}, ts

	else:
		var, tsV = variable(ts)
		num, tsN = number(ts)
		if var is not None:
			return {'Variable': [var]}, tsV
		elif num is not None:
			return {'Number': [num]}, tsN

		return None, None

def parenthesis(ts):
	if ts[0] == '(':
		e1, ts = term(ts[1:])
		if ts[0] == ')':
			return e1, ts[1:]

#1d
def program(ts):
	if not ts or ts[0] == '}':
		return 'End', ts
	else:
		if ts[0] == 'print':
			exp, ts = expression(ts[1:])
			if exp is not None:
				if ts[0] == ';':
					end, ts = program(ts[1:])
					if end is not None:
						return {'Print': [exp, end]}, ts

		elif ts[0] == 'assign':
			var, ts = variable(ts[1:])
			if var is not None:
				if ts[0] == ':=':
					exp, ts = expression(ts[1:])
					if exp is not None:
						if ts[0]==';':
							end, ts = program(ts[1:])
							if end is not None:
								return {'Assign': [{'Variable':[var]}, exp, end]}, ts
		elif ts[0] == 'if':
			exp, ts = expression(ts[1:])
			if exp is not None:
				if ts[0] == '{':
					prog, ts = program(ts[1:])
					if prog is not None:
						if ts[0] == '}':
							prog2, ts = program(ts[1:])
							if prog2 is not None:
								return {'If':[exp, prog, prog2]}, ts
		elif ts[0] == 'while':
			exp, ts = expression(ts[1:])
			if exp is not None:
				if ts[0] == '{':
					prog, ts = program(ts[1:])
					if prog is not None:
						if ts[0] == '}':
							prog2, ts = program(ts[1:])
							if prog2 is not None:
								return {'While':[exp, prog, prog2]}, ts

		return None



def expression(ts):
	t, tst = term(ts)
	f, tsf = formula(ts)


	if t and f:
		if len(tst) < len(tsf):
			return t, tst
		else:
			return f, tsf
	elif f:
		return f, tsf
	elif t:
		return t, tst

	else:
		return None, None










