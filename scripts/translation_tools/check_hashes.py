"""check_hashes.py TRANSLATIONDIR [-v] : translation status against the work texts.

For every translated phrase_<lang>.txt, <lang>.uxt, r2_<lang>.uxt and *_words_<lang>.txt, counts the entries
whose stored HASH_VALUE equals the hash of the work text (up to date), the ones that differ (the work text
changed since, so the translation tools offer them for retranslation), and the ones the work files do not have.
The work texts are translation/work/phrase_wk.txt with its #include files, work/*.uxt and work/*_words_wk.txt.
-v lists the ids that are not up to date."""
import sys, os, re, glob
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ryi18n
from uxt import parse_uxt, parse_uxt_string

if len(sys.argv) < 2:
	ryi18n.fail(__doc__)
root = sys.argv[1]
verbose = '-v' in sys.argv
work = os.path.join(root, 'work')
tr = os.path.join(root, 'translated')


def report(name, stored, wanted):
	up = stale = extra = 0
	bad = []
	for k, h in stored.items():
		if k not in wanted:
			extra += 1
			bad.append('not in work: ' + k)
		elif h == wanted[k]:
			up += 1
		else:
			stale += 1
			bad.append('changed: ' + k)
	missing = len([k for k in wanted if k not in stored])
	print('%-28s up to date %6d   changed %5d   not in work %4d   missing %4d' % (name, up, stale, extra, missing))
	if verbose:
		for b in bad:
			print('    ' + b)


# phrases
wk = {p['id']: ryi18n.phrase_hash(p) for p in ryi18n.parse_phrases(ryi18n.read_with_includes(os.path.join(work, 'phrase_wk.txt')))}
for f in sorted(glob.glob(os.path.join(tr, 'phrase_*.txt'))):
	ps = ryi18n.parse_phrases(ryi18n.read_text(f)[0])
	report(os.path.basename(f), {p['id']: ryi18n.comment_hash(p) for p in ps}, wk)

# uxt
for wf in sorted(glob.glob(os.path.join(work, '*.uxt'))):
	base = os.path.basename(wf)[:-len('wk.uxt')]
	ents, _ = parse_uxt(wf)
	wanted = {k: ryi18n.make_hash(e['text']) for k, e in ents.items()}
	for f in sorted(glob.glob(os.path.join(tr, base + '*.uxt'))):
		lang = os.path.basename(f)[len(base):-4]
		if '_' in lang:
			continue
		got, _ = parse_uxt(f)
		report(os.path.basename(f), {k: e['hash'] for k, e in got.items()}, wanted)

# words
for wf in sorted(glob.glob(os.path.join(work, '*_words_wk.txt'))):
	base = os.path.basename(wf)[:-len('wk.txt')]
	h, rows = ryi18n.words_rows(wf)
	wanted = {r[0]: ryi18n.words_hash(h, r) for r in rows if r and r[0]}
	for f in sorted(glob.glob(os.path.join(tr, base + '*.txt'))):
		th, trows = ryi18n.words_rows(f)
		if not th or th[0] != '*HASH_VALUE':
			continue
		report(os.path.basename(f), {r[1]: r[0].lstrip('_') for r in trows if len(r) > 1 and r[1]}, wanted)
