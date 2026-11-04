"""race_check.py LEVELDESIGN_ROOT [--races] : kill_race/target_race steps whose race never spawns in the step's region.

Races come from the creature sheets (Basics.Race, resolved through PARENT sheets, mapped to the CPeople strings by
DFN/game_elem/_creature/_creature_race.typ). A region's spawns are the creature_code values of every primitive in the
region's folder (primitives/<continent>/<region>/); region_<name> maps to folder <name>."""
import sys, os, re, html, collections

root = sys.argv[1]
prim = os.path.join(root, 'primitives')

# race labels
typ = open(os.path.join(root, 'DFN/game_elem/_creature/_creature_race.typ'), 'rb').read().decode('utf-8', 'replace')
label2race = {m.group(1).lower(): m.group(2) for m in re.finditer(r'<DEFINITION Label="([^"]*)" Value="([^"]*)"', typ)}

# creature sheets by name
sheets = {}
for dp, dn, fn in os.walk(os.path.join(root, 'game_elem')):
	for f in fn:
		if f.endswith('.creature'):
			sheets.setdefault(f.lower(), os.path.join(dp, f))
cache = {}


def race_of(name, depth=0):
	name = name.lower()
	if not name.endswith('.creature'):
		name += '.creature'
	if name in cache:
		return cache[name]
	cache[name] = None
	p = sheets.get(name)
	if not p or depth > 20:
		return None
	s = open(p, 'rb').read().decode('utf-8', 'replace')
	head = s.split('<LOG>')[0]
	m = re.search(r'<ATOM Name="Race" Value="([^"]*)"', head)
	r = None
	if m:
		r = label2race.get(m.group(1).lower(), m.group(1))
	else:
		for pm in re.finditer(r'<PARENT Filename="([^"]*)"', head):
			r = race_of(pm.group(1), depth + 1)
			if r:
				break
	cache[name] = r
	return r


# region folders and their spawned races
region_dirs = {}
for cont in os.listdir(prim):
	cd = os.path.join(prim, cont)
	if not os.path.isdir(cd) or cont.startswith('_'):
		continue
	for reg in os.listdir(cd):
		if os.path.isdir(os.path.join(cd, reg)):
			region_dirs.setdefault(reg.lower(), []).append(os.path.join(cd, reg))
spawns = {}


def region_spawns(reg):
	if reg in spawns:
		return spawns[reg]
	races = collections.defaultdict(set)
	for d in region_dirs.get(reg, []):
		for f in os.listdir(d):
			if not f.endswith('.primitive') or f.startswith('task_'):
				continue
			s = open(os.path.join(d, f), 'rb').read().decode('utf-8', 'replace')
			for m in re.finditer(r'<NAME>(?:creature_code|sheet|sheet_client)</NAME>\s*<STRING>([^<]*)</STRING>', s):
				code = m.group(1).strip()
				r = race_of(code)
				if r:
					races[r.lower()].add(code.lower().replace('.creature', ''))
	spawns[reg] = races
	return races


def level_of(name, depth=0):
	name = name.lower()
	if not name.endswith('.creature'):
		name += '.creature'
	p = sheets.get(name)
	if not p or depth > 20:
		return None
	head = open(p, 'rb').read().decode('utf-8', 'replace').split('<LOG>')[0]
	m = re.search(r'<ATOM Name="XPLevel" Value="([^"]*)"', head)
	if m:
		return m.group(1)
	for pm in re.finditer(r'<PARENT Filename="([^"]*)"', head):
		r = level_of(pm.group(1), depth + 1)
		if r:
			return r
	return None


HUMANOID = set(['fyros', 'matis', 'tryker', 'zorai', 'karavan', 'kami', 'tribe', 'common', 'mektoubmount', 'mektoubpacker'])
if '--races' in sys.argv:
	for reg in sys.argv[sys.argv.index('--races') + 1:]:
		rs = region_spawns(reg)
		print(reg)
		for k, v in sorted(rs.items()):
			if k not in HUMANOID:
				print('  %-14s %s' % (k, ' '.join('%s:%s' % (c, level_of(c)) for c in sorted(v))))
	sys.exit(0)

step = re.compile(r'^(kill_race|target_race)\s*:\s*(.*?)\s*(?::\s*([A-Za-z0-9_]+)\s*)?$')
bad = []
unknown_regions = set()
for dp, dn, fn in os.walk(prim):
	if '_unpublished_' in dp:
		continue
	for f in fn:
		if not f.endswith('.primitive'):
			continue
		path = os.path.join(dp, f)
		s = open(path, 'rb').read().decode('utf-8', 'replace')
		for m in re.finditer(r'<STRING>((?:kill_race|target_race)\s*:[^<]*)</STRING>', s):
			line = html.unescape(m.group(1)).strip()
			mm = step.match(line)
			if not mm:
				continue
			kind, body, place = mm.groups()
			if not place or not place.lower().startswith('region_'):
				continue
			reg = place.lower()[len('region_'):]
			if reg not in region_dirs:
				unknown_regions.add(place)
				continue
			rs = region_spawns(reg)
			for part in body.split(';'):
				w = part.split()
				if not w:
					continue
				race = w[0].lower()
				if race not in rs:
					ln = s.count('\n', 0, m.start()) + 1
					bad.append((os.path.relpath(path, prim).replace(os.sep, '/'), ln, kind, race, place, line))
for b in bad:
	print('%s:%d\t%s\t%s\t%s\t%s' % b)
print('steps with a race that does not spawn in the region:', len(bad))
cnt = collections.Counter((b[3], b[4]) for b in bad)
for (race, place), n in sorted(cnt.items()):
	print('  %-20s %-35s %d' % (race, place, n))
print('regions without a folder:', ' '.join(sorted(unknown_regions)))
