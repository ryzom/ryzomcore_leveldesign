# Forage and quartering for Ryzom Core, every level up to 250: the prospection bricks (BHFP*, the spying and gardening
# roots BHFSPA and BHFGPA, the material filters BHFPRMFM*), the extraction and care bricks (BHFE*), the quartering root
# bhq01, and the phrases that teach them (abhf*, abhq01, and the Basic Extraction that the fight, magic and craft
# rolemasters sell: ab{f,m,c}fepa01).
#
# What the code does with them (survey_server.md 5 and 8):
# - The first brick picks the class: a prospection root (BHFPPA, BHFSPA, BHFGPA: all three run as prospection) or the
#   extraction root BHFEPA. An extraction phrase whose bricks set no rate (FG_PRES, FG_STAB, KAMI_OFFERING, or no rate
#   brick at all) is a care action. Prospection reads its options from every brick (fg_prospection_phrase.cpp), and
#   extraction likewise (fg_extraction_phrase.cpp); the Sabrina balance is checked each time the phrase is built.
# - Quartering builds a phrase of bhq01 alone (CPhraseManager::harvestDefault); the player's phrases are not used.
# - The skill comes from the ecotype of the deposit, never from the brick.
# - The client gives a forage phrase the background of its BHFPMA or BHFEMA brick by its IndexInFamily (1 forest ...
#   5 prime roots, CSabrinaCom::getPhraseForageFamily), and for the extraction families BHFEEA to BHFEEC it shows the
#   IconOver as the main icon.
#
# The material filters follow the raw materials of core4 (mp_generator, game_element/sitem/raw_material): the group
# and family numbers come from the DFN types the raw material sheets use, and every filter must name a group or family
# that a deposit material has, else the run fails.
#
# Rearranged against the old layout:
# - The care root BHFEPA02 has no mandatory families: speed, rate and quality do nothing in a care action, and the code
#   takes a care action's Sabrina cost as its level, so they would only raise it. It offers the care options
#   (preservation, stability, kami offering, explosion reduction) and the two specialisations, whose care factors
#   apply; the extraction root BHFEPA01 offers the specialisations and the source damage absorption.
# - Deposit tracking (BHFPPOK) excludes the options that act on the sources a search spawns (range, angle, number of
#   sources, knowledge, source time) by ForbiddenDef and ForbiddenExclude: it locates a deposit instead, and its range
#   and FG_RANGE write the same field.
# - Each material filter (BHFPRMFM*) uses the icon of its own raw material instead of its group's.

import collections, os, re
import framework
from balancing import forage as B

OWNS = [
	"sbrick/forage",   # prospection, prospection/material, extraction, care (the Nevrax copies in extraction are replaced)
	"sbrick/harvest",  # bhq01
	"sphrase/forage",
	"sphrase/harvest",
]

PROSPECTION = "sbrick/forage/prospection"
MATERIAL = "sbrick/forage/prospection/material"
EXTRACTION = "sbrick/forage/extraction"
CARE = "sbrick/forage/care"
HARVEST = "sbrick/harvest"
P_PROSPECTION = "sphrase/forage/prospection"
P_EXTRACTION = "sphrase/forage/extraction"
P_CARE = "sphrase/forage/care"
P_HARVEST = "sphrase/harvest"

# The ecotypes in the order of the BHFPMA and BHFEMA numbers, which the client relies on: the FG_ECT_SPC name
# (ecosystem.cpp), the skill of that ecotype, the civilisation whose rolemasters teach it (forest Matis, desert Fyros,
# jungle Zorai, lakes Tryker; the prime roots belong to no nation) and the icon.
ECOTYPES = [
	( "Forest", "SHFF", "matis", "ico_forest.png" ),
	( "Desert", "SHFD", "fyros", "ico_desert.png" ),
	( "Jungle", "SHFJ", "zorai", "ico_jungle.png" ),
	( "Lacustre", "SHFL", "tryker", "ico_lacustre.png" ),
	( "PrimaryRoot", "SHFP", None, "ico_prime_roots.png" ),
]

# The item parts the BHFPMI texts name, as the index of RM_FABER_TYPE (rm_family.cpp TypeToSheetEntry: A MpL (Blade)
# is 0 ... Z MpMF (Magic Focus) is 25), with their icons
ITEM_PARTS = {
	"blade": ( 0, "ico_blade.png" ), "hammer": ( 1, "ico_hammer.png" ), "point": ( 2, "ico_pointe.png" ),
	"shaft": ( 3, "ico_shaft.png" ), "grip": ( 4, "ico_gripp.png" ), "counterweight": ( 5, "ico_counterweight.png" ),
	"trigger": ( 6, "ico_trigger.png" ), "firing pin": ( 7, "ico_firing_pin.png" ), "barrel": ( 8, "ico_barrel.png" ),
	"explosive": ( 9, "ico_explosif.png" ), "ammo jacket": ( 10, "ico_ammo_jacket.png" ),
	"ammo bullet": ( 11, "ico_ammo_bullet.png" ), "armor shell": ( 12, "ico_armor_shell.png" ),
	"lining": ( 13, "ico_lining.png" ), "stuffing": ( 14, "ico_stuffing.png" ), "armor clip": ( 15, "ico_armor_clip.png" ),
	"jewel setting": ( 16, "ico_jewel_stone_support.png" ), "jewel": ( 17, "ico_jewel_stone.png" ),
	"clothes": ( 24, "ico_clothes.png" ), "magic focus": ( 25, "ico_magic_focus.png" ),
}

# The classes of raw materials and the highest stat energy of each (rm_family.h, RM_CLASS_TYPE::TRMClassEnergyLimit)
CLASSES = [ ( "basic", 20 ), ( "fine", 35 ), ( "choice", 50 ), ( "excellent", 65 ), ( "supreme", 100 ) ]

# Names in the texts that the DFN types spell otherwise
GROUP_ALIASES = { "harmful": "nocive" }
FAMILY_ALIASES = { "small spider web": "small spiders web", "large spider web": "large spiders web" }

# Ids of this domain that get no sheet
STEALTH = ("the creature stealth of an extraction (FG_CR_STEALTH) has no consumer: the extraction code has it "
	"commented out, so the brick would do nothing")
VISIBILITY = ("the visibility of a prospected source (FG_VIS_STEALTH, FG_VIS_DIST) has no consumer: the prospection "
	"code has it commented out, so the brick would do nothing")
ATYS = ("'Atys' is no ecotype the code can specialise in: FG_ECT_SPC knows the five ecotypes, and the code takes the "
	"common ecosystem as no specialisation")
EXCLUDED = [
	( "sbrick", r"^bhfeoe01$|^bhfeme0[1-5]$", STEALTH ),
	( "sphrase", r"^abhfeme0[1-5]$", STEALTH ),
	( "sbrick", r"^bhfpsoa01$|^bhfpmm0[1-3]$", VISIBILITY ),
	( "sphrase", r"^abhfppmm0[1-3]$|^abhfspmm0[1-3]$", VISIBILITY ),
	( "sbrick", r"^bhfppoj01$", "a <GEN> placeholder for the visibility option: its parameter family BHFPML has no "
		"translation rows, and the visibility tags have no consumer" ),
	( "sbrick", r"^bhfpma06$|^bhfema06$", ATYS ),
	( "sphrase", r"^abhfpma06$|^abhfema06$", ATYS ),
	( "sphrase", r"^abhfemb08$", "a <GEN> placeholder for a brick bhfemb08 that has no translation row (the extraction "
		"group numbers skip 08)" ),
	( "sphrase", r"^abhf01$", "it would carry bhf01, the default forage brick of the old deposit harvest, which has no "
		"translation row; the code only looks the name up (harvestDefault, which no caller asks for a deposit)" ),
]
# Ids of the scope that other domains make
OTHER_DOMAINS = r"^abhf[fmtz]aca01$|^abhf_magic_start$"

# ------------------------------------------------------------------------------------------------- reading core4 data
def readTyp(path):
	return { m.group(1).lower(): int(m.group(2)) for m in re.finditer(r'Label="([^"]*)" Value="([^"]*)"', framework.readText(path)) }

def readAtoms(path):
	text = framework.readText(path).split("<LOG>")[0]
	return re.findall(r'<PARENT Filename="([^"]+)"', text), dict(re.findall(r'<ATOM Name="([^"]+)" Value="([^"]*)"', text)), \
		re.findall(r'<STRUCT Name="([A-Z]) Mp[A-Za-z]+ \(', text)

class Materials:
	"""The forage raw materials of core4: the deposit sheets (m????d*.sitem, CREATURE_OR_DEPOSIT_MP_CHAR 'd' as
	CDeposit::selectRawMaterials keeps them) under sitem/raw_material, their family and group from their parent"""
	def __init__(self, gen):
		dfn = os.path.join(framework.LEVELDESIGN, "DFN", "game_elem", "_item")
		self.familyIds = readTyp(os.path.join(dfn, "item_mp_family.typ"))
		self.groupIds = readTyp(os.path.join(dfn, "item_mp_group.typ"))
		base = os.path.join(framework.GAME_ELEMENT, "sitem", "raw_material")
		parents = {}
		for f in os.listdir(os.path.join(base, "_parent")):
			parents[f.lower()] = readAtoms(os.path.join(base, "_parent", f))[1]
		self.families = {} # family id: { group, icon, energies, parts }
		self.energies = collections.defaultdict(set) # class index: stat energies
		self.maxQuality = collections.defaultdict(int) # class index: highest MaxQuality
		for root, dirs, files in os.walk(base):
			if os.path.basename(root) == "_parent":
				continue
			for f in files:
				if not (f.endswith(".sitem") and len(f) > 6 and f[0] == "m" and f[5] == "d"):
					continue
				sheetParents, atoms, parts = readAtoms(os.path.join(root, f))
				merged = {}
				for p in sheetParents:
					merged.update(parents.get(p.lower(), {}))
				merged.update(atoms)
				family = self.familyIds.get(merged.get("Family", "").lower())
				group = self.groupIds.get(merged.get("Group", "").lower())
				if family is None or group is None:
					gen.error("raw material " + f + ": family " + merged.get("Family", "?") + " or group " + merged.get("Group", "?")
						+ " is not in item_mp_family.typ / item_mp_group.typ")
					continue
				energy = int(merged.get("StatEnergy", "0"))
				e = self.families.setdefault(family, { "group": group, "icons": collections.Counter(), "parts": set() })
				if e["group"] != group:
					gen.error("raw material family " + merged.get("Family") + " is in two groups")
				e["icons"][merged.get("icon", "").lower()] += 1
				e["parts"].update(ord(p) - ord("A") for p in parts)
				c = classOfEnergy(energy)
				self.energies[c].add(energy)
				self.maxQuality[c] = max(self.maxQuality[c], int(merged.get("MaxQuality", "0")))
		if not self.families:
			raise framework.Stop("no forage raw material under " + base + ": run mp_generator first")

	def group(self, word):
		word = GROUP_ALIASES.get(word.lower(), word.lower())
		return self.groupIds.get(word)

	def family(self, name):
		name = FAMILY_ALIASES.get(name.lower(), name.lower())
		return self.familyIds.get(name)

	def groupHasMaterials(self, group):
		return any(e["group"] == group for e in self.families.values())

	def hasItemPart(self, index):
		return any(index in e["parts"] for e in self.families.values())

	def groupIcon(self, group):
		"""the icon most of the group's materials have"""
		icons = collections.Counter()
		for e in self.families.values():
			if e["group"] == group:
				icons.update(e["icons"])
		return sorted(icons.items(), key=lambda x: (-x[1], x[0]))[0][0]

	def familyIcon(self, family):
		return self.families[family]["icons"].most_common(1)[0][0]

def classOfEnergy(energy):
	for i, (name, limit) in enumerate(CLASSES):
		if energy <= limit:
			return i
	return len(CLASSES) - 1

class Atlas:
	"""the icon names of the interface atlases the client loads (framework.atlasNames: a list that is missing stops the
	run, naming its path and the --atlas option of generate.py)"""
	def __init__(self):
		self.names = framework.atlasNames()

	def has(self, name):
		return name.lower() in self.names

def atlasName(icon):
	"""a raw material's icon (MP_Wood.tga) as the atlas lists it (mp_wood.png)"""
	return re.sub(r"\.tga$", ".png", icon.lower())

# -------------------------------------------------------------------------------------------------------- the domain
class Forage:
	def __init__(self, gen):
		self.gen = gen
		self.atlas = Atlas()
		self.materials = Materials(gen)
		self.costs = {}

	def error(self, message):
		self.gen.error("forage: " + message)

	def icon(self, name):
		if not self.atlas.has(name):
			self.error("icon " + name + " is in no interface atlas")
		return name

	def client(self, **layers):
		return { k: self.icon(v) for k, v in layers.items() }

	def words(self, sheetType, sheetId):
		w = (self.gen.sbrickWords if sheetType == "sbrick" else self.gen.sphraseWords).get(sheetId)
		if w is None:
			raise framework.Stop("forage: " + sheetType + " " + sheetId + " has no translation row")
		return w

	def stated(self, text, pattern, where):
		"""a number a text states (the spec)"""
		m = re.search(pattern, text)
		if not m:
			self.error(where + ": the text '" + text + "' does not state the value (" + pattern + ")")
			return 0.0
		return float(m.group(1))

	def ids(self, sheetType, pattern):
		words = self.gen.sbrickWords if sheetType == "sbrick" else self.gen.sphraseWords
		return [ i for i in words.ids(pattern) if not self.isExcluded(sheetType, i) ]

	def isExcluded(self, sheetType, sheetId):
		return (sheetType, sheetId) in self.gen.excluded

	def brick(self, name, folder, parent, level, family=None, index=None, cost=0, learn=True, ecotypeSkill=None, basics=None, **fields):
		b = dict(basics or {})
		if family:
			b["FamilyId"] = family
		b["IndexInFamily"] = index if index is not None else int(re.search(r"(\d+)$", name).group(1))
		b["Level"] = level
		b["SabrinaCost"] = cost
		if learn:
			b["LearnRequiresOneOfSkills"] = B.learnRequires(level, ecotypeSkill)
			b["SPCost"] = B.spCost(level)
		self.costs[name] = (cost, level)
		return self.gen.brick(name, folder, self.words("sbrick", name).name, parent=parent, basics=b, **fields)

	def phraseCost(self, bricks):
		return sum(self.costs[b][0] for b in bricks if self.costs[b][0] > 0)

	def phrase(self, name, folder, bricks, credits, level, **flags):
		"""a castable phrase: the bricks, then the cheapest counterpart that pays for them, which must be learnable at
		the phrase's level (the client leaves credits out of a phrase's requirements, the server does not)"""
		cost = self.phraseCost(bricks)
		credit = None
		for creditName, creditLevel, points in credits:
			if points >= cost:
				credit = creditName
				if creditLevel > level:
					self.error(name + ": the counterpart " + creditName + " that pays its cost " + str(cost)
						+ " has level " + str(creditLevel) + ", above the phrase's level " + str(level))
				break
		if credit is None:
			self.error(name + ": no counterpart pays its cost " + str(cost))
			credit = credits[-1][0]
		return self.gen.phrase(name, folder, bricks + [ credit ], self.words("sphrase", name).name, **flags)

	# ---- prospection
	def prospection(self):
		gen = self.gen
		self.prospectionCredits = []

		# the counterparts: the phrase names state their numbers, which are their indices
		pcaIds = self.ids("sbrick", r"^bhfpca\d\d$")
		levels = B.creditLevels(len(pcaIds))
		pca = gen.parent("_bhfpca", PROSPECTION, basics={ "FamilyId": "BHFPCA" },
			client=self.client(Icon="ico_focus.png", IconBack="cp_back.png", IconOver="cp_over_more.png"))
		for i, name in enumerate(pcaIds):
			n = i + 1
			phraseWords = gen.sphraseWords.get("a" + name)
			if phraseWords and int(self.stated(phraseWords.name, r"Counterpart (\d+)", "a" + name)) != n:
				self.error("a" + name + " names another counterpart number than " + str(n))
			level = levels[i]
			credit = B.prospectionCredit(level)
			self.brick(name, PROSPECTION, pca, level, index=n, cost=credit, properties=[ "FOCUS: %d" % B.prospectionFocus(level) ])
			self.prospectionCredits.append((name, level, -credit))

		# the roots: all three run as prospection and offer the same options
		options = [ "BHFPPOA", "BHFPPOB", "BHFPPOC", "BHFPPOD", "BHFPPOE", "BHFPPOF", "BHFPPOG", "BHFPPOH", "BHFPPOI",
			"BHFPPOK", "BHFPPOL" ]
		root = gen.parent("_bhfp_root", PROSPECTION, basics={ "Skill": "SHF", "AvoidCyclic": True },
			client=self.client(IconBack="fo_back.png"), optional=options, credit=[ "BHFPCA" ])
		for name, family, icon in ( ( "bhfppa01", "BHFPPA", "ico_prospecting.png" ), ( "bhfspa01", "BHFSPA", "ico_spying.png" ),
				( "bhfgpa01", "BHFGPA", "ico_gardening.png" ) ):
			self.brick(name, PROSPECTION, root, B.FIRST_LEVEL, family=family, client=self.client(Icon=icon))

		# the parameters, family by family: (option, parameter family, option icon, spot) and their bricks
		param = gen.parent("_bhfp_param", PROSPECTION, client=self.client(IconBack="pa_back.png"))
		levels = {} # parameter family: levels of its bricks

		def family(fam, icon=None, folder=PROSPECTION):
			client = self.client(Icon=icon) if icon else {}
			return gen.parent("_" + fam.lower(), folder, parent=param, basics={ "FamilyId": fam }, client=client)

		# terrain
		p = family("BHFPMA")
		for name in self.ids("sbrick", r"^bhfpma\d\d$"):
			n = int(name[-2:])
			ecotype, skill, civ, icon = ECOTYPES[n - 1]
			self.check(self.words("sbrick", name).name, ( "Forest", "Desert", "Jungle", "Lakes", "Prime Roots" )[n - 1], name)
			basics = { "CivRestriction": civ } if civ else {}
			self.brick(name, PROSPECTION, p, B.ECOTYPE_LEVEL, cost=B.prospectionCost(B.ECOTYPE_LEVEL), ecotypeSkill=skill,
				basics=basics, properties=[ "FG_ECT_SPC: " + ecotype ], client=self.client(Icon=icon))
			levels.setdefault("BHFPMA", []).append(B.ECOTYPE_LEVEL)

		# material groups (with the material filter of the group as their parameter) and the material filters
		self.materialFilters(levels)

		# ranges, angles, number of sources, knowledge, speed, source time, deposit tracking: the phrase or brick texts
		# state the values
		def steps(fam, icon, prop, valueOf):
			p = family(fam, icon)
			names = self.ids("sbrick", r"^" + fam.lower() + r"\d\d$")
			for k, name in enumerate(names, 1):
				level = B.stepLevel(k, len(names))
				value = valueOf(name, k)
				self.brick(name, PROSPECTION, p, level, cost=B.prospectionCost(level), properties=[ prop % value ],
					**({ "basics": { "MinCastTime": int(round(value * 10)), "MaxCastTime": int(round(value * 10)) } } if fam == "BHFPMG" else {}))
				levels.setdefault(fam, []).append(level)

		phraseName = lambda name: self.words("sphrase", "a" + name).name
		steps("BHFPMC", "ico_range.png", "FG_RANGE: %g", lambda name, k: self.stated(phraseName(name), r"^(\d+) m Range", name))
		steps("BHFPMD", "ico_angle.png", "FG_ANGLE: %d", lambda name, k: int(self.stated(phraseName(name), r"^(\d+)\S* Angle", name)))
		steps("BHFPME", "ico_multiple_spots.png", "FG_MULTI: %d", lambda name, k: int(self.stated(phraseName(name), r"For (\d+) Resource", name)))
		steps("BHFPMF", "ico_source_knowledge.png", "FG_KNOW: %d",
			lambda name, k: int(self.stated(self.words("sbrick", name).name, r"Knowledge (\d+)", name)))
		steps("BHFPMG", "ico_speed.png", "FG_TIME: %g", lambda name, k: round(B.prospectionTime(k), 2))
		steps("BHFPMH", "ico_source_time.png", "FG_SRC_TIME: %g",
			lambda name, k: self.stated(self.words("sbrick", name).description, r"Adds ([\d.]+) seconds", name))
		steps("BHFPMJ", "ico_location.png", "FG_LD_RANGE: %g", lambda name, k: self.stated(self.words("sbrick", name).name, r"^(\d+) m Deposit", name))

		# item parts
		p = family("BHFPMI")
		for name in self.ids("sbrick", r"^bhfpmi\d\d$"):
			w = self.words("sbrick", name)
			m = re.match(r"^(Minor|Major) (.+) Raw Material Prospecting$", w.name)
			part = ITEM_PARTS.get(m.group(2).lower()) if m else None
			if part is None:
				self.error(name + ": '" + w.name + "' names no item part of RM_FABER_TYPE")
				continue
			if not self.materials.hasItemPart(part[0]):
				self.error(name + ": no forage raw material of core4 makes the item part " + m.group(2))
			major = m.group(1) == "Major"
			level = B.MAJOR_FILTER_LEVEL if major else B.GROUP_FILTER_LEVEL
			self.brick(name, PROSPECTION, p, level, cost=B.prospectionCost(level), client=self.client(Icon=part[1]),
				properties=[ "FG_ITEMPART_FILT: %d" % part[0] ] + ([ "FG_ATTEMPTS: %d" % B.MAJOR_ATTEMPTS ] if major else []))
			levels.setdefault("BHFPMI", []).append(level)

		# material classes: up to a class (the class's highest stat energy, rm_family.h), or only that class (the one
		# stat energy core4's materials of that class have)
		p = family("BHFPMK", "ico_quality.png")
		classNames = [ c[0] for c in CLASSES ]
		for name in self.ids("sbrick", r"^bhfpmk\d\d$"):
			w = self.words("sbrick", name)
			m = re.match(r"^(Up to|Only) (\w+) Materials$", w.name)
			c = classNames.index(m.group(2).lower()) if m and m.group(2).lower() in classNames else None
			if not c:
				self.error(name + ": '" + w.name + "' names no class above basic")
				continue
			level = B.classLevel(self.materials.maxQuality[c - 1])
			if m.group(1) == "Up to":
				prop = "FG_STAT_ENERGY: %d" % CLASSES[c][1]
			else:
				energies = self.materials.energies[c]
				if len(energies) != 1:
					self.error(name + ": the " + classNames[c] + " materials of core4 have the stat energies " + str(sorted(energies))
						+ ", and FG_STAT_ENERGY_ONLY finds one")
					continue
				prop = "FG_STAT_ENERGY_ONLY: %d" % list(energies)[0]
			self.brick(name, PROSPECTION, p, level, cost=B.prospectionCost(level), properties=[ prop ])
			levels.setdefault("BHFPMK", []).append(level)

		# the options: each comes with the first step of its parameter family (the phrases teach them together)
		option = gen.parent("_bhfp_option", PROSPECTION, client=self.client(IconBack="op_back.png"))
		for name, fam, paramFamily, icon, over, words in (
				( "bhfppoa01", "BHFPPOA", "BHFPMA", "ico_atys.png", False, None ),
				( "bhfppob01", "BHFPPOB", "BHFPMB", "ico_aim.png", False, None ),
				( "bhfppoc01", "BHFPPOC", "BHFPMC", "ico_range.png", True, "spot" ),
				( "bhfppod01", "BHFPPOD", "BHFPMD", "ico_angle.png", True, "spot" ),
				( "bhfppoe01", "BHFPPOE", "BHFPME", "ico_multiple_spots.png", True, "spot" ),
				( "bhfppof01", "BHFPPOF", "BHFPMF", "ico_source_knowledge.png", True, "spot" ),
				( "bhfppog01", "BHFPPOG", "BHFPMG", "ico_speed.png", True, None ),
				( "bhfppoh01", "BHFPPOH", "BHFPMH", "ico_source_time.png", True, "spot" ),
				( "bhfppoi01", "BHFPPOI", "BHFPMK", "ico_quality.png", True, None ),
				( "bhfppok01", "BHFPPOK", "BHFPMJ", "ico_location.png", False, "locate" ),
				( "bhfppol01", "BHFPPOL", "BHFPMI", "ico_aim.png", False, None ) ):
			client = { "Icon": icon }
			if over:
				client["IconOver"] = "op_over_more.png"
			basics = {}
			if words == "spot":
				basics = { "ForbiddenDef": "fg_spot", "ForbiddenExclude": "fg_locate" }
			elif words == "locate":
				basics = { "ForbiddenDef": "fg_locate", "ForbiddenExclude": "fg_spot" }
			self.brick(name, PROSPECTION, option, min(levels[paramFamily]), family=fam, index=1, basics=basics,
				client=self.client(**client), parameter=[ paramFamily ],
				properties=[ "FG_SRC_LOCATOR: 1" ] if words == "locate" else [])

		# the phrases
		credits = self.prospectionCredits
		gen.phrase("abhfppa01", P_PROSPECTION, [ "bhfppa01", credits[0][0] ], self.words("sphrase", "abhfppa01").name)
		for name, level, points in credits[1:]:
			gen.phrase("a" + name, P_PROSPECTION, [ "bhfppa01", name ], self.words("sphrase", "a" + name).name)
		for fam, opt in ( ( "bhfpma", "bhfppoa01" ), ( "bhfpmc", "bhfppoc01" ), ( "bhfpmd", "bhfppod01" ), ( "bhfpme", "bhfppoe01" ),
				( "bhfpmf", "bhfppof01" ), ( "bhfpmg", "bhfppog01" ), ( "bhfpmh", "bhfppoh01" ), ( "bhfpmi", "bhfppol01" ),
				( "bhfpmj", "bhfppok01" ), ( "bhfpmk", "bhfppoi01" ) ):
			for name in self.ids("sbrick", r"^" + fam + r"\d\d$"):
				if self.gen.sphraseWords.get("a" + name) and not self.isExcluded("sphrase", "a" + name):
					self.phrase("a" + name, P_PROSPECTION, [ "bhfppa01", opt, name ], credits, self.costs[name][1])
		for name in self.ids("sbrick", r"^bhfpmb\d\d$"):
			self.phrase("a" + name, P_PROSPECTION, [ "bhfppa01", "bhfppob01", name, self.anyMaterial[name] ], credits, self.costs[name][1])
		for name, group in self.specificMaterials:
			self.phrase("a" + name, P_PROSPECTION, [ "bhfppa01", "bhfppob01", self.minorGroup[group], name ], credits, self.costs[name][1])

	def check(self, text, expected, where):
		if expected.lower() not in text.lower():
			self.error(where + ": '" + text + "' does not name " + expected)

	def materialFilters(self, levels):
		"""the material group filters (BHFPMB, each with the filter of its group's family as parameter) and the material
		filters (BHFPRMFM?, 01 any material of the group, then one family each)"""
		gen = self.gen
		param = gen.parents["_bhfp_param"]
		# the filter families by the group of their materials
		letterGroup = {}
		self.specificMaterials = []
		for letter in sorted(set(i[8] for i in self.ids("sbrick", r"^bhfprmfm[a-z]\d\d$"))):
			fam = "BHFPRMFM" + letter.upper()
			names = self.ids("sbrick", r"^bhfprmfm" + letter + r"\d\d$")
			groups = set()
			families = {}
			for name in names[1:]:
				w = self.words("sbrick", name)
				m = re.match(r"^(.+) Prospecting$", w.name)
				f = self.materials.family(m.group(1)) if m else None
				if f is None:
					self.error(name + ": '" + w.name + "' names no raw material family of item_mp_family.typ")
					continue
				if f not in self.materials.families:
					self.error(name + ": no forage raw material of core4 is of the family " + m.group(1))
					continue
				families[name] = f
				groups.add(self.materials.families[f]["group"])
			if len(groups) != 1:
				self.error(fam + ": its materials are in the groups " + str(sorted(groups)) + ", not one")
				continue
			group = groups.pop()
			letterGroup[group] = letter
			p = gen.parent("_" + fam.lower(), MATERIAL, parent=param, basics={ "FamilyId": fam },
				client=self.client(Icon=atlasName(self.materials.groupIcon(group))))
			if not re.match(r"^any material from group$", self.words("sbrick", names[0]).name, re.I):
				self.error(names[0] + " is not the 'any material' filter")
			self.brick(names[0], MATERIAL, p, B.GROUP_FILTER_LEVEL, cost=0)
			levels.setdefault(fam, []).append(B.GROUP_FILTER_LEVEL)
			for name, f in families.items():
				icon = atlasName(self.materials.familyIcon(f))
				self.brick(name, MATERIAL, p, B.FAMILY_FILTER_LEVEL, cost=B.prospectionCost(B.FAMILY_FILTER_LEVEL),
					client=self.client(Icon=icon), properties=[ "FG_RMFAM_FILT: %d" % f ])
				self.specificMaterials.append((name, group))
				levels.setdefault(fam, []).append(B.FAMILY_FILTER_LEVEL)

		# the group filters
		p = gen.parent("_bhfpmb", MATERIAL, parent=param, basics={ "FamilyId": "BHFPMB" })
		self.anyMaterial = {}
		self.minorGroup = {}
		for name in self.ids("sbrick", r"^bhfpmb\d\d$"):
			w = self.words("sbrick", name)
			m = re.match(r"^(?:(Minor|Major) )?(\w+)(?: Group)? Prospecting$", w.name)
			group = self.materials.group(m.group(2)) if m else None
			if group is None or group not in letterGroup:
				self.error(name + ": '" + w.name + "' names no group that a material filter family covers")
				continue
			if not self.materials.groupHasMaterials(group):
				self.error(name + ": no forage raw material of core4 is in the group " + m.group(2))
			major = m.group(1) == "Major"
			level = B.MAJOR_FILTER_LEVEL if major else B.GROUP_FILTER_LEVEL
			letter = letterGroup[group]
			self.brick(name, MATERIAL, p, level, cost=B.prospectionCost(level),
				client=self.client(Icon=atlasName(self.materials.groupIcon(group))), parameter=[ "BHFPRMFM" + letter.upper() ],
				properties=[ "FG_RMGRP_FILT: %d" % group ] + ([ "FG_ATTEMPTS: %d" % B.MAJOR_ATTEMPTS ] if major else []))
			self.anyMaterial[name] = "bhfprmfm" + letter + "01"
			if not major:
				self.minorGroup[group] = name
			levels.setdefault("BHFPMB", []).append(level)

	# ---- extraction and care
	def extraction(self):
		gen = self.gen
		self.extractionCredits = []

		# the counterparts: their number in the name ($BHFECA_TAG) and their index is the number the phrases name
		# ("Extraction Counterpart 5" is abhfeca13), so they rise with their level
		ecaIds = self.ids("sbrick", r"^bhfeca\d\d$")
		order = {}
		for name in ecaIds:
			w = gen.sphraseWords.get("a" + name)
			order[name] = int(self.stated(w.name, r"Counterpart (\d+)", "a" + name)) if w else int(name[-2:])
		if sorted(order.values()) != list(range(1, len(ecaIds) + 1)):
			self.error("the extraction counterparts are not numbered 1.." + str(len(ecaIds)) + " by their phrases")
		levels = B.creditLevels(len(ecaIds))
		eca = gen.parent("_bhfeca", EXTRACTION, basics={ "FamilyId": "BHFECA" },
			client=self.client(Icon="ico_focus.png", IconBack="cp_back.png", IconOver="cp_over_less.png"))
		for name in sorted(ecaIds, key=lambda n: order[n]):
			n = order[name]
			level = levels[n - 1]
			credit = B.extractionCredit(level)
			self.brick(name, EXTRACTION, eca, level, index=n, cost=credit,
				properties=[ "FOCUS: %d" % B.extractionFocus(level), "BHFECA_TAG: %d" % n ])
			self.extractionCredits.append((name, level, -credit))

		# the roots: extraction, and care with no mandatory family
		root = gen.parent("_bhfepa", EXTRACTION, basics={ "FamilyId": "BHFEPA", "Skill": "SHF" }, client=self.client(IconBack="fo_back.png"))
		self.brick("bhfepa01", EXTRACTION, root, B.FIRST_LEVEL, client=self.client(Icon="ico_extracting.png"),
			mandatory=[ "BHFEEA", "BHFEEB", "BHFEEC" ], optional=[ "BHFEOA", "BHFEOB", "BHFEOF" ], credit=[ "BHFECA" ])
		self.brick("bhfepa02", CARE, root, B.FIRST_LEVEL, client=self.client(Icon="ico_preservation.png"),
			optional=[ "BHFEOA", "BHFEOB", "BHFEOC", "BHFEOD", "BHFEOG", "BHFEOH" ], credit=[ "BHFECA" ])

		# speed, rate and quality: the texts state the step or the quality and the version
		effect = gen.parent("_bhfe_effect", EXTRACTION, client=self.client(IconBack="ef_back.png", IconOver2="ef_over_more.png"))
		for fam, over, pattern in ( ( "BHFEEA", "ico_time.png", r"^Speed (\d+) - (Harmful|Gentle) Version$" ),
				( "BHFEEB", "ico_hit_rate.png", r"^Rate (\d+) - (Harmful|Gentle) Version$" ),
				( "BHFEEC", "ico_quality.png", r"^Quality (\d+) - (Harmful|Gentle) Version$" ) ):
			p = gen.parent("_" + fam.lower(), EXTRACTION, parent=effect, basics={ "FamilyId": fam }, client=self.client(IconOver=over))
			names = self.ids("sbrick", r"^" + fam.lower() + r"\d\d$")
			for name in names:
				w = self.words("sbrick", name)
				m = re.match(pattern, w.name)
				if not m:
					self.error(name + ": '" + w.name + "' does not state its step and version")
					continue
				k, gentle = int(m.group(1)), m.group(2) == "Gentle"
				absorption = B.GENTLE_ABSORPTION if gentle else B.HARMFUL_ABSORPTION
				icon = self.client(Icon="ico_gentle.png" if gentle else "ico_harmful.png")
				if fam == "BHFEEC":
					self.brick(name, EXTRACTION, p, k, cost=B.qualityCost(k, gentle), client=icon,
						properties=[ "FG_ABS_Q: %g" % absorption, "FG_QUALITY: %d" % k ])
					continue
				level = B.stepLevel(k, B.SPEED_STEPS)
				if fam == "BHFEEA":
					period = B.extractionPeriod(k)
					self.brick(name, EXTRACTION, p, level, cost=B.extractionStepCost(level, gentle), client=icon,
						basics={ "MinCastTime": int(round(period * 10)), "MaxCastTime": int(round(period * 10)) },
						properties=[ "FG_ABS_S: %g" % absorption, "FG_SRC_PRD: %g" % period ])
				else:
					# FG_SRC_APT is an index into ForageQuantityBrick1..12 of the EGS configuration, which lists the
					# harmful rates 1-6 then the gentle ones: the brick's number
					self.brick(name, EXTRACTION, p, level, cost=B.extractionStepCost(level, gentle), client=icon,
						properties=[ "FG_ABS_A: %g" % absorption, "FG_SRC_APT: %d" % int(name[-2:]) ])
					if int(name[-2:]) != k + (B.SPEED_STEPS if gentle else 0):
						self.error(name + ": its number is not the rate index of step " + str(k) + " of its version")

		# the parameters
		param = gen.parent("_bhfe_param", EXTRACTION, client=self.client(IconBack="pa_back.png"))
		levels = {}
		p = gen.parent("_bhfema", EXTRACTION, parent=param, basics={ "FamilyId": "BHFEMA" })
		for name in self.ids("sbrick", r"^bhfema\d\d$"):
			n = int(name[-2:])
			ecotype, skill, civ, icon = ECOTYPES[n - 1]
			self.check(self.words("sbrick", name).name, ( "Forest", "Desert", "Jungle", "Lakes", "Prime Roots" )[n - 1], name)
			self.brick(name, EXTRACTION, p, B.ECOTYPE_LEVEL, cost=B.extractionOptionCost(B.ECOTYPE_LEVEL), ecotypeSkill=skill,
				basics={ "CivRestriction": civ } if civ else {}, properties=[ "FG_ECT_SPC: " + ecotype ], client=self.client(Icon=icon))
			levels.setdefault("BHFEMA", []).append(B.ECOTYPE_LEVEL)
		p = gen.parent("_bhfemb", EXTRACTION, parent=param, basics={ "FamilyId": "BHFEMB" })
		for name in self.ids("sbrick", r"^bhfemb\d\d$"):
			w = self.words("sbrick", name)
			m = re.match(r"^(\w+) Group Specialization$", w.name)
			group = self.materials.group(m.group(1)) if m else None
			if group is None or not self.materials.groupHasMaterials(group):
				self.error(name + ": '" + w.name + "' names no group of core4's forage raw materials")
				continue
			level = B.EXTRACTION_GROUP_LEVEL
			self.brick(name, EXTRACTION, p, level, cost=B.extractionOptionCost(level),
				client=self.client(Icon=atlasName(self.materials.groupIcon(group))), properties=[ "FG_RMGRP_FILT: %d" % group ])
			levels.setdefault("BHFEMB", []).append(level)

		def steps(fam, folder, icon, costOf, propsOf, over2=False):
			client = { "Icon": icon }
			if over2:
				client["IconOver2"] = "ef_over_more.png"
			p = gen.parent("_" + fam.lower(), folder, parent=param, basics={ "FamilyId": fam }, client=self.client(**client))
			names = self.ids("sbrick", r"^" + fam.lower() + r"\d\d$")
			for k, name in enumerate(names, 1):
				level = B.stepLevel(k, len(names))
				self.brick(name, folder, p, level, cost=costOf(level), properties=propsOf(name, k, level))
				levels.setdefault(fam, []).append(level)

		steps("BHFEMG", EXTRACTION, "ico_absorb_damage.png", B.extractionOptionCost,
			lambda name, k, level: [ "FG_ABS_SRC_DMG: %d" % B.absorbSourceDamagePercent(k) ])
		steps("BHFEMC", CARE, "ico_preservation.png", B.careCost, lambda name, k, level: [ "FG_PRES: %g" % B.careDelta(level) ])
		steps("BHFEMD", CARE, "ico_safe.png", B.careCost, lambda name, k, level: [ "FG_STAB: %g" % B.careDelta(level) ])
		# the texts state the reduction ("by 10%"); FG_REDUCE_DMG is the factor the damage is multiplied by
		steps("BHFEMK", CARE, "ico_safe.png", B.careCost, lambda name, k, level: [ "FG_REDUCE_DMG: %g" %
			round(1.0 - self.stated(self.words("sbrick", name).description, r"by (\d+)%", name) / 100.0, 2) ], over2=True)
		steps("BHFEMF", CARE, "ico_safe.png", B.careCost,
			lambda name, k, level: [ "KAMI_OFFERING: %d" % k, "KAMI_ANGER_DECREASE: %g" % B.kamiAngerDecrease(k) ])

		# the options
		option = gen.parent("_bhfe_option", EXTRACTION, client=self.client(IconBack="op_back.png"))
		for name, folder, fam, paramFamily, icon, over in (
				( "bhfeoa01", EXTRACTION, "BHFEOA", "BHFEMA", "ico_atys.png", False ),
				( "bhfeob01", EXTRACTION, "BHFEOB", "BHFEMB", "ico_aim.png", False ),
				( "bhfeof01", EXTRACTION, "BHFEOF", "BHFEMG", "ico_absorb_damage.png", False ),
				( "bhfeoc01", CARE, "BHFEOC", "BHFEMC", "ico_preservation.png", True ),
				( "bhfeod01", CARE, "BHFEOD", "BHFEMD", "ico_safe.png", True ),
				( "bhfeog01", CARE, "BHFEOG", "BHFEMF", "ico_safe.png", False ),
				( "bhfeoh01", CARE, "BHFEOH", "BHFEMK", "ico_safe.png", True ) ):
			client = { "Icon": icon }
			if over:
				client["IconOver"] = "op_over_more.png"
			self.brick(name, folder, option, min(levels[paramFamily]), family=fam, index=1, client=self.client(**client),
				parameter=[ paramFamily ])

		# the phrases: the Basic Extraction of every role, then one per brick with the first steps of the other mandatory
		# families (the client shows the root's icon for that basic phrase: five bricks, the first of each)
		credits = self.extractionCredits
		basic = [ "bhfepa01", "bhfeea01", "bhfeeb01", "bhfeec01" ]
		for name in ( "abhfepa01", "abmfepa01", "abffepa01", "abcfepa01" ):
			self.phrase(name, P_EXTRACTION, list(basic), credits, B.FIRST_LEVEL)
		for i, fam in enumerate([ "bhfeea", "bhfeeb", "bhfeec" ]):
			for name in self.ids("sbrick", r"^" + fam + r"\d\d$"):
				if self.gen.sphraseWords.get("a" + name):
					bricks = list(basic)
					bricks[i + 1] = name
					self.phrase("a" + name, P_EXTRACTION, bricks, credits, self.costs[name][1])
		for fam, opt in ( ( "bhfema", "bhfeoa01" ), ( "bhfemb", "bhfeob01" ), ( "bhfemg", "bhfeof01" ) ):
			for name in self.ids("sbrick", r"^" + fam + r"\d\d$"):
				if not self.isExcluded("sphrase", "a" + name):
					self.phrase("a" + name, P_EXTRACTION, basic + [ opt, name ], credits, self.costs[name][1])
		for name, level, points in credits[1:]:
			self.gen.phrase("a" + name, P_EXTRACTION, basic + [ name ], self.words("sphrase", "a" + name).name)
		for fam, opt in ( ( "bhfemc", "bhfeoc01" ), ( "bhfemd", "bhfeod01" ), ( "bhfemk", "bhfeoh01" ) ):
			for name in self.ids("sbrick", r"^" + fam + r"\d\d$"):
				self.phrase("a" + name, P_CARE, [ "bhfepa02", opt, name ], credits, self.costs[name][1])

	# ---- quartering
	def harvest(self):
		# Quartering runs a phrase of bhq01 alone, built by the code (harvestDefault), and takes no cost: the brick is
		# never learnt or checked. Index 1 of RootHarvest stays free for bhf01, should it get a translation row.
		self.brick("bhq01", HARVEST, None, 1, family="RootHarvest", index=2, learn=False,
			basics={ "Skill": "SH", "LearnRequiresOneOfSkills": "SH 0" },
			client=self.client(Icon="ico_over_fauna.png", IconBack="bk_generic_brick.png"))
		# The phrase cannot run (the code needs the corpse's material, which only the quartering window gives) and no
		# rolemaster sells a name after 'abh' without 'f': it only teaches the brick to who learns everything.
		self.gen.phrase("abhq01", P_HARVEST, [ "bhq01" ], self.words("sphrase", "abhq01").name, castable=False, showInAPOnlyIfLearnt=True)

	# ---- coverage of the scope
	def checkScope(self):
		gen = self.gen
		other = re.compile(OTHER_DOMAINS)
		for sheetType, pattern, made in ( ( "sbrick", r"^bh[fq]", gen.bricks ), ( "sphrase", r"^abh[fq]|^ab[mfc]fepa01$", gen.phrases ) ):
			words = gen.sbrickWords if sheetType == "sbrick" else gen.sphraseWords
			for i in words.ids(pattern):
				if i not in made and (sheetType, i) not in gen.excluded and not other.match(i):
					self.error(sheetType + " " + i + " is in the scope of the forage domain and has no sheet and no reason")

def generate(gen):
	for sheetType, pattern, reason in EXCLUDED:
		words = gen.sbrickWords if sheetType == "sbrick" else gen.sphraseWords
		ids = words.ids(pattern)
		if not ids:
			gen.error("forage: the exclusion " + pattern + " matches no translation id")
		for i in ids:
			gen.exclude(sheetType, i, reason)
	f = Forage(gen)
	f.prospection()
	f.extraction()
	f.harvest()
	f.checkScope()
