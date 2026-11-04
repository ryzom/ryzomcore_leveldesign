"""ammo_scan.py LEVELDESIGN_ROOT [--cap BULK] [--fix] : craft tasks whose crafted items weigh more bag bulk than BULK.

Item bulk comes from the sitem sheets (through PARENT sheets), the number built per craft from the plan bricks
('Nb built items'), so a craft step for N items builds ceil(N / per craft) * per craft of them. With --fix the
quantity of every heavy item (bulk >= 1) in the craft, give_item and mission_desc lines is lowered to the largest
multiple of its per-craft count, all heavy items of a step by the same factor, so that the step's bulk stays within
the cap with its light items counted as they are."""
import sys, os, re, math, collections

root = sys.argv[1]
cap = float(sys.argv[sys.argv.index('--cap') + 1]) if '--cap' in sys.argv else 300.0
fix = '--fix' in sys.argv
ge = os.path.join(root, 'game_element')
prim = os.path.join(root, 'primitives')

sitems = {}
for dp, dn, fn in os.walk(os.path.join(ge, 'sitem')):
	for f in fn:
		if f.endswith('.sitem'):
			sitems.setdefault(f.lower(), os.path.join(dp, f))


def atom(name, key, depth=0):
	p = sitems.get(name.lower() if name.endswith('.sitem') else name.lower() + '.sitem')
	if not p or depth > 20:
		return None
	head = open(p, 'rb').read().decode('utf-8', 'replace').split('<LOG>')[0]
	m = re.search(r'<ATOM Name="%s" Value="([^"]*)"' % key, head)
	if m:
		return m.group(1)
	for pm in re.finditer(r'<PARENT Filename="([^"]*)"', head):
		r = atom(pm.group(1), key, depth + 1)
		if r is not None:
			return r
	return None


per_craft = {}
for dp, dn, fn in os.walk(os.path.join(ge, 'sbrick')):
	for f in fn:
		if f.endswith('.sbrick'):
			s = open(os.path.join(dp, f), 'rb').read().decode('utf-8', 'replace')
			m = re.search(r'<ATOM Name="Crafted Item" Value="([^"]*)"/>\s*<ATOM Name="Nb built items" Value="(\d+)"', s)
			if m:
				per_craft[m.group(1).lower().replace('.sitem', '')] = int(m.group(2))

CRAFT = re.compile(r'^(\s*<STRING>\s*craft\s*:\s*)(.*?)(\s*</STRING>)$')
hits = 0
changed = collections.Counter()
for dp, dn, fn in os.walk(prim):
	if '_unpublished_' in dp:
		continue
	for f in sorted(fn):
		if not (f.startswith('task_') and f.endswith('.primitive')):
			continue
		path = os.path.join(dp, f)
		lines = open(path, 'rb').read().decode('utf-8').split('\n')
		dirty = False
		for i, l in enumerate(lines):
			m = CRAFT.match(l)
			if not m:
				continue
			items = []
			for part in m.group(2).split(';'):
				w = part.split()
				if len(w) == 3:
					items.append((w[0], int(w[1]), w[2]))
			info = []
			for it, q, ql in items:
				b = float(atom(it, 'Bulk') or 0)
				pc = per_craft.get(it.lower(), 1)
				info.append((it, q, ql, b, pc))
			total = sum(math.ceil(q / pc) * pc * b for it, q, ql, b, pc in info)
			if total <= cap or not any(b >= 1 for _, _, _, b, _ in info):
				continue
			hits += 1
			light = sum(math.ceil(q / pc) * pc * b for it, q, ql, b, pc in info if b < 1)
			heavy = [x for x in info if x[3] >= 1]
			room = cap - light
			# one factor for all heavy items of the step, the largest that fits
			def scaled(fac):
				return {it: (q, max(pc, int(q * fac // pc) * pc)) for it, q, ql, b, pc in heavy}

			def bulk_of(sc):
				return sum(math.ceil(sc[it][1] / pc) * pc * b for it, q, ql, b, pc in heavy)
			lo, hi = 0.0, 1.0
			for _ in range(60):
				mid = (lo + hi) / 2
				if bulk_of(scaled(mid)) <= room:
					lo = mid
				else:
					hi = mid
			new = scaled(lo)
			newtotal = light + sum(math.ceil(nq / pc) * pc * b for (it, (q, nq)), (_, _, _, b, pc) in zip(new.items(), heavy))
			print('%s:%d\t%s\tbulk %g -> %g' % (os.path.relpath(path, prim).replace(os.sep, '/'), i + 1,
				'; '.join('%s %d->%d' % (it, q, nq) for it, (q, nq) in new.items()), total, newtotal))
			if fix:
				# craft line, then give_item and mission_desc of the same mission script property
				st = i
				while st > 0 and '<NAME>script</NAME>' not in lines[st]:
					st -= 1
				en = i
				while lines[en].strip() != '</PROPERTY>':
					en += 1
				for j in range(st, en):
					t = lines[j]
					for it, (q, nq) in new.items():
						if not re.search(r'<STRING>\s*(craft|give_item|mission_desc)\b', t):
							continue
						if re.search(r'<STRING>\s*mission_desc\b', t):
							t2 = re.sub(r'(;\s*%s;\s*)%d(;)' % (re.escape(it), q), r'\g<1>%d\2' % nq, t)
						else:
							t2 = re.sub(r'(\b%s\s+)%d(\s)' % (re.escape(it), q), r'\g<1>%d\2' % nq, t)
						if t2 != t:
							changed[re.search(r'<STRING>\s*(\w+)', t).group(1)] += 1
							t = t2
					lines[j] = t
				dirty = True
		if dirty:
			open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('craft steps over %g bulk: %d' % (cap, hits), dict(changed))
