"""mission_givers.py FILE.primitive... : per mission, its enclosing bot and kill/target race steps."""
import sys, re, xml.etree.ElementTree as ET


def props(n):
	d = {}
	for p in n.findall('PROPERTY'):
		d[p.findtext('NAME')] = [s.text or '' for s in p.findall('STRING')]
	return d


def walk(n, chain, out):
	d = props(n)
	cls = (d.get('class') or [''])[0]
	name = (d.get('name') or [''])[0]
	if cls == 'mission':
		script = d.get('script', [])
		steps = [l for l in script if re.match(r'\s*(kill_race|target_race)\s*:', l)]
		title = [l for l in script if l.startswith('mission_title')]
		bot = [c for c in chain if c[0] in ('npc_bot', 'npc_group')]
		out.append((bot[-1][1] if bot else '?', name, title[0] if title else '', steps))
	for c in n.findall('CHILD'):
		walk(c, chain + [(cls, name)], out)


for f in sys.argv[1:]:
	out = []
	r = ET.parse(f).getroot()
	walk(r.find('ROOT_PRIMITIVE') if r.find('ROOT_PRIMITIVE') is not None else r, [], out)
	print('==', f)
	cur = None
	for bot, name, title, steps in out:
		if not steps:
			continue
		if bot != cur:
			print(' ', bot)
			cur = bot
		print('    %-16s %-60s %s' % (name, title[15:75], ' | '.join(s.strip() for s in steps)))
