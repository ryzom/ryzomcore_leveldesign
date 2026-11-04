"""uxt_tokens.py TRANSLATEDDIR LANG KEYS.tsv [--fix-trailing OUT.tsv] : compares placeholders, colour codes,
newlines and trailing spaces of the listed keys (first TSV column) between en.uxt and LANG.uxt. With
--fix-trailing, writes the texts with the trailing spaces of en to OUT.tsv, for uxt_set.py."""
import sys, os, re
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uxt import parse_uxt

tr, lang, tsv = sys.argv[1], sys.argv[2], sys.argv[3]
fix = sys.argv[sys.argv.index('--fix-trailing') + 1] if '--fix-trailing' in sys.argv else None
en, _ = parse_uxt(os.path.join(tr, 'en.uxt'))
lo, _ = parse_uxt(os.path.join(tr, lang + '.uxt'))
keys = [l.rstrip('\r\n').split('\t', 1)[0] for l in open(tsv, encoding='utf-8') if l.strip()]
tok = re.compile(r'@\{[0-9A-Fa-fT]+\}|%[a-z_0-9]+|&[A-Z]+&|\{[a-z]+\}')
bad = 0
fixes = []
for k in keys:
	a = en[k]['text']
	b = lo[k]['text']
	ta = sorted(t for t in tok.findall(a) if not t.startswith('@{'))
	tb = sorted(t for t in tok.findall(b) if not t.startswith('@{'))
	if ta != tb:
		print('TOKENS', k, ta, tb)
		bad += 1
	ca = [t for t in tok.findall(a) if t.startswith('@{')]
	cb = [t for t in tok.findall(b) if t.startswith('@{')]
	if sorted(set(ca)) != sorted(set(cb)):
		print('COLORS', k, ca, cb)
		bad += 1
	if a.count('\n') != b.count('\n'):
		print('NEWLINES', k, a.count('\n'), b.count('\n'))
		bad += 1
	ea = len(a) - len(a.rstrip(' '))
	eb = len(b) - len(b.rstrip(' '))
	if ea != eb:
		print('TRAILING', k, repr(a[-3:]), repr(b[-3:]))
		fixes.append((k, b.rstrip(' ') + ' ' * ea))
print('problems', bad, 'trailing', len(fixes))
if fix and fixes:
	out = fix
	with open(out, 'w', encoding='utf-8', newline='\n') as f:
		for k, t in fixes:
			f.write(k + '\t' + t.replace('\n', chr(92) + 'n') + '\n')
	print('wrote', out)
