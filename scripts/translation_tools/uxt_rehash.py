"""uxt_rehash.py KEY OLDHASH NEWHASH FILE... : replaces the HASH_VALUE comment of KEY, which must be OLDHASH, in
each .uxt or clause_*.txt FILE. The hash of a work text is printed by
python -c "import ryi18n; print(ryi18n.make_hash('text'))"."""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ryi18n
from uxt import parse_uxt_string

if len(sys.argv) < 5:
	ryi18n.fail(__doc__)
key, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
for path in sys.argv[4:]:
	s, bom = ryi18n.read_text(path)
	ents, _ = parse_uxt_string(s)
	if key not in ents:
		ryi18n.fail('%s: no key %s' % (path, key))
	e = ents[key]
	if e['hash'] != old:
		ryi18n.fail('%s: %s has hash %s, not %s' % (path, key, e['hash'], old))
	head = s[:e['start']]
	pos = head.rfind('// HASH_VALUE ' + old)
	if pos < 0 or '\n' + key in head[pos:]:
		ryi18n.fail('%s: cannot place the hash comment of %s' % (path, key))
	s = head[:pos] + '// HASH_VALUE ' + new + head[pos + len('// HASH_VALUE ') + 16:] + s[e['start']:]
	if parse_uxt_string(s)[0][key]['hash'] != new:
		ryi18n.fail('%s: check failed' % path)
	ryi18n.write_text(path, s, bom)
	print(path, key, old, '->', new)
