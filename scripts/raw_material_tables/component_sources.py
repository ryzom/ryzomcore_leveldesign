# What serves each component type of a craft plan, read from what mp_generator wrote: the raw material sheets
# (game_element/sitem/raw_material) and the quartering tables of the creatures (_<creature>_mp.creature). Writes
# component_sources.tsv (one line per material sheet and component type it serves) and the generated part of the
# interface section of README.md, and checks that every creature material is quartered from some creature and every
# quartered material exists.
#
#   python component_sources.py

import collections, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELDESIGN = os.path.normpath(os.path.join(HERE, "..", ".."))
MATERIALS = os.path.join(LEVELDESIGN, "game_element", "sitem", "raw_material")
CREATURES = os.path.join(LEVELDESIGN, "game_elem", "creature")
WORDS = os.path.join(LEVELDESIGN, "translation", "work", "item_words_wk.txt")

TYPES = [ ( "A", "MpL", "Blade" ), ( "B", "MpH", "Hammer" ), ( "C", "MpP", "Point" ), ( "D", "MpM", "Shaft" ), ( "E", "MpG", "Grip" ),
	( "F", "MpC", "Counterweight" ), ( "G", "MpGA", "Trigger" ), ( "H", "MpPE", "Firing pin" ), ( "I", "MpCA", "Barrel" ),
	( "J", "MpE", "Explosive" ), ( "K", "MpEN", "Ammo jacket" ), ( "L", "MpPR", "Ammo bullet" ), ( "M", "MpCR", "Armor shell" ),
	( "N", "MpRI", "Lining" ), ( "O", "MpRE", "Stuffing" ), ( "P", "MpAT", "Armor clip" ), ( "Q", "MpSU", "Jewel setting" ),
	( "R", "MpED", "Jewel" ), ( "S", "MpBT", "Blacksmith tool" ), ( "T", "MpPES", "Pestle tool" ), ( "U", "MpSH", "Sharpener tool" ),
	( "V", "MpTK", "Tunneling knife" ), ( "W", "MpJH", "Jewelry hammer" ), ( "X", "MpCF", "Campfire" ), ( "Y", "MpVE", "Clothes" ),
	( "Z", "MpMF", "Magic focus" ) ]
CLASSES = [ ( "a", "Basic" ), ( "b", "Fine" ), ( "c", "Choice" ), ( "d", "Excellent" ), ( "e", "Supreme" ) ]
ECOSYSTEMS = { "c": "common", "d": "desert", "f": "forest", "j": "jungle", "l": "lakes", "p": "prime roots" }
DEPOSIT_CLASSES = { "b": "Basic", "c": "Fine", "d": "Choice", "e": "Excellent", "f": "Supreme" }
# The deposit families made as special items (make_tables.py SPECIALS): the kitin lairs' larva
SPECIAL_DEPOSITS = [ "Kitin Larva" ]

errors = []

def readForm(path):
	with open(path, "r", encoding="utf-8", errors="replace") as f:
		text = f.read()
	return text, re.findall(r'<PARENT Filename="([^"]+)"', text), dict(re.findall(r'<ATOM Name="([^"]+)" Value="([^"]*)"', text))

def main():
	# the families and groups of the parents
	parents = {}
	for f in os.listdir(os.path.join(MATERIALS, "_parent")):
		parents[f.lower()] = readForm(os.path.join(MATERIALS, "_parent", f))[2]

	# the material sheets: family, group, parts and the best stat of each, class, ecosystem, energy, max quality
	sheets = {}
	for folder in os.listdir(MATERIALS):
		path = os.path.join(MATERIALS, folder)
		if folder == "_parent" or not os.path.isdir(path):
			continue
		for f in os.listdir(path):
			m = re.match(r"^m(\d{4})([a-z]{3})([a-z])([a-z])(\d\d)\.sitem$", f)
			if not m:
				continue
			text, sheetParents, atoms = readForm(os.path.join(path, f))
			merged = {}
			for p in sheetParents:
				merged.update(parents.get(p.lower(), {}))
			merged.update(atoms)
			parts = {}
			for letter, body in re.findall(r'<STRUCT Name="([A-Z]) Mp[A-Za-z]+ \([^"]*\)">(.*?)</STRUCT>', text, re.S):
				stats = { k: int(v) for k, v in re.findall(r'<ATOM Name="([^"]+)" Value="(\d+)"', body) }
				best = max(stats.items(), key=lambda kv: kv[1])
				parts[letter] = ( best[0] if list(stats.values()).count(best[1]) == 1 else "", stats )
			sheets[f[:-6]] = { "family": merged.get("Family", "?"), "group": merged.get("Group", "?"), "code": m.group(2),
				"eco": m.group(3), "class": m.group(4), "parts": parts, "energy": int(merged.get("StatEnergy", "0")),
				"maxQuality": int(merged.get("MaxQuality", "0")) }

	# the quartering tables: which creature gives which material, at which quality
	givers = collections.defaultdict(list) # sheet: [ ( creature, quality ) ]
	for root, dirs, files in os.walk(CREATURES):
		for f in files:
			m = re.match(r"^_(c[a-z]{2}[a-z][a-j][1-8])_mp\.creature$", f)
			if not m:
				continue
			with open(os.path.join(root, f), "r", encoding="utf-8", errors="replace") as fh:
				text = fh.read()
			for entry in re.findall(r'<STRUCT Name="MP\d+">(.*?)</STRUCT>', text, re.S):
				item = re.search(r'Name="AssociatedItem" Value="([^"]+)\.sitem"', entry)
				quality = re.search(r'Name="MaxQuality" Value="(\d+)"', entry)
				if not item or item.group(1).startswith("system_mp"):
					continue
				if item.group(1) not in sheets:
					errors.append(m.group(1) + " quarters " + item.group(1) + ", which is no raw material sheet")
					continue
				if sheets[item.group(1)]["parts"] and not quality:
					errors.append(m.group(1) + " quarters " + item.group(1) + " with no quality")
					continue
				givers[item.group(1)].append(( m.group(1), int(quality.group(1)) if quality else 0 ))

	# every creature craft material is quartered from some creature, and its stats add up to its class
	for name, s in sorted(sheets.items()):
		if s["code"] not in ( "dxa", "cxx", "ixx" ) and not givers.get(name):
			errors.append(name + " (" + s["family"] + ") is quartered from no creature")
		for letter, ( best, stats ) in s["parts"].items():
			# the total of a part is its class's, but for the floor of 1 the tool keeps a weak durability at (Basic)
			total = sum(stats.values())
			expected = s["energy"] * len(stats) + (1 if s["energy"] == 20 and stats.get("Durability") == 1 else 0)
			if total != expected:
				errors.append("%s, part %s: its stats add up to %d, its class to %d" % (name, letter, total, expected))

	words = set()
	with open(WORDS, "r", encoding="utf-8-sig") as f:
		for line in f:
			words.add(line.split("\t")[0])
	for name in sheets:
		if name not in words:
			errors.append(name + " has no name in item_words_wk.txt")

	# ---- component_sources.tsv
	lines = [ "\t".join([ "Type", "Component", "Source", "Family", "Group", "Class", "Ecosystem", "Sheet", "Quality", "Best stat", "Creatures" ]) ]
	summary = collections.defaultdict(lambda: collections.defaultdict(lambda: { "deposit": set(), "creature": [], "families": set() }))
	kinds = collections.defaultdict(lambda: collections.defaultdict(set))
	for name, s in sorted(sheets.items(), key=lambda kv: ( kv[0][5:8] != "dxa", kv[1]["family"], kv[0] )):
		for letter, ( best, stats ) in sorted(s["parts"].items()):
			t = [ t for t in TYPES if t[0] == letter ][0]
			if s["code"] == "dxa" and s["family"] in SPECIAL_DEPOSITS:
				# a special item of its family, not one of the deposit classes
				source = "kitin lair"
				cls = DEPOSIT_CLASSES.get(s["class"], "?")
				quality = "1-%d" % s["maxQuality"]
				who = ""
			elif s["code"] == "dxa":
				source = "deposit"
				cls = DEPOSIT_CLASSES.get(s["class"], "?")
				quality = "1-%d" % s["maxQuality"]
				who = ""
				summary[letter][cls]["deposit"].add(( ECOSYSTEMS.get(s["eco"], s["eco"]), s["maxQuality"] ))
				kinds[letter]["deposit"].add(s["group"])
			else:
				source = "creature"
				cls = dict(CLASSES).get(s["class"], "?")
				qualities = [ q for c, q in givers.get(name, []) ]
				quality = ("%d-%d" % (min(qualities), max(qualities))) if qualities else ""
				who = str(len(set(c for c, q in givers.get(name, []))))
				summary[letter][cls]["creature"] += qualities
				summary[letter][cls]["families"].add(s["family"])
				kinds[letter]["creature"].add(s["family"].split(" ", 1)[1])
			lines.append("\t".join([ letter + " " + t[1], t[2], source, s["family"], s["group"], cls, ECOSYSTEMS.get(s["eco"], s["eco"]),
				name, quality, best, who ]))
	with open(os.path.join(HERE, "component_sources.tsv"), "w", encoding="utf-8", newline="\n") as f:
		f.write("\n".join(lines) + "\n")

	# ---- the generated part of the README interface
	out = [ "| Type | Name | Basic | Fine | Choice | Excellent | Supreme |", "| --- | --- | --- | --- | --- | --- | --- |" ]
	for letter, code, label in TYPES:
		if letter in "STUVWX":
			continue
		cells = []
		for cls in ( "Basic", "Fine", "Choice", "Excellent", "Supreme" ):
			e = summary[letter][cls]
			parts = []
			if e["deposit"]:
				ecos = sorted(set(x[0] for x in e["deposit"]))
				parts.append("deposits q%d (%s)" % (max(x[1] for x in e["deposit"]), ", ".join(ecos)))
			if e["creature"]:
				parts.append("%d creature families q%d-%d" % (len(e["families"]), min(e["creature"]), max(e["creature"])))
			cells.append("; ".join(parts) or "none")
		out.append("| %s %s | %s | %s |" % (letter, code, label, " | ".join(cells)))
	readme = os.path.join(HERE, "README.md")
	with open(readme, "r", encoding="utf-8") as f:
		text = f.read()
	start, end = "<!-- generated by component_sources.py -->", "<!-- end of the generated part -->"
	if start not in text or end not in text:
		errors.append("README.md has no generated part between '" + start + "' and '" + end + "'")
	else:
		text = text[:text.index(start) + len(start)] + "\n" + "\n".join(out) + "\n" + text[text.index(end):]
		with open(readme, "w", encoding="utf-8", newline="\n") as f:
			f.write(text)

	counts = collections.Counter("deposit" if s["code"] == "dxa" else "creature" if s["code"] not in ( "cxx", "ixx" ) else "other" for s in sheets.values())
	print("%d raw material sheets (%s), %d of them quartered from creatures" % (len(sheets), ", ".join("%d %s" % (v, k) for k, v in sorted(counts.items())), len(givers)))
	if errors:
		for e in errors[:50]:
			print("ERROR: " + e, file=sys.stderr)
		print("%d errors" % len(errors), file=sys.stderr)
		sys.exit(1)

if __name__ == "__main__":
	main()
