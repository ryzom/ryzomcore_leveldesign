# The sheet generator of Ryzom Core: the bricks (.sbrick) and phrases (.sphrase) of every action come from here.
#
# The list of what exists is the translation: every sheet is named by its id in translation/work/<type>_words_wk.txt,
# so the CC BY-SA texts apply as they are. What a brick can do is fixed by the code (code_tables.py, refreshed from it):
# the families, the property keywords and their arguments, the skills, the grammar and cost check of a phrase. The
# domains (domains/*.py) choose levels, values, prices and gates from balancing_core4.py.
#
# A domain owns folders of game_element: a sheet there that the run does not make is removed when it writes. Every
# check runs before anything is written, and a failed one stops the run without writing.

import collections, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import code_tables as CT

LEVELDESIGN = os.path.normpath(os.path.join(HERE, "..", ".."))
GAME_ELEMENT = os.path.join(LEVELDESIGN, "game_element")
TRANSLATION = os.path.join(LEVELDESIGN, "translation")
# the folders the sheet ids are made from (build_gamedata, process sheet_id): a sheet name must be unique across them
SHEET_ID_FOLDERS = [ os.path.join(LEVELDESIGN, "game_elem"), GAME_ELEMENT, os.path.join(LEVELDESIGN, "world") ]
# what a sheet name (a parent starts with _) and a folder under game_element may hold: they are joined into paths
SHEET_NAME = re.compile(r"_?[a-z0-9][a-z0-9_]*")
FOLDER_NAME = re.compile(r"[a-z0-9_]+")
# names Windows keeps for devices, whatever their extension (both patterns are matched whole, with fullmatch)
RESERVED_NAMES = set(["con", "prn", "aux", "nul"] + [ "com%d" % i for i in range(1, 10) ] + [ "lpt%d" % i for i in range(1, 10) ])

def isFileName(pattern, name):
	return pattern.fullmatch(name) is not None and name not in RESERVED_NAMES
# a sheet is written beside its target under this suffix, then renamed over it
TEMPORARY_SUFFIX = ".generating"

def deleteTemporaries(paths, done):
	"""delete the temporary files that exist of these, each removal guarded so that the stop or interruption being
	handled is the one reported: done when all went, or which could not be deleted"""
	left = []
	for path in paths:
		try:
			if os.path.exists(path):
				os.remove(path)
		except OSError:
			left.append(path)
	return done if not left else "these temporary files could not be deleted, remove them: " + ", ".join(left)

# keywords only the client reads (sbrick_manager.cpp compiles every KEY: it finds), which the server skips
CLIENT_ONLY_KEYWORDS = { "fplan", "info", "bhfeca_tag" }

# the sheets the code names directly (survey_format_client.md 2.8, survey_server.md 10.7): checked with --complete
REQUIRED_BRICKS = [ "bfpa01", "bcpa01", "bhq01", "bapa01", "bapa02", "bapa03", "bapa04", "bapa05", "big_equip_item",
	"big_remove", "hatred", "shoot_again", "bsxea11", "mezz", "mod_defense", "mod_dodge", "mod_parry",
	"enchant_weapon", "enchant_weapon_rot", "enchant_weapon_acid", "enchant_weapon_cold", "enchant_weapon_fire",
	"enchant_weapon_poison", "enchant_weapon_electricity", "enchant_weapon_shockwave" ]
REQUIRED_PHRASES = [ "abf01" ]

# Basics fields in the order of _sbrick_basics.dfn; the writer puts the others after them, sorted
BASICS_ORDER = [ "FamilyId", "IndexInFamily", "TargetRestriction", "PowerValue", "SabrinaCost", "SabrinaRelativeValue", "SPCost",
	"ForcedLocalisation" ] + [ "Property %d" % i for i in range(20) ] + [ "LearnRequiresOneOfSkills", "Action Nature", "Skill",
	"Level", "ForbiddenDef", "ForbiddenExclude", "LearnRequiresBricks", "MinCastTime", "MaxCastTime", "MinRange", "MaxRange",
	"CivRestriction", "Faction", "Minimum fame", "AvoidCyclic", "UsableWithEmptyHands" ]
GRAMMAR_GROUPS = [ ("Mandatory", 12), ("Optional", 32), ("Parameter", 4), ("Credit", 12) ]

class Stop(Exception):
	pass

# ---------------------------------------------------------------------------------------------------------------- code
FAMILIES = set(CT.FAMILIES)
SKILLS = set(CT.SKILLS)

def familyValue(family):
	return CT.FAMILY_VALUES[family]

def familyIs(family, kind):
	"""kind: root, mandatory, option, credit or parameter, as BRICK_FAMILIES::is<Kind>Family"""
	v = CT.FAMILY_VALUES[family]
	return any(b <= v <= e for b, e in CT.FAMILY_PREDICATES[kind])

def brickType(family):
	v = CT.FAMILY_VALUES[family]
	for b, e, t in CT.BRICK_TYPES:
		if b <= v <= e:
			return t
	return "UNKNOWN"

def table(key):
	"""a string conversion table of the code, by 'file:Type' or 'file:Type:array'"""
	if key not in CT.TABLES:
		raise Stop("code_tables.py has no table " + key + ": run refresh_code_tables.py, or name one of " + ", ".join(sorted(CT.TABLES)))
	return CT.TABLES[key]

def tableHas(key, value, caseSensitive=False):
	values = table(key)
	return value in values if caseSensitive else value.lower() in [ v.lower() for v in values ]

def wrap16(v):
	v = int(v) & 0xFFFF
	return v - 0x10000 if v >= 0x8000 else v

# -------------------------------------------------------------------------------------------------------- translation
class WordsRow:
	def __init__(self, sheetId, name, description, description2):
		self.id = sheetId
		self.name = name
		self.description = description
		self.description2 = description2

def readWordsFile(path):
	with open(path, "rb") as f:
		lines = f.read().decode("utf-8-sig").split("\n")
	header = lines[0].rstrip("\r").split("\t")
	rows = []
	for l in lines[1:]:
		l = l.rstrip("\r")
		if not l:
			continue
		fields = l.split("\t")
		rows.append(dict(zip(header, fields)))
	return header, rows

class Words:
	"""The ids of a sheet type: those of the work file, which every language must have too; names from English."""
	def __init__(self, sheetType):
		self.type = sheetType
		self.rows = collections.OrderedDict()
		self.problems = []
		column = sheetType + " ID"
		work = os.path.join(TRANSLATION, "work", sheetType + "_words_wk.txt")
		header, rows = readWordsFile(work)
		if column not in header:
			raise Stop(work + " has no column " + column)
		english = {}
		enPath = os.path.join(TRANSLATION, "translated", sheetType + "_words_en.txt")
		for row in readWordsFile(enPath)[1]:
			if row.get(column):
				english[row[column].lower()] = row
		for row in rows:
			sheetId = row.get(column, "")
			if not sheetId:
				continue
			en = english.get(sheetId.lower(), {})
			self.rows[sheetId.lower()] = WordsRow(sheetId, en.get("name", row.get("name", "")), en.get("description", ""),
				en.get("description2", ""))
		with open(os.path.join(TRANSLATION, "languages.txt"), "r", encoding="utf-8") as f:
			languages = [ l.strip() for l in f if l.strip() and l.strip() != "wk" ]
		for language in languages:
			path = os.path.join(TRANSLATION, "translated", sheetType + "_words_" + language + ".txt")
			ids = set(row[column].lower() for row in readWordsFile(path)[1] if row.get(column))
			for sheetId in self.rows:
				if sheetId not in ids:
					self.problems.append(sheetId + " has a row in the work file but none in " + path)

	def get(self, sheetId):
		return self.rows.get(sheetId.lower())

	def ids(self, pattern=None):
		"""the ids (lower case), in the order of the file, that match a regular expression (on the lower case id)"""
		if pattern is None:
			return list(self.rows)
		r = re.compile(pattern)
		return [ i for i in self.rows if r.match(i) ]

# ------------------------------------------------------------------------------------------------------------- sheets
def mergeStruct(parent, child):
	"""a Georges struct of the child over the parent's, atom by atom"""
	if child is None:
		return parent
	if parent is None or not isinstance(parent, dict) or not isinstance(child, dict):
		return child
	merged = dict(parent)
	for k, v in child.items():
		merged[k] = mergeStruct(parent.get(k), v)
	return merged

class Brick:
	def __init__(self, name, folder, source, parent=None, isParent=False):
		self.name = name
		self.folder = folder # under game_element, with forward slashes
		self.source = source
		self.parent = parent
		self.isParent = isParent
		self.basics = {}
		self.properties = []
		self.client = {}
		self.grammar = { group: [] for group, size in GRAMMAR_GROUPS }
		self.faber = None

	def effective(self):
		"""(basics, properties, client, grammar, faber) as Georges gives them: the parent's values under the brick's"""
		basics, properties, client, grammar, faber = self.effectivePositional()
		return basics, [ p for p in properties if p ], client, grammar, faber

	def effectivePositional(self):
		"""effective(), with the properties by their atom number (Property 0..19), None where neither sheet sets one"""
		if self.parent is None:
			return dict(self.basics), list(self.properties), dict(self.client), { k: list(v) for k, v in self.grammar.items() }, self.faber
		basics, properties, client, grammar, faber = self.parent.effectivePositional()
		basics.update(self.basics)
		# properties are atoms Property 0..19: the brick's replace the parent's of the same number, gaps included
		merged = properties + [ None ] * max(0, len(self.properties) - len(properties))
		for i, p in enumerate(self.properties):
			if p is not None:
				merged[i] = p
		client.update(self.client)
		# Georges looks each atom up by its path in the parent: a brick's f<i> replaces the parent's f<i> only, and a
		# faber atom the brick does not set comes from the parent
		for group in grammar:
			mine = self.grammar[group]
			grammar[group] = [ mine[i] if i < len(mine) and mine[i] else (grammar[group][i] if i < len(grammar[group]) else None)
				for i in range(max(len(mine), len(grammar[group]))) ]
			grammar[group] = [ f for f in grammar[group] if f ]
		return basics, merged, client, grammar, mergeStruct(faber, self.faber)

	def family(self):
		return self.effective()[0].get("FamilyId")

	def path(self):
		return os.path.join(GAME_ELEMENT, *self.folder.split("/"), self.name + ".sbrick")

class Phrase:
	def __init__(self, name, folder, bricks, source, castable=True, showInActionProgression=True, showInAPOnlyIfLearnt=False,
		usableByPlayer=True):
		self.name = name
		self.folder = folder
		self.bricks = bricks
		self.source = source
		self.castable = castable
		self.showInActionProgression = showInActionProgression
		self.showInAPOnlyIfLearnt = showInAPOnlyIfLearnt
		self.usableByPlayer = usableByPlayer

	def path(self):
		return os.path.join(GAME_ELEMENT, *self.folder.split("/"), self.name + ".sphrase")

def xmlAttr(value):
	return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;")

def formatValue(value):
	if isinstance(value, bool):
		return "true" if value else "false"
	if isinstance(value, float):
		text = ("%.4f" % value).rstrip("0").rstrip(".")
		return text if text not in ("", "-0") else "0"
	return str(value)

def structLines(indent, values, order=None):
	lines = []
	keys = list(values)
	if order:
		keys = [ k for k in order if k in values ] + sorted(k for k in values if k not in order)
	for k in keys:
		v = values[k]
		if isinstance(v, dict):
			lines.append(indent + "<STRUCT Name=\"" + xmlAttr(k) + "\">")
			lines += structLines(indent + "  ", v)
			lines.append(indent + "</STRUCT>")
		else:
			lines.append(indent + "<ATOM Name=\"" + xmlAttr(k) + "\" Value=\"" + xmlAttr(formatValue(v)) + "\"/>")
	return lines

def formData(body, parent=None):
	text = "<?xml version=\"1.0\"?>\n<FORM Version=\"4.0\" State=\"modified\">\n"
	if parent:
		text += "  <PARENT Filename=\"" + xmlAttr(parent) + "\"/>\n"
	text += "  <STRUCT>\n" + "".join(l + "\n" for l in body) + "  </STRUCT>\n</FORM>\n"
	return text.encode("utf-8")

def brickData(brick):
	basics = dict(brick.basics)
	for i, p in enumerate(brick.properties):
		if p is not None:
			basics["Property %d" % i] = p
	body = []
	if basics:
		body.append("    <STRUCT Name=\"Basics\">")
		body += structLines("      ", basics, BASICS_ORDER)
		body.append("    </STRUCT>")
	if brick.client:
		body.append("    <STRUCT Name=\"Client\">")
		body += structLines("      ", brick.client)
		body.append("    </STRUCT>")
	for group, size in GRAMMAR_GROUPS:
		if brick.grammar[group]:
			body.append("    <STRUCT Name=\"" + group + "\">")
			body += structLines("      ", collections.OrderedDict(("f%d" % i, f) for i, f in enumerate(brick.grammar[group])))
			body.append("    </STRUCT>")
	if brick.faber:
		body.append("    <STRUCT Name=\"faber\">")
		body += structLines("      ", brick.faber)
		body.append("    </STRUCT>")
	return formData(body, brick.parent.name + ".sbrick" if brick.parent else None)

def phraseData(phrase):
	body = [ "    <ATOM Name=\"brick %d\" Value=\"%s\"/>" % (i, xmlAttr(b + ".sbrick")) for i, b in enumerate(phrase.bricks) ]
	body += structLines("    ", collections.OrderedDict([ ("castable", phrase.castable),
		("ShowInActionProgression", phrase.showInActionProgression), ("ShowInAPOnlyIfLearnt", phrase.showInAPOnlyIfLearnt),
		("usable_by_player", phrase.usableByPlayer) ]))
	return formData(body)

def referencedSheets():
	"""(sheet type, name, where) for every phrase a starting role or a mission teaches and every plan an item names"""
	found = []
	createperso = os.path.join(LEVELDESIGN, "game_elem", "createperso")
	for root, dirs, files in os.walk(createperso):
		for f in files:
			if f.endswith(".starting_role"):
				with open(os.path.join(root, f), "r", encoding="utf-8", errors="replace") as fh:
					text = fh.read().split("<LOG>")[0] # the edit history names long gone phrases
				for n in re.findall(r"Name=\"Sabrina Phrase\" Value=\"([^\"]+)\.sphrase\"", text, re.I):
					found.append(("sphrase", n.lower(), "starting role " + f))
	for root, dirs, files in os.walk(os.path.join(LEVELDESIGN, "primitives")):
		for f in files:
			if f.endswith(".primitive"):
				with open(os.path.join(root, f), "r", encoding="utf-8", errors="replace") as fh:
					for m in re.finditer(r"learn_action\s*:\s*([^:<\n]+)", fh.read()):
						for n in m.group(1).split(";"):
							if n.strip():
								found.append(("sphrase", n.strip().lower(), "mission learn_action in " + f))
	for root, dirs, files in os.walk(os.path.join(GAME_ELEMENT, "sitem")):
		for f in files:
			if f.endswith(".sitem"):
				with open(os.path.join(root, f), "r", encoding="utf-8", errors="replace") as fh:
					for n in re.findall(r"Name=\"CraftPlan\" Value=\"([^\"]+)\.sbrick\"", fh.read(), re.I):
						found.append(("sbrick", n.lower(), "item " + f))
	return found

# ---------------------------------------------------------------------------------------------------------- generator
class Generator:
	def __init__(self):
		self.sbrickWords = Words("sbrick")
		self.sphraseWords = Words("sphrase")
		self.bricks = collections.OrderedDict()
		self.parents = collections.OrderedDict()
		self.phrases = collections.OrderedDict()
		self.excluded = {} # (type, id): reason
		self.owned = [] # folders under game_element
		self.errors = []
		self.notes = []
		self.domain = None

	# ---- for the domains
	def error(self, message):
		self.errors.append(message)

	def note(self, message):
		self.notes.append(message)

	def own(self, folder):
		self.owned.append(folder)

	def parent(self, name, folder, parent=None, **fields):
		if not name.startswith("_"):
			raise Stop("parent sheet " + name + " must start with _ (make_sheet_id gives such files no id)")
		b = Brick(name.lower(), folder, "parent of " + (self.domain or "?"), parent, isParent=True)
		self._fill(b, fields)
		if b.name in self.parents:
			self.error("the parent " + b.name + " is made twice (" + self.domain + ")")
		self.parents[b.name] = b
		return b

	def brick(self, name, folder, source, parent=None, **fields):
		b = Brick(name.lower(), folder, source, parent)
		self._fill(b, fields)
		if b.name in self.bricks:
			self.error(b.name + " is made twice: by " + self.bricks[b.name].source + " and by " + source)
		self.bricks[b.name] = b
		return b

	def phrase(self, name, folder, bricks, source, **flags):
		p = Phrase(name.lower(), folder, [ b.lower() for b in bricks ], source, **flags)
		if p.name in self.phrases:
			self.error(p.name + " is made twice: by " + self.phrases[p.name].source + " and by " + source)
		self.phrases[p.name] = p
		return p

	def exclude(self, sheetType, sheetId, reason):
		"""a translation id that gets no sheet, and why (the coverage report lists the reasons)"""
		self.excluded[(sheetType, sheetId.lower())] = reason

	def _fill(self, b, fields):
		for k, v in fields.items():
			if k == "properties":
				b.properties = list(v)
			elif k == "client":
				b.client = dict(v)
			elif k in ("mandatory", "optional", "parameter", "credit"):
				b.grammar[k.capitalize()] = list(v)
			elif k == "faber":
				b.faber = v
			elif k == "basics":
				b.basics.update(v)
			else:
				raise Stop("unknown brick field " + k + " (use basics={...} for the Basics atoms)")

	# ---- checks
	def checkProperty(self, where, prop):
		keyword, sep, tail = prop.partition(":")
		keyword = keyword.strip().lower()
		tail = tail.strip()
		if keyword in CLIENT_ONLY_KEYWORDS:
			return
		spec = CT.PROPERTIES.get(keyword)
		if spec is None:
			self.error(where + ": property '" + prop + "': the server has no keyword " + keyword)
			return
		args = tail.split(":") if tail else []
		if tail.endswith(":"):
			args = args[:-1]
		if len(args) not in spec["counts"]:
			self.error(where + ": property '" + prop + "' has " + str(len(args)) + " arguments, " + spec["keyword"] + " takes "
				+ " or ".join(str(c) for c in spec["counts"]) + " (" + ", ".join(a[2] for a in spec["args"]) + ")")
			return
		for value, arg in zip(args, spec["args"]):
			kind = arg[0]
			try:
				if kind == "i":
					int(value.strip())
				elif kind == "f":
					float(value.strip())
			except ValueError:
				self.error(where + ": property '" + prop + "': " + arg[2] + " is not a" + (" whole" if kind == "i" else "") + " number")
			if kind == "s" and value != value.strip():
				self.error(where + ": property '" + prop + "': the text argument " + arg[2] + " has spaces around it, which the server keeps")
		if keyword == "ma" and args and args[0].strip() not in CT.MAGIC_ACTIONS:
			self.error(where + ": property '" + prop + "': the service builds no magic action " + args[0].strip()
				+ " (it builds " + ", ".join(sorted(CT.MAGIC_ACTIONS)) + ")")

	def checkBrick(self, b):
		where = b.name + " (" + b.source + ")"
		basics, properties, client, grammar, faber = b.effective()
		family = basics.get("FamilyId")
		if family not in FAMILIES:
			self.error(where + ": FamilyId " + str(family) + " is not a family of the code (brick_families.cpp)")
			return
		index = basics.get("IndexInFamily")
		limit = 255 if family in ("BIF", "BIG") else 64
		if not isinstance(index, int) or not 1 <= index <= limit:
			self.error(where + ": IndexInFamily " + str(index) + " is not in 1.." + str(limit) + " (one 64-bit field per family keeps the known bricks)")
		if len(properties) > 20:
			self.error(where + ": " + str(len(properties)) + " properties, the sheet has 20 places")
		for p in properties:
			self.checkProperty(where, p)
		if "Skill" in basics and basics["Skill"] not in ("", "None"):
			for s in str(basics["Skill"]).split(":"):
				if s not in SKILLS:
					self.error(where + ": Skill " + s + " is not a skill of the code (skills.cpp)")
		learn = basics.get("LearnRequiresOneOfSkills", "")
		for entry in [ e for e in str(learn).split(":") if e ]:
			parts = entry.split(" ")
			if len(parts) != 2 or parts[0] not in SKILLS or not parts[1].isdigit() or int(parts[1]) > 250:
				self.error(where + ": LearnRequiresOneOfSkills entry '" + entry + "' is not 'SKILL value' with a skill of the code and a value up to 250")
		for name in [ n for n in str(basics.get("LearnRequiresBricks", "")).split(":") if n ]:
			n = name.lower().replace(".sbrick", "")
			if n not in self.bricks:
				self.error(where + ": LearnRequiresBricks names " + name + ", which this run does not make")
		nature = basics.get("Action Nature")
		if nature is not None and not tableHas("action_nature:TActionNature", nature, True):
			self.error(where + ": Action Nature " + nature + " is not one of the code (action_nature.cpp)")
		civ = basics.get("CivRestriction")
		if civ is not None and not tableHas("people_pd:TPeople:TPeopleConvert", civ):
			self.error(where + ": CivRestriction " + civ + " is not a people of the code")
		for group, size in GRAMMAR_GROUPS:
			if len(grammar[group]) > size:
				self.error(where + ": " + str(len(grammar[group])) + " " + group + " families, the sheet has " + str(size) + " places")
			for f in grammar[group]:
				if f not in FAMILIES:
					self.error(where + ": " + group + " family " + f + " is not a family of the code")
		for k in ("SabrinaCost", "SPCost", "PowerValue"):
			if k in basics and not isinstance(basics[k], int):
				self.error(where + ": " + k + " " + str(basics[k]) + " is not a whole number")

	def phraseValidity(self, phrase):
		"""CPhraseManager::checkPhraseValidity: None when valid, else why not"""
		mandatory, allowed, found = set(), set(), set()
		forbiddenDef, forbiddenExclude = set(), set()
		cost = credit = 0
		relCost = relCredit = 1.0
		for name in phrase.bricks:
			b = self.bricks.get(name)
			basics, properties, client, grammar, faber = b.effective()
			mandatory.update(grammar["Mandatory"] + grammar["Parameter"])
			allowed.update(grammar["Optional"] + grammar["Credit"])
			defWords = [ w for w in str(basics.get("ForbiddenDef", "")).split(":") if w ]
			excWords = [ w for w in str(basics.get("ForbiddenExclude", "")).split(":") if w ]
			for w in defWords:
				if w in forbiddenExclude:
					return "the flag " + w + " of " + name + " is excluded by an earlier brick"
			for w in excWords:
				if w in forbiddenDef:
					return name + " excludes the flag " + w + " of an earlier brick"
			forbiddenDef.update(defWords)
			forbiddenExclude.update(excWords)
			family = basics["FamilyId"]
			if not familyIs(family, "root"):
				found.add(family)
			sabrina = int(basics.get("SabrinaCost", 0))
			if sabrina > 0:
				cost = wrap16(cost + sabrina)
			else:
				credit = wrap16(credit - sabrina)
			rel = float(basics.get("SabrinaRelativeValue", 0.0))
			if rel > 0:
				relCost += rel
			else:
				relCredit -= rel
		totalCost = wrap16(math.trunc(cost * relCost))
		totalCredit = wrap16(math.trunc(credit * relCredit))
		if totalCost > totalCredit:
			return "its cost " + str(totalCost) + " is above its credit " + str(totalCredit)
		missing = [ f for f in mandatory if f not in found ]
		if missing:
			return "the mandatory families " + ", ".join(sorted(missing)) + " are missing"
		extra = [ f for f in found if f not in mandatory and f not in allowed ]
		if extra:
			return "the families " + ", ".join(sorted(extra)) + " are neither mandatory nor allowed"
		return None

	def checkPhrase(self, p):
		where = p.name + " (" + p.source + ")"
		if not p.bricks:
			self.error(where + ": no brick")
			return
		missing = [ b for b in p.bricks if b not in self.bricks ]
		if missing:
			self.error(where + ": names " + ", ".join(missing) + ", which this run does not make")
			return
		if p.castable:
			first = self.bricks[p.bricks[0]].family()
			if not familyIs(first, "root"):
				self.error(where + ": its first brick " + p.bricks[0] + " is not of a root family, and the first brick chooses the action")
			why = self.phraseValidity(p)
			if why:
				self.error(where + ": the server refuses it at memorize (checkPhraseValidity): " + why)
		if p.usableByPlayer and not p.showInAPOnlyIfLearnt and not re.match(r"^.(bf|bm|bc|bhf|bpp[cmspbiwdl]|bs[fmgxd])", p.name):
			self.note(where + ": no rolemaster sells it (the name after its first letter has none of the rolemaster prefixes)")

	def coverage(self):
		"""translation ids without a sheet and without a reason: (type, id) list"""
		left = []
		for sheetType, words, made in (("sbrick", self.sbrickWords, self.bricks), ("sphrase", self.sphraseWords, self.phrases)):
			for i in words.rows:
				if i not in made and (sheetType, i) not in self.excluded:
					left.append((sheetType, i))
		return left

	def check(self, complete):
		self.errors += self.sbrickWords.problems + self.sphraseWords.problems
		# the names come from the translation and make paths: they stay file names inside their folder
		for s in list(self.parents.values()) + list(self.bricks.values()) + list(self.phrases.values()):
			if not isFileName(SHEET_NAME, s.name):
				self.error("the sheet name '" + s.name + "' (" + s.source + ") has other characters than a-z, 0-9 and _, or is a device name of Windows: it cannot be a file name in its folder")
			if not all(isFileName(FOLDER_NAME, part) for part in s.folder.split("/")):
				self.error("the folder '" + s.folder + "' of " + s.name + " (" + s.source + ") is not a path of names of a-z, 0-9 and _ (and no device name of Windows)")
		for folder in self.owned:
			if not all(isFileName(FOLDER_NAME, part) for part in folder.split("/")):
				self.error("the owned folder '" + folder + "' is not a path of names of a-z, 0-9 and _ (and no device name of Windows)")
		for b in self.bricks.values():
			if b.name.startswith("_"):
				self.error(b.name + " (" + b.source + "): a brick name cannot start with _, such a file gets no sheet id")
			elif not self.sbrickWords.get(b.name):
				self.error(b.name + " (" + b.source + ") has no row in the translation (sbrick_words_wk.txt): sheets are named by their translation id")
			self.checkBrick(b)
		seen = {}
		for b in self.bricks.values():
			basics = b.effective()[0]
			key = (basics.get("FamilyId"), basics.get("IndexInFamily"))
			if key in seen:
				self.error(b.name + " and " + seen[key] + " have the same family index " + str(key) + " (ALREADY ADDED brick)")
			seen[key] = b.name
		for p in self.phrases.values():
			if not self.sphraseWords.get(p.name):
				self.error(p.name + " (" + p.source + ") has no row in the translation (sphrase_words_wk.txt)")
			self.checkPhrase(p)
		if len(self.bricks) >= 65535:
			self.error(str(len(self.bricks)) + " bricks: a phrase sends brick ids on 16 bits, there must be fewer than 65535")
		# a generated name must not exist outside the owned folders
		owned = [ os.path.normcase(os.path.join(GAME_ELEMENT, *f.split("/"))) for f in self.owned ]
		names = {}
		for s in list(self.bricks.values()) + list(self.parents.values()):
			names[s.name + ".sbrick"] = s
		for s in self.phrases.values():
			names[s.name + ".sphrase"] = s
		self.outside = {}
		removed = set() # sheets in the owned folders that the run does not make: a write removes them
		for folder in SHEET_ID_FOLDERS:
			for root, dirs, files in os.walk(folder):
				inOwned = any((os.path.normcase(root) + os.sep).startswith(o + os.sep) for o in owned)
				for f in files:
					fl = f.lower()
					if not inOwned and fl in names:
						self.error("Sheet " + f + " also exists as " + os.path.join(root, f) + ", outside the folders the generator owns: "
							+ "move or remove it before generating " + names[fl].path())
					if not inOwned and (fl.endswith(".sbrick") or fl.endswith(".sphrase")):
						self.outside[fl] = os.path.join(root, f)
					if inOwned and (fl.endswith(".sbrick") or fl.endswith(".sphrase")) and fl not in names:
						removed.add(fl)
		# a sheet a write would remove must not be one that a starting role, a mission, an item or the code names
		required = set(n + ".sbrick" for n in REQUIRED_BRICKS) | set(n + ".sphrase" for n in REQUIRED_PHRASES)
		for kind, name, where in referencedSheets():
			if name + "." + kind in removed:
				self.error(where + " names " + name + "." + kind + ", which a write would remove and this run does not make")
		for fl in sorted(removed & required):
			self.error("the code names " + fl + ", which a write would remove and this run does not make")
		# bricks no phrase teaches: nothing in the game reaches them (the interface families are shown, not learnt)
		taught = set(b for p in self.phrases.values() for b in p.bricks)
		# the known bricks of a family are one 64-bit field of the character's database
		for b in self.bricks.values():
			index = b.effective()[0].get("IndexInFamily")
			if b.name in taught and index is not None and int(index) > 64:
				self.error(b.name + " (" + b.source + ") is taught by a phrase and has index " + str(index) + " in its family: a family has 64 known bricks at most")
		untaught = collections.Counter(b.family() for b in self.bricks.values() if b.name not in taught
			and b.family() in FAMILIES and b.family() not in ("BIF", "BIG") and not familyIs(b.family(), "root"))
		if untaught:
			self.note("bricks no phrase teaches, by family: " + ", ".join("%s %d" % kv for kv in sorted(untaught.items())))
		if complete:
			# what the starting roles, the missions and the items name must exist, as a generated sheet or one outside
			for kind, name, where in referencedSheets():
				fileName = name + "." + kind
				if (kind == "sbrick" and name not in self.bricks or kind == "sphrase" and name not in self.phrases) and fileName not in self.outside:
					self.error(where + " names " + fileName + ", which neither this run nor a sheet outside its folders makes")
			for n in REQUIRED_BRICKS:
				if n not in self.bricks:
					self.error("the code names " + n + ".sbrick, which this run does not make")
			for n in REQUIRED_PHRASES:
				if n not in self.phrases:
					self.error("the code names " + n + ".sphrase, which this run does not make")
			left = self.coverage()
			if left:
				self.error(str(len(left)) + " translation ids have no sheet and no reason, among them " + ", ".join(t + " " + i for t, i in left[:20]))

	# ---- writing
	def write(self, dryRun):
		counts = collections.Counter()
		wanted = {}
		for s in list(self.parents.values()) + list(self.bricks.values()):
			wanted[os.path.normcase(s.path())] = (s.path(), brickData(s))
		for p in self.phrases.values():
			wanted[os.path.normcase(p.path())] = (p.path(), phraseData(p))
		changes = []
		for key, (path, data) in sorted(wanted.items()):
			if not os.path.isfile(path):
				state = "new"
			else:
				with open(path, "rb") as f:
					state = "unchanged" if f.read() == data else "changed"
			counts[state] += 1
			if state != "unchanged":
				changes.append((path, data))
		if not dryRun:
			# a file of this suffix in an owned folder is the leftover of a write that stopped: process sheet_id would
			# give it an id
			for folder in self.owned:
				for root, dirs, files in os.walk(os.path.join(GAME_ELEMENT, *folder.split("/"))):
					for f in files:
						if f.endswith(TEMPORARY_SUFFIX):
							try:
								os.remove(os.path.join(root, f))
							except OSError as e:
								raise Stop("removing " + os.path.join(root, f) + ", the leftover of a write that stopped, failed (" + str(e) + "): nothing was changed")
							counts["leftovers of a stopped write removed"] += 1
			# every file is written beside its target first, and nothing changes before the first rename: a write that
			# fails until then leaves the sheets as they were; a stop after it names what was done, and running the
			# write again completes it
			temporaries = []
			current = None
			try:
				for path, data in changes:
					current = path + TEMPORARY_SUFFIX
					os.makedirs(os.path.dirname(path), exist_ok=True)
					temporaries.append(current)
					with open(current, "wb") as f:
						f.write(data)
			except BaseException as e:
				state = "no sheet was changed or removed, " + deleteTemporaries(temporaries, "the files written so far beside them were deleted")
				if not isinstance(e, OSError):
					sys.stderr.write("error: the write was stopped while writing " + str(current) + ", " + state + "\n")
					raise
				raise Stop("writing " + current + " failed (" + str(e) + "): " + state)
			replaced = 0
			try:
				for path, data in changes:
					os.replace(path + TEMPORARY_SUFFIX, path)
					replaced += 1
			except BaseException as e:
				left = deleteTemporaries([ path + TEMPORARY_SUFFIX for path, data in changes[replaced:] ], "")
				state = ("with " + str(replaced) + " of " + str(len(changes)) + " sheets replaced before it and no stale sheet removed"
					+ ("; " + left if left else "") + ": run the write again to complete it")
				if not isinstance(e, OSError):
					sys.stderr.write("error: the write was stopped while replacing " + changes[replaced][0] + ", " + state + "\n")
					raise
				raise Stop("replacing " + changes[replaced][0] + " failed (" + str(e) + "), " + state + " (close what holds the file first)")
		removed = []
		for folder in self.owned:
			base = os.path.join(GAME_ELEMENT, *folder.split("/"))
			for root, dirs, files in os.walk(base):
				for f in files:
					path = os.path.join(root, f)
					if (f.endswith(".sbrick") or f.endswith(".sphrase")) and os.path.normcase(path) not in wanted:
						removed.append(path)
		done = 0
		try:
			for path in removed:
				counts["removed"] += 1
				if not dryRun:
					os.remove(path)
					done += 1
		except BaseException as e:
			state = "with every sheet written and " + str(done) + " of " + str(len(removed)) + " stale sheets removed before it: run the write again to complete it"
			if not isinstance(e, OSError):
				sys.stderr.write("error: the write was stopped while removing " + removed[done] + ", " + state + "\n")
				raise
			raise Stop("removing " + removed[done] + " failed (" + str(e) + "), " + state + " (close what holds the file first)")
		if not dryRun:
			for folder in self.owned:
				base = os.path.join(GAME_ELEMENT, *folder.split("/"))
				for root, dirs, files in sorted(os.walk(base, topdown=False), key=lambda w: -len(w[0])):
					if not os.listdir(root) and root != base:
						os.rmdir(root)
		return counts, removed
