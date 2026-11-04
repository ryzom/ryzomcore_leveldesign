"""dup_titles.py PRIMITIVES_DIR : givers whose mission list shows the same title twice.

A title is the phrase id plus every parameter of the mission_title line (region, variant, faction), so two
missions of one giver with the same mission_title line print the same text."""
import sys, os, re, collections, xml.etree.ElementTree as ET

root = sys.argv[1]


def props(n):
	return {p.findtext('NAME'): [s.text or '' for s in p.findall('STRING')] for p in n.findall('PROPERTY')}


def walk(n, chain, out):
	d = props(n)
	cls = (d.get('class') or [''])[0]
	name = (d.get('name') or [''])[0]
	if cls == 'mission':
		sc = d.get('script', [])
		t = [l for l in sc if l.startswith('mission_title')]
		bot = [c for c in chain if c[0] == 'npc_bot']
		if t and bot:
			out.append((bot[-1][1], name, re.sub(r'\s+', ' ', t[0].split(':', 1)[1]).strip()))
	for c in n.findall('CHILD'):
		walk(c, chain + [(cls, name)], out)


total = 0
for dp, dn, fn in os.walk(root):
	if '_unpublished_' in dp:
		continue
	for f in sorted(fn):
		if not (f.startswith('task_') and f.endswith('.primitive')):
			continue
		path = os.path.join(dp, f)
		r = ET.parse(path).getroot()
		out = []
		walk(r.find('ROOT_PRIMITIVE'), [], out)
		by = collections.defaultdict(list)
		for bot, name, title in out:
			by[(bot, title.replace(' ;', ';').replace('; ', ';'))].append(name)
		for (bot, title), names in sorted(by.items()):
			if len(names) > 1:
				total += 1
				print('%s\t%s\t%s\t%s' % (os.path.relpath(path, root).replace(os.sep, '/'), bot.split('$')[0], title, ' '.join(names)))
print('duplicate titles:', total)
