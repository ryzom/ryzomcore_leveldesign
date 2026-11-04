"""craft_titles.py PRIMITIVES_DIR [--fix] : craft tasks whose nation title (TEMPLATE_TASK_CRAFT_11..14_TITLE: Matis,
Zorai, Fyros, Tryker) does not match the nation of the crafted items (icm, icz, icf, ict)."""
import sys, os, re

root = sys.argv[1]
fix = '--fix' in sys.argv
NATION = {'11': 'm', '12': 'z', '13': 'f', '14': 't'}
BY_LETTER = {v: k for k, v in NATION.items()}
total = 0
for dp, dn, fn in os.walk(root):
	if '_unpublished_' in dp:
		continue
	for f in fn:
		if not f.startswith('task_') or not f.endswith('.primitive'):
			continue
		path = os.path.join(dp, f)
		lines = open(path, 'rb').read().decode('utf-8').split('\n')
		changed = False
		i = 0
		while i < len(lines):
			m = re.match(r'^(\s*)<STRING>mission_title : TEMPLATE_TASK_CRAFT_(1[1-4])_TITLE(;.*)</STRING>$', lines[i])
			if m:
				# the craft step of the same script
				j = i
				items = []
				while j < len(lines) and lines[j].strip() != '</PROPERTY>':
					c = re.match(r'^\s*<STRING>craft\s*:\s*(.*)</STRING>$', lines[j])
					if c:
						items = re.findall(r'\b(ic[a-z])[a-z0-9_]*', c.group(1))
					j += 1
				letters = set(x[2] for x in items)
				if len(letters) == 1 and NATION[m.group(2)] not in letters:
					want = BY_LETTER.get(letters.pop())
					total += 1
					print('%s:%d\t_%s_ -> _%s_\t%s' % (os.path.relpath(path, root).replace(os.sep, '/'), i + 1, m.group(2), want, ' '.join(items)))
					if fix and want:
						lines[i] = lines[i].replace('TEMPLATE_TASK_CRAFT_%s_TITLE' % m.group(2), 'TEMPLATE_TASK_CRAFT_%s_TITLE' % want)
						changed = True
			i += 1
		if changed:
			open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('mismatches', total)
