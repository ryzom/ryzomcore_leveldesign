"""uxt_set.py FILE VALUES.tsv : sets the texts of existing keys of a .uxt or clause_*.txt file.

VALUES.tsv rows are key<TAB>text; a literal backslash-n in the text is the newline escape, and the file gets it
as a backslash-n followed by a line break and a tab, the layout of the translated files. Hashes, indexes and
comments are kept. Texts with brackets or other backslashes are refused. The result is checked before the file
is written."""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ryi18n
from uxt import parse_uxt_string

BS = chr(92)
ESC_N = BS + 'n'

if len(sys.argv) != 3:
	ryi18n.fail(__doc__)
path, tsv = sys.argv[1], sys.argv[2]
vals = []
for line in open(tsv, encoding='utf-8'):
	line = line.rstrip('\r\n')
	if not line:
		continue
	if '\t' not in line:
		ryi18n.fail('no tab in TSV row: %r' % line)
	k, t = line.split('\t', 1)
	vals.append((k, t))
s, bom = ryi18n.read_text(path)
ents, order = parse_uxt_string(s)
edits = []
seen = set()
for k, t in vals:
	if k not in ents:
		ryi18n.fail('unknown key ' + k)
	if k in seen:
		ryi18n.fail('key twice in the TSV: ' + k)
	seen.add(k)
	body = t.replace(ESC_N, '\x00')
	if '[' in body or ']' in body or BS in body:
		ryi18n.fail('brackets or backslashes in the text of ' + k)
	body = body.replace('\x00', ESC_N + '\n\t')
	e = ents[k]
	edits.append((e['start'], e['end'], k + '\t[' + body + ']'))
for st, en, new in sorted(edits, reverse=True):
	s = s[:st] + new + s[en:]
chk, chk_order = parse_uxt_string(s)
if chk_order != order:
	ryi18n.fail('key order changed')
for k, t in vals:
	if chk[k]['text'] != t.replace(ESC_N, '\n') or chk[k]['hash'] != ents[k]['hash']:
		ryi18n.fail('check failed for ' + k)
ryi18n.write_text(path, s, bom)
print('set', len(vals), 'keys in', path)
