"""dedup_titles.py LEVELDESIGN_ROOT [--fix] : gives every mission of a giver its own title text.

Generated task missions pick a title variant (the 'random' parameter of their TEMPLATE_TASK_*_TITLE line) at
random, so a giver can list two missions under the same title. For each such duplicate the later missions get a
variant this giver does not use yet for that title (same template and same other parameters); the mission_desc
'random' parameter moves along when it was equal to the old title variant."""
import sys, os, re, collections, html
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'translation_tools'))
import ryi18n
import xml.etree.ElementTree as ET

root = sys.argv[1]
fix = '--fix' in sys.argv
prim = os.path.join(root, 'primitives')

# title variants: the (random = N) values, plus one value for the default clause
s = open(os.path.join(root, 'translation/translated/phrase_en.txt'), 'rb').read().decode('utf-8-sig')
variants = {}
for p in ryi18n.parse_phrases(s):
	if re.match(r'TEMPLATE_TASK_.*_TITLE$', p['id']):
		vals = [int(m.group(1)) for m in (re.fullmatch(r'\(random = (\d+)\)', c[0]) for c in p['clauses']) if m]
		dflt = 10 if 10 not in vals else max(vals) + 1
		variants[p['id']] = sorted(vals) + [dflt]


def props(n):
	return {p.findtext('NAME'): [s.text or '' for s in p.findall('STRING')] for p in n.findall('PROPERTY')}


def walk(n, chain, out):
	d = props(n)
	cls = (d.get('class') or [''])[0]
	name = (d.get('name') or [''])[0]
	if cls == 'mission':
		bot = [c for c in chain if c[0] == 'npc_bot']
		if bot:
			out.append((bot[-1][1], name, d.get('script', [])))
	for c in n.findall('CHILD'):
		walk(c, chain + [(cls, name)], out)


TITLE = re.compile(r'^mission_title\s*:\s*(TEMPLATE_TASK_[A-Z0-9_]*_TITLE)\s*((?:;[^;]*)*)$')
changed_total = 0
left = []
for dp, dn, fn in os.walk(prim):
	if '_unpublished_' in dp:
		continue
	for f in sorted(fn):
		if not (f.startswith('task_') and f.endswith('.primitive')):
			continue
		path = os.path.join(dp, f)
		out = []
		walk(ET.parse(path).getroot().find('ROOT_PRIMITIVE'), [], out)
		groups = collections.defaultdict(list)
		for bot, name, script in out:
			for l in script:
				m = TITLE.match(l.strip())
				if m:
					args = [a.strip() for a in m.group(2).split(';')[1:]]
					# the variant is the numeric argument before the faction
					vi = len(args) - 2
					if vi < 0 or not args[vi].isdigit() or m.group(1) not in variants:
						continue
					key = (bot, m.group(1), tuple(a for k, a in enumerate(args) if k != vi))
					groups[key].append((name, int(args[vi]), l, script))
		edits = {}
		for key, ms in groups.items():
			used = collections.Counter(v for _, v, _, _ in ms)
			if max(used.values()) < 2:
				continue
			taken = set(used)
			free = [v for v in variants[key[1]] if v not in taken]
			seen = set()
			for name, v, line, script in ms:
				if v not in seen:
					seen.add(v)
					continue
				if not free:
					left.append((path, key, name))
					continue
				nv = free.pop(0)
				edits[name] = (v, nv)
				print('%s\t%s\t%s\t%s: %d -> %d' % (os.path.relpath(path, prim).replace(os.sep, '/'), key[0].split('$')[0], key[1], name, v, nv))
		if fix and edits:
			lines = open(path, 'rb').read().decode('utf-8').split('\n')
			for name, (ov, nv) in edits.items():
				st = [i for i, l in enumerate(lines) if l.strip() == '<STRING>#%s</STRING>' % name]
				assert len(st) == 1, (path, name)
				en = st[0]
				while lines[en].strip() != '</PROPERTY>':
					en += 1
				done = 0
				for i in range(st[0], en):
					t = html.unescape(re.sub(r'^\s*<STRING>|</STRING>\s*$', '', lines[i]))
					for kw in ('mission_title', 'mission_desc'):
						if t.startswith(kw):
							parts = t.split(';')
							k = len(parts) - 2
							if parts[k].strip() == str(ov):
								parts[k] = parts[k].replace(str(ov), str(nv))
								lines[i] = lines[i].replace(';'.join(t.split(';')[k:]), ';'.join(parts[k:]))
								assert html.unescape(re.sub(r'^\s*<STRING>|</STRING>\s*$', '', lines[i])) == ';'.join(parts), lines[i]
								done += 1
							elif kw == 'mission_title':
								raise AssertionError((path, name, t))
				assert done >= 1
			open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
		changed_total += len(edits)
print('retitled', changed_total, 'left', len(left))
for l in left:
	print('LEFT', l)
