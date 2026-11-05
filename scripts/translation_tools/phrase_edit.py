"""Phrase file edits that keep the rest of the file byte-identical. Each result is checked before it is written.

phrase_edit.py text FILE ID CLAUSE_INDEX OLD_TEXT NEW_TEXT
	replaces the (unescaped) text of one clause; OLD_TEXT must match the parsed text exactly.
phrase_edit.py texts FILE EDITS.tsv
	the same for many clauses, named by their identifier: rows ID<TAB>CLAUSE_IDENTIFIER<TAB>OLD_TEXT<TAB>NEW_TEXT.
phrase_edit.py rehash ID OLDHASH NEWHASH FILE...
	replaces the HASH_VALUE comment preceding phrase ID.
phrase_edit.py hash FILE ID
	prints the computed hash of phrase ID in FILE (meaningful for work files) and its stored hash.
"""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ryi18n


def find(s, pid, path):
	ps = [p for p in ryi18n.parse_phrases(s) if p['id'] == pid]
	if len(ps) != 1:
		ryi18n.fail('%s: %d phrases named %s' % (path, len(ps), pid))
	return ps[0]


if len(sys.argv) < 2:
	ryi18n.fail(__doc__)
cmd = sys.argv[1]
if cmd == 'text' and len(sys.argv) == 7:
	path, pid, idx, old, new = sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6]
	s, bom = ryi18n.read_text(path)
	p = find(s, pid, path)
	if idx >= len(p['clauses']) or p['clauses'][idx][2] != old:
		ryi18n.fail('%s: clause %d of %s is %r' % (path, idx, pid, p['clauses'][idx][2] if idx < len(p['clauses']) else None))
	a, b = p['spans'][idx]
	s = s[:a] + '[' + ryi18n.escape(new) + ']' + s[b:]
	q = find(s, pid, path)
	if q['clauses'][idx][2] != new or len(q['clauses']) != len(p['clauses']):
		ryi18n.fail('%s: check failed' % path)
	ryi18n.write_text(path, s, bom)
	print(path, pid, 'clause', idx, 'set')
elif cmd == 'texts' and len(sys.argv) == 4:
	path, tsv = sys.argv[2], sys.argv[3]
	rows = []
	for line in open(tsv, encoding='utf-8-sig'):
		line = line.rstrip('\r\n')
		if line:
			f = line.split('\t')
			if len(f) != 4:
				ryi18n.fail('%s: expected 4 fields: %r' % (tsv, line))
			rows.append(f)
	s, bom = ryi18n.read_text(path)
	phrases = {}
	for p in ryi18n.parse_phrases(s):
		phrases.setdefault(p['id'], []).append(p)
	edits = []
	seen = set()
	for pid, ident, old, new in rows:
		if len(phrases.get(pid, [])) != 1:
			ryi18n.fail('%s: %d phrases named %s' % (path, len(phrases.get(pid, [])), pid))
		p = phrases[pid][0]
		idx = [i for i, c in enumerate(p['clauses']) if c[1] == ident]
		if (pid, ident) in seen:
			ryi18n.fail('%s: clause %s of %s is in the TSV twice' % (tsv, ident, pid))
		if len(idx) != 1:
			ryi18n.fail('%s: clause %s of %s found %d times' % (path, ident, pid, len(idx)))
		seen.add((pid, ident))
		if p['clauses'][idx[0]][2] != old:
			ryi18n.fail('%s: clause %s of %s is %r' % (path, ident, pid, p['clauses'][idx[0]][2]))
		edits.append((p['spans'][idx[0]], pid, ident, new))
	for (a, b), pid, ident, new in sorted(edits, reverse=True):
		s = s[:a] + '[' + ryi18n.escape(new) + ']' + s[b:]
	after = {}
	for p in ryi18n.parse_phrases(s):
		after.setdefault(p['id'], []).append(p)
	if sorted(after) != sorted(phrases):
		ryi18n.fail('%s: check failed, phrase list changed' % path)
	for _, pid, ident, new in edits:
		q = after[pid][0]
		if [c[1] for c in q['clauses']] != [c[1] for c in phrases[pid][0]['clauses']] or \
				[c[2] for c in q['clauses'] if c[1] == ident] != [new]:
			ryi18n.fail('%s: check failed for %s' % (path, ident))
	ryi18n.write_text(path, s, bom)
	print(path, len(edits), 'clauses set')
elif cmd == 'rehash' and len(sys.argv) >= 6:
	pid, old, new = sys.argv[2], sys.argv[3], sys.argv[4]
	for path in sys.argv[5:]:
		s, bom = ryi18n.read_text(path)
		p = find(s, pid, path)
		if ryi18n.comment_hash(p) != old:
			ryi18n.fail('%s: %s has hash %s, not %s' % (path, pid, ryi18n.comment_hash(p), old))
		head = s[:p['start']]
		pos = head.rfind('// HASH_VALUE ' + old)
		if pos < 0 or pid in head[pos:]:
			ryi18n.fail('%s: cannot place the hash comment of %s' % (path, pid))
		s = head[:pos] + '// HASH_VALUE ' + new + head[pos + len('// HASH_VALUE ') + 16:] + s[p['start']:]
		if ryi18n.comment_hash(find(s, pid, path)) != new:
			ryi18n.fail('%s: check failed' % path)
		ryi18n.write_text(path, s, bom)
		print(path, pid, old, '->', new)
elif cmd == 'hash' and len(sys.argv) == 4:
	s, bom = ryi18n.read_text(sys.argv[2])
	p = find(s, sys.argv[3], sys.argv[2])
	print('computed', ryi18n.phrase_hash(p), 'stored', ryi18n.comment_hash(p))
else:
	ryi18n.fail(__doc__)
