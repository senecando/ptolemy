import os, sys, string, re
from flask import Flask, url_for, render_template, request, Markup


app = Flask(__name__)
app.debug = True

warning = '''
			<small>At this point, all calculations are conducted in decimal and
			converted to display in sexagesimal. This can cause bad 
			errors. For example, try: 1;1+1;0. This will be changed
			shortly.</small>
		  '''

@app.route('/query/', methods=['GET'])
@app.route('/')
def ptolemy():
	return render_template('pt.html', title="Ptolemy", instructions=True)

@app.route('/query/', methods=['POST'])
def evaluate_query():
	error = ''; steps = []; result = ''

	if request.method == 'POST':
		query = request.form['query']
		query = re.sub(r'\/','\:', query)
		query = re.sub(r'[^\w\*\+\-\/\:\^\;\,\.]', '', query)
		parts = re.split('([\*\+\-\:\^])', query)	
		formatted_query = formatParts(parts)
		if (parts == ['']):
			error = "That query is not a query at all!"

	while True:
		try:
			if (len(parts) == 1):
				result = sexagesimal(parts[0])
				break
			elif (len(parts) < 4):
				result = evaluate(parts[0], parts[2], parts[1])
				break
			c = 0; triplets = []; length = len(parts) - 2	
			
			while (c < length):
				triplets.extend([parts[c:c+3]])
				c = c + 1
			d = next_to_evaluate(triplets)

			subResult = evaluate(parts[d], parts[d+2], parts[d+1])

			parts.pop(d)
			parts.pop(d+1)
			parts[d] = subResult
			steps.append(Markup(formatParts(parts)))
		except Exception as e:
			error = "There was a problem with the query: " + formatted_query + '<br/><small><small>Python sez: ' + str(e) + '</small></small>'
			break

	if (error==''): 
		return render_template('pt.html', steps=steps, result=Markup(sexagesimal(result)), query=Markup(formatted_query), warning=Markup(warning))
	else:
		return render_template('pt.html', result=result, error=Markup(error))

def decimal(s):
	if (';' in str(s)):
		whole_and_frac = string.split(s, ";")
		number_as_decimal = float(whole_and_frac[0])
		fracs = string.split(whole_and_frac[1], ",")
		y = 1
		for x in fracs:
			x = float(x)
			denom = pow(60, y)
			number_as_decimal += x/denom
			y += 1
		return number_as_decimal
	else:
		return float(s)

def sexagesimal(n, places=2):
	# If sexagesimal, return n
	# If not, return a sexigesimal representation of n
	# If not a number, return n

	if (';' in str(n)):
		return n
	elif ('.' in str(n)):
		s = ''
		i, d = divmod(float(n), 1)
		s += str(int(i)) + ";"
		while (places > 0):
			i, d = divmod(d * 60, 1)
			s += str(int(i))
			if (places > 1):
				s += ","
			places -= 1
		return s
	else:
		return n

def evaluate(x, y, operator):
	if (operator == "*"):
		return decimal(x) * decimal(y)
	elif (operator == "+"):
		return decimal(x) + decimal(y)
	elif (operator == ':'):
		return decimal(x) / decimal(y)
	elif (operator == '-'):
		return decimal(x) - decimal(y)
	elif (operator == '^'):
		return decimal(x) ** decimal(y)
	else:
		return 1000 #For debugging purposes

def next_to_evaluate(triplets):
	order = ['^', '*', ':', '+', '-']
	for operator in order:
		c = 0
		for x in triplets:		
			if (x[1] == operator):
				return c
			c += 1
	return 0

def formatParts(parts):
	html = ''; endSuper = False
	for x in parts:
		if (x == '^'):
			html += '<sup>'
			endSuper = True
		elif (endSuper):
			html += sexagesimal(x) + '</sup>'
			endSuper = False
		elif (x == '+'):
			html += ' <b>+</b> '
		elif (x == '*'):
			html += ' &times; '
		elif (x == ':'):
			html += ' <b>:</b> '
		elif (x == '-'):
			html += ' <b>&ndash;</b> '
		else:
			html += sexagesimal(x)
	return html

def createAlert(kind, text):
	html = '<div class="%s">%s</div>' % (kind, text)
	return html

def printList(listy):
	html = "<ul>"
	for x in listy:
		html += '<li>%s</li>' % x
	html += '</ul>'
	return html