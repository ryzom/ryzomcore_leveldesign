"""Python port of the NeL i18n hashes (CI18N::makeHash, STRING_MANAGER::makePhraseHash, makeHashCode)
and of the phrase file parser in nel/src/misc/diff_tool.cpp, for checking and regenerating HASH_VALUE lines."""
import re, sys, os


def make_hash(s):
	pc = s.encode('utf-16-le')
	n = len(pc)
	if n == 0:
		return '0000000000000000'
	ph = [0] * 8
	roll = 0
	for i in range(max(n, 64)):
		b = pc[i % n]
		k = (i >> 1) & 7
		ph[k] = (ph[k] + ((b << roll) & 0xff)) & 0xff
		ph[k] = (ph[k] + (b >> (8 - roll))) & 0xff
		roll = (roll + 1) & 7
	lo = ph[0] | (ph[1] << 8) | (ph[2] << 16) | (ph[3] << 24)
	hi = ph[4] | (ph[5] << 8) | (ph[6] << 16) | (ph[7] << 24)
	return '%08X%08X' % (lo, hi)


class ParseError(Exception):
	pass


def _skip_ws(s, i, comments=None):
	n = len(s)
	while i < n:
		c = s[i]
		if c in ' \t\r\n':
			i += 1
		elif s.startswith('//', i):
			j = s.find('\n', i)
			j = n if j < 0 else j + 1
			if comments is not None:
				comments.append(s[i:j])
			i = j
		elif s.startswith('/*', i):
			j = s.find('*/', i + 2)
			if j < 0:
				raise ParseError('unclosed comment at %d' % i)
			if comments is not None:
				comments.append(s[i:j + 2])
			i = j + 2
		else:
			break
	return i


def _marked(s, i, op, cl):
	if i >= len(s) or s[i] != op:
		raise ParseError('expected %s at %d' % (op, i))
	i += 1
	out = []
	n = len(s)
	while i < n and s[i] != cl:
		c = s[i]
		if c == op:
			raise ParseError('unescaped %s at %d' % (op, i))
		if c in '\t\n\r':
			i += 1
		elif c == '\\' and i + 1 < n and s[i + 1] != '\\':
			e = s[i + 1]
			if e == 't':
				out.append('\t')
			elif e == 'n':
				out.append('\n')
			elif e == 'd':
				out.append('\x08')
			elif e == cl or e == op:
				out.append(e)
			else:
				raise ParseError('bad escape \\%s at %d' % (e, i))
			i += 2
		elif c == '\\' and i + 1 < n and s[i + 1] == '\\':
			out.append('\\')
			i += 2
		else:
			out.append(c)
			i += 1
	if i >= n:
		raise ParseError('unclosed %s' % op)
	return ''.join(out), i + 1


_label = re.compile(r'[0-9A-Za-z_@]+')


def parse_phrases(s):
	"""Returns dicts: id, params, clauses [(cond, ident, text)], spans [(start, end) of each clause's [text] in s],
	start, end, comments (text before the id). A file with #include lines (work/phrase_wk.txt) must be read
	through its included files."""
	i = 0
	n = len(s)
	res = []
	while True:
		comments = []
		i = _skip_ws(s, i, comments)
		if i >= n:
			break
		m = _label.match(s, i)
		if not m:
			raise ParseError('expected identifier at %d: %r' % (i, s[i:i + 40]))
		ident = m.group(0)
		start = i
		i = m.end()
		i = _skip_ws(s, i)
		params, i = _marked(s, i, '(', ')')
		i = _skip_ws(s, i)
		if i >= n or s[i] != '{':
			raise ParseError('expected { in %s' % ident)
		i += 1
		clauses = []
		spans = []
		while True:
			i = _skip_ws(s, i)
			if i < n and s[i] == '}':
				break
			cond = ''
			while i < n and s[i] == '(':
				c, i = _marked(s, i, '(', ')')
				if cond:
					cond += ' '
				cond += '(' + c + ')'
				i = _skip_ws(s, i)
			m = _label.match(s, i)
			cid = ''
			if m:
				cid = m.group(0)
				i = m.end()
			i = _skip_ws(s, i)
			j = i
			text, i = _marked(s, i, '[', ']')
			clauses.append((cond, cid, text))
			spans.append((j, i))
		i += 1
		res.append(dict(id=ident, params=params, clauses=clauses, spans=spans, start=start, end=i, comments=comments))
	return res


def escape(t):
	"""The inverse of the [ ] text parsing: backslashes, brackets, tabs and newlines escaped."""
	bs = chr(92)
	return t.replace(bs, bs + bs).replace('[', bs + '[').replace(']', bs + ']').replace('\t', bs + 't').replace('\n', bs + 'n')


def fail(msg):
	sys.stderr.write(msg + '\n')
	sys.exit(1)


def read_text(path):
	"""(text, has_bom) of a UTF-8 file, line endings untouched."""
	raw = open(path, 'rb').read()
	bom = raw.startswith(b'\xef\xbb\xbf')
	return raw.decode('utf-8-sig' if bom else 'utf-8'), bom


def write_text(path, text, bom):
	open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + text.encode('utf-8'))


def phrase_hash(p):
	text = p['params'] + ''.join(c + ci + t for (c, ci, t) in p['clauses'])
	return make_hash(text)


def comment_hash(p):
	for c in p['comments']:
		m = re.match(r'//\s*HASH_VALUE\s+([0-9A-F]{16})', c)
		if m:
			return m.group(1)
	return None


def words_rows(path):
	"""Returns (header, rows) of a *_words_*.txt worksheet as lists of str (BOM and LF stripped)."""
	data = open(path, 'rb').read().decode('utf-8-sig')
	lines = data.split('\n')
	if lines and lines[-1] == '':
		lines.pop()
	rows = [l.rstrip('\r').split('\t') for l in lines]
	return rows[0], rows[1:]


def words_hash(header, row):
	"""makeHashCode: every column whose header starts with neither '*' nor 'DIFF ', the id included. A work sheet
	has no *HASH_VALUE column; its rows hash the same."""
	s = ''
	for k in range(len(header)):
		if not header[k].startswith('*') and not header[k].startswith('DIFF '):
			s += row[k] if k < len(row) else ''
	return make_hash(s)


def read_with_includes(path, depth=0):
	"""The text of a file with its #include "path" lines (relative to the file) replaced by the included files."""
	if depth > 10:
		fail('include depth at ' + path)
	s = read_text(path)[0]
	out = []
	for line in s.split('\n'):
		m = re.match(r'^\s*#include\s+"([^"]+)"', line)
		if m:
			out.append(read_with_includes(os.path.join(os.path.dirname(path), m.group(1)), depth + 1))
		else:
			out.append(line)
	return '\n'.join(out)
