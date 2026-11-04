"""parse_uxt(path) and parse_uxt_string(text) -> ({key: dict(text, hash, start, end, comments)}, [keys in file order])
for .uxt and clause_*.txt files. 'hash' is the first HASH_VALUE comment before the key, as NeL reads it."""
import re, sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ryi18n


def parse_uxt_string(s):
	i = 0
	n = len(s)
	out = {}
	order = []
	while True:
		com = []
		i = ryi18n._skip_ws(s, i, com)
		if i >= n:
			break
		m = ryi18n._label.match(s, i)
		if not m:
			raise ryi18n.ParseError('label at %d %r' % (i, s[i:i + 30]))
		k = m.group(0)
		st = i
		i = m.end()
		i = ryi18n._skip_ws(s, i)
		t, i = ryi18n._marked(s, i, '[', ']')
		h = None
		for c in com:
			mm = re.match(r'//\s*HASH_VALUE\s+([0-9A-F]{16})', c)
			if mm:
				h = mm.group(1)
				break
		out[k] = dict(text=t, hash=h, start=st, end=i, comments=com)
		order.append(k)
	return out, order


def parse_uxt(path):
	return parse_uxt_string(ryi18n.read_text(path)[0])
