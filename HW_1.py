#collaborated with Jasper Burns


import re
import json


#Functions

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

def directions(ts):
	if ts[0] == 'forward' and ts[1] == ';':
		return {'Forward':[directions(ts[2:])]}
	if ts[0] == 'reverse' and ts[1] == ';':
		return {'Reverse':[directions(ts[2:])]}
	if ts[0] == 'left':
		if ts[1] == 'turn' and ts[2] == ';':
			return {'LeftTurn':[directions(ts[3:])]}
	if ts[0] == 'right':
		if ts[1] == 'turn' and ts[2] == ';':
			return {'RightTurn':[directions(ts[3:])]}
	if ts[0] == 'stop' and ts[1] == ';':
		return 'Stop'

def variable(ts):
	if re.match(r"^([a-zA-Z]+)$",ts[0]):
		return {"Variable": [ts[0]]}, ts[1:]

def number(ts):
	if re.match(r"^([1-9][0-9]*)$", ts[0]):
		return {"Number": [int(ts[0])]}, ts[1:]

def term(ts):
	if ts[0] == 'plus' and ts[1] == '(':
		e1, ts = term(ts[2:])
		if ts[0] == ',':
			e2, ts = term(ts[1:])
			if ts[0] == ')':
				return {'Plus': [e1, e2]}, ts[1:]

	elif ts[0] == 'mult' and ts[1] == '(':
		e1, ts = term(ts[2:])
		if ts[0] == ',':
			e2, ts = term(ts[1:])
			if ts[0] == ')':
				return {'Mult': [e1, e2]}, ts[1:]

	elif ts[0] == 'log' and ts[1] == '(':
		e1, ts = term(ts[2:])
		if ts[0] == ')':
			return {'Log':[e1]}, ts[1:]

	elif ts[0] == '(':
		e1, ts = term(ts[1:])
		if e1 != None:
			if ts[0] == '+':
				e2, ts = term(ts[1:])
				if ts[0] == ")":
					return {'Plus': [e1, e2]}, ts[1:]
			if ts[0] == '*':
				e2, ts = term(ts[1:])
				if ts[0] == ")":
					return {'Mult': [e1, e2]}, ts[1:]

	elif ts[0] == '@':
		return variable(ts[1:])
	elif ts[0] == '#':
		return number(ts[1:])

	return None, None

def formula(ts):
	if ts[0] == 'and' and ts[1] == '(':
		e1, ts = formula(ts[2:])
		if ts[0] == ',':
			(e2, ts) = formula(ts[1:])
			if ts[0] == ')':
				return {'And': [e1, e2]}, ts[1:]

	elif ts[0] == 'or' and ts[1] == '(':
		e1, ts = formula(ts[2:])
		if ts[0] == ',':
			(e2, ts) = formula(ts[1:])
			if ts[0] == ')':
				return {'Or': [e1, e2]}, ts[1:]

	elif ts[0] == 'not' and ts[1] == '(':
		e1, ts = formula(ts[2:])
		if ts[0] == ')':
			return {'Not':[e1]}, ts[1:]

	elif ts[0] == 'equal' and ts[1] == '(':
		e1, ts = term(ts[2:])
		if ts[0] == ',':
			(e2, ts) = term(ts[1:])
			if ts[0] == ')':
				return {'Equal': [e1, e2]}, ts[1:]

	elif ts[0] == 'less' and ts[1] == 'than' and ts[2] == '(':
		e1, ts = term(ts[3:])
		if ts[0] == ',':
			(e2, ts) = term(ts[1:])
			if ts[0] == ')':
				return {'LessThan': [e1, e2]}, ts[1:]

	elif ts[0] == 'greater' and ts[1] == 'than' and ts[2] == '(':
		e1, ts = term(ts[3:])
		if ts[0] == ',':
			(e2, ts) = term(ts[1:])
			if ts[0] == ')':
				return {'GreaterThan': [e1, e2]}, ts[1:]

	elif ts[0] == 'false':
		return "False", ts[1:]

	elif ts[0] == 'true':
		return "True", ts[1:]

	elif ts[0] == '(':

		e1f, tsf = formula(ts[1:])
		e1t, tst = term(ts[1:])

		if e1f != None:
			ts = tsf[0:]
			e1 = e1f
			if ts[0] == '&&':
				e2, ts = formula(ts[1:])
				if ts[0] == ")":
					return {'And': [e1, e2]}, ts[1:]
			if ts[0] == '||':
				e2, ts = formula(ts[1:])
				if ts[0] == ")":
					return {'Or': [e1, e2]}, ts[1:]

		elif e1t != None:
			ts = tst[0:]
			e1 = e1t
			if ts[0] == '==':
				e2, ts = term(ts[1:])
				if ts[0] == ")":
					return {'Equal': [e1, e2]}, ts[1:]
			if ts[0] == '<':
				e2, ts = term(ts[1:])
				if ts[0] == ")":
					return {'LessThan': [e1, e2]}, ts[1:]
			if ts[0] == '>':
				e2, ts = term(ts[1:])
				if ts[0] == ")":
					return {'GreaterThan': [e1, e2]}, ts[1:]

	return None, None

def program(ts):
	if ts[0] == 'print':
		tsc = ts[0:]
		e1, ts = formula(ts[1:])
		if e1 != None:
			if ts[0] == ';':
				return {"Print":[e1, program(ts[1:])]}
		else:
			e1, ts = term(tsc[1:])
			if e1 != None:
				if ts[0] == ';':
					return {"Print":[e1, program(ts[1:])]}
	elif ts[0] == 'assign' and ts[1] == '@':
		var, ts = variable(ts[2:])
		if ts[0] == ':=':
			e1, ts = term(ts[1:])
			if ts[0] == ';':
				return {"Assign":[var,e1, program(ts[1:])]}

	elif ts[0] == 'end' and ts[1] == ';':
		return 'End'

	return None

def complete(s):
	ts = tokenize(['print', 'assign', 'end', 'true', 'false', 'not', 'and', 'or', 'equal', 'less', 'than', 'greater', 'plus', 'mult', 'log', '@', '#', ';', ':=', '(', ')', ',', '+', '*', '&&', "||", "==", "<", ">"], s)


	t = term(ts)
	f = formula(ts)
	p = program(ts)


	if t[0] != None:
		return t[0]
	if f[0] != None:
		return f[0]
	if p != None:
		return p




























