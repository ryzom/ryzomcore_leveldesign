"""Edits of *_words_*.txt worksheets (UTF-8 with BOM, LF) that keep every other byte.

words_edit.py set FILE ID COLUMN OLD NEW               replace OLD (must occur once in that cell) by NEW
words_edit.py setcell FILE ID COLUMN OLDCELL NEWCELL   replace the whole cell (must equal OLDCELL)
words_edit.py renameid FILE OLDID NEWID
words_edit.py hash FILE ID                             computed hash of the row (makeHashCode) and the stored one
words_edit.py rehash ID OLDHASH NEWHASH FILE...        replace the stored hash of a row (must be OLDHASH)
"""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ryi18n


def load(path):
	s, bom = ryi18n.read_text(path)
	if not bom or '\r' in s:
		ryi18n.fail('%s: expected UTF-8 with BOM and LF line endings' % path)
	return s.split('\n')


def save(path, lines):
	ryi18n.write_text(path, '\n'.join(lines), True)


def idcol(h):
	return 1 if h[0] == '*HASH_VALUE' else 0


def row_index(lines, rid, path):
	c = idcol(lines[0].split('\t'))
	hits = [i for i in range(1, len(lines)) if lines[i] and lines[i].split('\t')[c] == rid]
	if len(hits) != 1:
		ryi18n.fail('%s: %d rows with id %s' % (path, len(hits), rid))
	return hits[0]


def args(n):
	if len(sys.argv) != n:
		ryi18n.fail(__doc__)
	return sys.argv[2:]


cmd = sys.argv[1] if len(sys.argv) > 1 else ''
if cmd in ('set', 'setcell'):
	path, rid, col, old, new = args(7)
	if '\t' in new or '\n' in new:
		ryi18n.fail('tabs and line breaks cannot go in a cell')
	lines = load(path)
	h = lines[0].split('\t')
	if col not in h:
		ryi18n.fail('%s: no column %s' % (path, col))
	ci = h.index(col)
	ri = row_index(lines, rid, path)
	cells = lines[ri].split('\t')
	while len(cells) <= ci:
		cells.append('')
	if cmd == 'set':
		if cells[ci].count(old) != 1:
			ryi18n.fail('%s: %r does not occur once in %s %s: %r' % (path, old, rid, col, cells[ci]))
		cells[ci] = cells[ci].replace(old, new)
	else:
		if cells[ci] != old:
			ryi18n.fail('%s: %s %s is %r' % (path, rid, col, cells[ci]))
		cells[ci] = new
	lines[ri] = '\t'.join(cells)
	save(path, lines)
	print(path, rid, col, 'set')
elif cmd == 'renameid':
	path, old, new = args(5)
	lines = load(path)
	c = idcol(lines[0].split('\t'))
	if any(l and l.split('\t')[c] == new for l in lines[1:]):
		ryi18n.fail('%s: id %s exists already' % (path, new))
	ri = row_index(lines, old, path)
	cells = lines[ri].split('\t')
	cells[c] = new
	lines[ri] = '\t'.join(cells)
	save(path, lines)
	print(path, old, '->', new)
elif cmd == 'hash':
	path, rid = args(4)
	lines = load(path)
	h = lines[0].split('\t')
	cells = lines[row_index(lines, rid, path)].split('\t')
	print('computed', ryi18n.words_hash(h, cells), 'stored', cells[0].lstrip('_') if h[0] == '*HASH_VALUE' else None)
elif cmd == 'rehash' and len(sys.argv) >= 6:
	rid, old, new = sys.argv[2:5]
	for path in sys.argv[5:]:
		lines = load(path)
		if lines[0].split('\t')[0] != '*HASH_VALUE':
			ryi18n.fail('%s: no *HASH_VALUE column' % path)
		ri = row_index(lines, rid, path)
		cells = lines[ri].split('\t')
		if cells[0] != '_' + old:
			ryi18n.fail('%s: %s has hash %s, not _%s' % (path, rid, cells[0], old))
		cells[0] = '_' + new
		lines[ri] = '\t'.join(cells)
		save(path, lines)
		print(path, rid, old, '->', new)
else:
	ryi18n.fail(__doc__)
