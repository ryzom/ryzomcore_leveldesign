
import os, zlib

from balancing_config import *

if not os.path.isdir("../../game_elem"):
	print("Script run from wrong folder")
	exit(1)

def loadTsvWithHeaders(filename):
	table = {}
	columns = None
	with open(filename, "r") as f:
		for l in f:
			if not columns:
				columns = l.strip().split("\t")
			else:
				row = l.strip().split("\t")
				name = row[0]
				entry = {}
				for i in range(1, len(row)):
					rv = row[i]
					if len(rv) >= 2 and rv[0] == "\"" and rv[-1] == "\"":
						rv = rv[1:-1]
					entry[columns[i]] = rv
				table[name] = entry
	return table;

def loadTsvWithHeadersNoEmpty(filename):
	table = {}
	columns = None
	with open(filename, "r") as f:
		for l in f:
			if not columns:
				columns = l.strip().split("\t")
			else:
				row = l.strip().split("\t")
				name = row[0]
				entry = {}
				for i in range(1, len(row)):
					rv = row[i]
					if len(rv) >= 2 and rv[0] == "\"" and rv[-1] == "\"":
						rv = rv[1:-1]
					if len(rv) > 0:
						entry[columns[i]] = rv
				table[name] = entry
	return table;

creatureFauna = loadTsvWithHeaders("creature_fauna.tsv")
creatureScale = loadTsvWithHeadersNoEmpty("creature_scale.tsv")

generate = {}

textures = {
	"l": "Lacustre/Low Quality/Young",
	"d": "Desert/Medium Quality/Normal",
	"j": "Jungle/High Quality/Old",
	"f": "Jungle/High Quality/Old",
	"p": "PrimR",
	"g": "goo",
}

inherit = {
	"i": True,
	"r": True,
	"e": True
}

folders = {
	"l": "lacustre",
	"d": "desert",
	"j": "jungle",
	"f": "forest",
	"p": "primes_racines",
	"g": "goo",
	"i": "invasion",
	"r": "invasion",
	"e": "event",
}

suffix = {
	"l": "lac",
	"d": "des",
	"j": "jun",
	"f": "for",
	"p": "pr",
	"g": "goo",
}

ecosystem = {
	"l": "Lacustre",
	"d": "Desert",
	"j": "Jungle",
	"f": "Forest",
	"p": "PrimeRoots",
	"g": "Goo",
	"i": "Invasion",
	"r": "Raid",
	"e": "Event",
}

# Override specified group assist (use gooAggro range if this exists)
groupAggro = {
	"g": {
		# Goo attacks all non-goo
		"a": "a_,zp",
		"b": "b_,c_,d_,h_,p_,zp",
		"c": "b_,c_,d_,h_,p_,zp",
		"d": "b_,c_,d_,h_,p_,zp",
		"h": "b_,c_,d_,h_,p_,zp",
		"k": "k_,b_,c_,d_,h_,p_,zp",
		"p": "b_,c_,d_,h_,zp",
	},
	"i": { "a": "zp", "b": "zp", "c": "b_,h_,zp", "h": "zp", "k": "b_,h_,zp", "p": "zp" },
	"r": { "a": "zp", "b": "zp", "c": "b_,h_,zp", "h": "zp", "k": "b_,h_,zp", "p": "zp" },
	"e": { "a": "zp", "b": "zp", "c": "b_,h_,zp", "h": "zp", "k": "b_,h_,zp", "p": "zp" },
}

# Override specified group assist (use gooAssist range if this exists)
groupAssist = {
	"g": {
		# Goo plants defend plants and themselves
		"a": "@", "b": "@", "c": "@", "d": "@", "h": "@", "k": "@",
		"p": "@,p_,p_g"
	},
}

# Don't aggro ecosystem when specified by _ wildcard
dontAggroAssistEs = [ "g" ]

with open("creature_list.txt", "r") as f:
	for l in f:
		c = l.split(".")[0]
		if c.startswith("c") and len(c) == 6:
			id = c[1:3]
			es = c[3:4]
			lvl = c[4:6]
			if id not in generate:
				generate[id] = {}
			g = generate[id]
			if es not in g:
				g[es] = []
			g = g[es]
			if lvl not in g:
				g += [ lvl ]

groups = []
for sheet in creatureFauna:
	entry = creatureFauna[sheet]
	id = entry["id"]
	if not id in groups:
		groups += [ id ]
	if id in generate:
		gen = generate[id]
		for eco in gen:
			if eco in groupAggro and not id + eco in groups:
				groups += [ id + eco ]
groups.sort()
print(groups)
def extendGroup(group, me):
	groupv = group.lower().strip().split(",")
	#if me == "cj":
	#	print group
	#	print groupv
	res = []
	for g in groupv:
		# print(g)
		if g == "@" and not me in res:
			res += [ me ]
		elif len(g) == 2:
			if g[1] == "_":
				for rg in groups:
					if rg[0] == g[0] and (len(rg) == 2 or not rg[2] in dontAggroAssistEs) and not rg in res:
						res += [ rg ]
			elif not g in res:
				res += [ g ]
		elif len(g) == 3:
			if g[1] == "_":
				for rg in groups:
					if len(rg) == 3 and rg[0] == g[0] and rg[2] == g[2] and not rg in res:
						res += [ rg ]
			elif g[2] == "_":
				for rg in groups:
					if g[0] == rg[0] and g[1] == rg[1] and (len(rg) == 2 or rg[2] not in dontAggroAssistEs) and not rg in res:
						res += [ rg ]
			elif not g in res:
				res += [ g ]
	res.sort()
	#if me == "cj":
	#	print res
	return ",".join(res)
print(extendGroup("b_,h_,zp", "ca"))
print(extendGroup("@,p_,p_g", "pa"))
print(extendGroup("ka_,kb_,kc_", "ka"))
print(extendGroup("k_,zp", "dag"))

generatedParents = {}
def generateParent(sheet, eco):
	entry = creatureFauna[sheet]
	es = eco
	print(ecosystem[eco] + " " + entry["name"])
	if eco in inherit:
		es = entry[eco]
	name = "_" + sheet + "_" + suffix[es]
	if name in generatedParents:
		return name
	pathDir = "../../game_elem/creature/" + entry["folder"] + "/" + folders[es]
	if not os.path.isdir(pathDir):
		os.makedirs(pathDir)
	pathFile = pathDir + "/" + name + ".creature"
	esn = ecosystem[es].lower()
	if esn == "primeroots":
		esn = "prime roots"
	with open(pathFile, "w") as f:
		f.write("<?xml version=\"1.0\"?>\n")
		f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
		f.write("  <PARENT Filename=\"_" + sheet + ".creature\"/>\n")
		f.write("  <STRUCT>\n")
		f.write("    <STRUCT Name=\"Basics\">\n")
		f.write("      <ATOM Name=\"First Name\" Value=\"" + esn + " " + entry["name"].lower() + "\"/>\n")
		f.write("      <ATOM Name=\"Ecosystem\" Value=\"" + ecosystem[es] + "\"/>\n")
		f.write("      <STRUCT Name=\"Equipment\">\n")
		f.write("        <STRUCT Name=\"Body\">\n")
		f.write("          <ATOM Name=\"Texture\" Value=\"" + textures[es] + "\"/>\n")
		f.write("        </STRUCT>\n")
		f.write("      </STRUCT>\n")
		f.write("    </STRUCT>\n")
		f.write("  </STRUCT>\n")
		f.write("</FORM>\n")
	return name

xpVariance = 0.1
hpVariance = 0.1

attackTime = 3
attackTimeVariance = 0.2

attackVariance = 0.1

otherVariance = 0.1

notHungryFactor = 0.75
hungryFactor = 1.0
huntingFactor = 1.25
aggroVariance = 0.1
assistVariance = 0.1
aggroDefault = 15
assistDefault = 0

def randomValue(mod, seed):
	rv = zlib.crc32(seed) & 0xffffffff
	return rv % mod

def randomFloat(seed):
	rv = zlib.crc32(seed) & 0xffffffff
	return ((rv % 2000) * 1.0) / 2000.0

def varyFloat(value, variance, seed):
	rv = randomFloat(seed)
	rv = ((rv * 2.0) - 1.0) * variance
	return value + (value * rv)

def varyLevel(level, seed, newbie):
	rv = zlib.crc32("Level_" + seed + "_Level") & 0xffffffff
	vrange = levelVariance[1] - levelVariance[0]
	if newbie:
		vrange = newbieLevelVariance[1] - newbieLevelVariance[0]
	rv = rv % vrange
	vmin = levelVariance[0]
	if newbie:
		vmin = newbieLevelVariance[0]
	rv = rv + vmin
	res = level + rv
	if res < 1:
		res = 1
	return res

def varyProtection(protection, seed):
	rv = zlib.crc32("Protection_" + seed + "_Protection") & 0xffffffff
	rv = rv % 10
	rv = rv - 5
	res = int(round(protection + (protection * rv * 0.01), 0))
	if res < 0:
		res = 0
	if res > 100:
		res = 100
	return res

def randomProtectionMax(level, seed):
	protectionMax = (getScore(level) * attackTime) / combatTime
	protectionMax = varyFloat(protectionMax, attackVariance, "ProtectionsMax" + seed)

for sheet in creatureFauna:
	entry = creatureFauna[sheet]
	id = entry["id"]
	if id in generate:
		gen = generate[id]
		for eco in gen:
			if eco not in folders:
				print sheet
				print "c" + id + eco
				print gen
			parent = generateParent(sheet, eco)
			es = eco
			if eco in inherit:
				es = entry[eco]
			for lvl in gen[eco]:
				name = "c" + id + eco + lvl
				# print(entry["name"] + " " + suffix[es] + " " + eco + " " + lvl + " " + name + " " + parent)
				mpDir = "../../game_elem/creature/" + entry["folder"] + "/_parent_mp/" + folders[eco]
				if not os.path.isdir(mpDir):
					os.makedirs(mpDir)
				mpFile = mpDir + "/_" + name + "_mp.creature"
				if not os.path.isfile(mpFile):
					with open(mpFile, "w") as f:
						f.write("<?xml version=\"1.0\"?>\n")
						f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
						f.write("  <STRUCT>\n")
						f.write("    <STRUCT Name=\"Harvest\">\n")
						f.write("      <STRUCT Name=\"MP1\">\n")
						f.write("        <ATOM Name=\"AssociatedItem\" Value=\"system_mp_basic.sitem\"/>\n")
						f.write("      </STRUCT>\n")
						f.write("    </STRUCT>\n")
						f.write("  </STRUCT>\n")
						f.write("</FORM>\n")
				newbie = False
				boss = False
				refLevel = None
				if lvl in levels:
					refLevel = levels[lvl]
				elif lvl in bossLevels:
					refLevel = bossLevels[lvl]
					boss = True
				elif lvl in newbieLevels:
					refLevel = newbieLevels[lvl]
					newbie = True
				baseLevel = varyLevel(refLevel + levelOffset[eco] + int(entry["levelOffset"]), "Level_" + name, newbie)
				attackLevel = varyLevel(baseLevel + attackOffset[eco] + int(entry["attackOffset"]), "Attack_" + name, newbie)
				defenseLevel = varyLevel(baseLevel + defenseOffset[eco] + int(entry["defenseOffset"]), "Defense_" + name, newbie)
				avgLevel = int(round((attackLevel + defenseLevel) / 2, 0))
				xpLevel = int(round((baseLevel + attackLevel + defenseLevel) / 3, 0))
				playerHpLevel = int(getScore(baseLevel) / 100.0)
				hp = round(varyFloat(getScore(defenseLevel), hpVariance, "life" + name) * hpFactor[eco] * float(entry["hpFactor"]), 0)
				regen = varyFloat(hp / regenTimeAi, hpVariance, "LifeRegen" + name)
				totalTime = round(varyFloat(attackTime, attackTimeVariance, "AttackSpeed" + name), 1)
				totalDamage = (getScore(attackLevel) * totalTime * boosts["melee"] * attackFactor[eco] * float(entry["attackFactor"])) / combatTime
				totalDamage = varyFloat(totalDamage, attackVariance, "NbHitToKillPlayer" + name)
				hitsToKill = (playerHpLevel * 100.0) / totalDamage
				xpGainCoef = round(varyFloat(xpGain[eco] * float(entry["xpGain"]), xpVariance, "XPGainCoef" + name), 2)
				protectionMax = (getScore(defenseLevel) * totalTime) / combatTime
				protectionMax = varyFloat(protectionMax, attackVariance, "ProtectionsMax" + name)
				aggro = entry["aggro"]
				if eco in groupAggro:
					aggro = entry["gooAggro"]
				if len(aggro) == 0:
					aggro = 15
				else:
					aggro = int(aggro)
				assist = entry["assist"]
				if eco in groupAssist:
					assist = entry["gooAssist"]
				if len(assist) == 0:
					assist = 0
				else:
					assist = int(assist)
				groupId = id
				if eco in groupAggro:
					groupId += eco
				aggros = entry["groupAggro"]
				if eco in groupAggro and id[0] in groupAggro[eco]:
					aggros = groupAggro[eco][id[0]]
				aggros = extendGroup(aggros, groupId)
				assists = entry["groupAssist"]
				if eco in groupAssist and id[0] in groupAssist[eco]:
					assists = groupAssist[eco][id[0]]
				assists = extendGroup(assists, groupId)
				groupId = groupId.upper()
				# print baseLevel
				# print attackLevel
				# print defenseLevel
				# print hp
				# print totalDamage
				# print xpGainCoef
				# exit(1)
				sheetDir = "../../game_elem/creature/" + entry["folder"] + "/" + folders[eco]
				if not os.path.isdir(sheetDir):
					os.makedirs(sheetDir)
				sheetFile = sheetDir + "/" + name + ".creature"
				with open(sheetFile, "w") as f:
					f.write("<?xml version=\"1.0\"?>\n")
					f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
					f.write("  <PARENT Filename=\"" + parent + ".creature\"/>\n")
					f.write("  <PARENT Filename=\"_" + name + "_mp.creature\"/>\n")
					f.write("  <STRUCT>\n")
					f.write("    <STRUCT Name=\"Basics\">\n")
					# f.write("      <ATOM Name=\"Level\" Value=\"" + str(avgLevel) + "\"/>\n")
					f.write("      <ATOM Name=\"NbPlayers\" Value=\"1\"/>\n")
					f.write("      <ATOM Name=\"PlayerHpLevel\" Value=\"" + str(playerHpLevel) + "\"/>\n")
					f.write("      <ATOM Name=\"NbHitToKillPlayer\" Value=\"" + str(hitsToKill) + "\"/>\n")
					f.write("      <STRUCT Name=\"Characteristics\">\n")
					f.write("        <ATOM Name=\"DynamicEnergyValue\" Value=\"0.00125\"/>\n") # TODO
					f.write("      </STRUCT>\n")
					f.write("      <STRUCT Name=\"MovementSpeeds\">\n")
					f.write("        <ATOM Name=\"GroupDispersion\" Value=\"" + str(round(varyFloat(0.90, otherVariance, "GroupDispersion" + name), 2)) + "\"/>\n") # TODO
					f.write("      </STRUCT>\n")
					f.write("      <ATOM Name=\"life\" Value=\"" + str(int(hp)) + "\"/>\n")
					f.write("      <ATOM Name=\"AttackSpeed\" Value=\"" + str(totalTime) + "\"/>\n")
					f.write("      <ATOM Name=\"LifeRegen\" Value=\"" + str(regen) + "\"/>\n")
					f.write("      <ATOM Name=\"AttackLevel\" Value=\"" + str(attackLevel) + "\"/>\n")
					f.write("      <ATOM Name=\"DefenseLevel\" Value=\"" + str(defenseLevel) + "\"/>\n")
					f.write("      <ATOM Name=\"XPLevel\" Value=\"" + str(xpLevel) + "\"/>\n")
					f.write("      <ATOM Name=\"TauntLevel\" Value=\"" + str(varyLevel(baseLevel, "TauntLevel" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"MeleeReachValue\" Value=\"1\"/>\n") # TODO
					f.write("      <ATOM Name=\"RegionForce\" Value=\"" + str(getRegionForce(lvl)) + "\"/>\n")
					f.write("      <ATOM Name=\"ForceLevel\" Value=\"" + str(getForceLevel(lvl)) + "\"/>\n")
					f.write("      <ATOM Name=\"LocalCode\" Value=\"" + str(getForceLevel(lvl)) + "\"/>\n")
					if entry["defenseMode"].lower() == "dodge":
						f.write("      <ATOM Name=\"DodgeAsDefense\" Value=\"true\"/>\n")
					else:
						f.write("      <ATOM Name=\"DodgeAsDefense\" Value=\"false\"/>\n")
					f.write("    </STRUCT>\n")
					if (id + eco) in creatureScale and lvl in creatureScale[id + eco]:
						f.write("    <STRUCT Name=\"3d data\">\n")
						f.write("      <ATOM Name=\"Scale\" Value=\"" + str(float(creatureScale[id + eco][lvl])) + "\"/>\n")
						# f.write("      <ATOM Name=\"SoundFamily\" Value=\"0\"/>\n") # TODO
						# f.write("      <ATOM Name=\"SoundVariation\" Value=\"0\"/>\n") # TODO
						f.write("    </STRUCT>\n")
					f.write("    <STRUCT Name=\"Properties\">\n")
					f.write("      <ATOM Name=\"LootHarvestState\" Value=\"Harvestable\"/>\n")
					f.write("      <ATOM Name=\"XPGainCoef\" Value=\"" + str(xpGainCoef) + "\"/>\n")
					f.write("    </STRUCT>\n")
					f.write("    <STRUCT Name=\"Combat\">\n")
					f.write("      <ATOM Name=\"AggroRadiusNotHungry\" Value=\"" + str(int(round(varyFloat(aggro * notHungryFactor, aggroVariance, "AggroRadiusNotHungry" + name), 0))) + "\"/>\n")
					f.write("      <ATOM Name=\"AggroRadiusHungry\" Value=\"" + str(int(round(varyFloat(aggro * hungryFactor, aggroVariance, "AggroRadiusHungry" + name), 0))) + "\"/>\n")
					f.write("      <ATOM Name=\"AggroRadiusHunting\" Value=\"" + str(int(round(varyFloat(aggro * huntingFactor, aggroVariance, "AggroRadiusHunting" + name), 0))) + "\"/>\n")
					f.write("      <ATOM Name=\"DistModulator\" Value=\"" + str(round(varyFloat(0.2, otherVariance, "DistModulator" + name), 2)) + "\"/>\n") # TODO
					f.write("      <ATOM Name=\"TargetModulator\" Value=\"" + str(round(varyFloat(0.25, otherVariance, "TargetModulator" + name), 2)) + "\"/>\n") # TODO
					f.write("      <ATOM Name=\"LifeLevelModulator\" Value=\"" + str(round(varyFloat(0.01, otherVariance, "LifeLevelModulator" + name), 2)) + "\"/>\n") # TODO
					f.write("      <ATOM Name=\"CourageModulator\" Value=\"" + str(round(varyFloat(0.90, otherVariance, "CourageModulator" + name), 2)) + "\"/>\n") # TODO
					f.write("      <ATOM Name=\"GroupCohesionModulator\" Value=\"" + str(round(varyFloat(0.01, otherVariance, "GroupCohesionModulator" + name), 2)) + "\"/>\n") # TODO
					f.write("      <ATOM Name=\"AssistDist\" Value=\"" + str(int(round(varyFloat(assist, assistVariance, "AssistDist" + name), 0))) + "\"/>\n")
					f.write("    </STRUCT>\n")
					f.write("    <STRUCT Name=\"Protections\">\n")
					f.write("      <ATOM Name=\"PiercingFactor\" Value=\"" + str(varyProtection(int(entry["piercingProtection"]), "PiercingFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"SlashingFactor\" Value=\"" + str(varyProtection(int(entry["slashingProtection"]), "SlashingFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"BluntFactor\" Value=\"" + str(varyProtection(int(entry["bluntProtection"]), "BluntFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"RotFactor\" Value=\"" + str(varyProtection(int(entry["rotProtection"]), "RotFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"AcidFactor\" Value=\"" + str(varyProtection(int(entry["acidProtection"]), "AcidFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"ColdFactor\" Value=\"" + str(varyProtection(int(entry["coldProtection"]), "ColdFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"FireFactor\" Value=\"" + str(varyProtection(int(entry["fireProtection"]), "FireFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"PoisonFactor\" Value=\"" + str(varyProtection(int(entry["poisonProtection"]), "PoisonFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"ElectricityFactor\" Value=\"" + str(varyProtection(int(entry["electricityProtection"]), "ElectricityFactor" + name)) + "\"/>\n")
					f.write("      <ATOM Name=\"ShockFactor\" Value=\"" + str(varyProtection(int(entry["shockwaveProtection"]), "ShockFactor" + name)) + "\"/>\n")
					f.write("    </STRUCT>\n")
					f.write("    <STRUCT Name=\"Resists\">\n")
					f.write("      <ATOM Name=\"Fear\" Value=\"" + str(varyLevel(defenseLevel, "Fear" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Sleep\" Value=\"" + str(varyLevel(defenseLevel, "Sleep" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Stun\" Value=\"" + str(varyLevel(defenseLevel, "Stun" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Root\" Value=\"" + str(varyLevel(defenseLevel, "Root" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Blind\" Value=\"" + str(varyLevel(defenseLevel, "Blind" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Snare\" Value=\"" + str(varyLevel(defenseLevel, "Snare" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Slow\" Value=\"" + str(varyLevel(defenseLevel, "Slow" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Acid\" Value=\"" + str(varyLevel(defenseLevel, "Acid" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Cold\" Value=\"" + str(varyLevel(defenseLevel, "Cold" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Electricity\" Value=\"" + str(varyLevel(defenseLevel, "Electricity" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Fire\" Value=\"" + str(varyLevel(defenseLevel, "Fire" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Poison\" Value=\"" + str(varyLevel(defenseLevel, "Poison" + name, newbie)) + "\"/>\n")
					f.write("      <ATOM Name=\"Rot\" Value=\"" + str(varyLevel(defenseLevel, "Rot" + name, newbie)) + "\"/>\n")
					f.write("    </STRUCT>\n")
					f.write("    <STRUCT Name=\"Damage Shield\">\n")
					f.write("      <ATOM Name=\"Damage\" Value=\"0\"/>\n") # TODO
					f.write("      <ATOM Name=\"Drained HP\" Value=\"0\"/>\n") # TODO
					f.write("    </STRUCT>\n")
					f.write("    <ATOM Name=\"category\" Value=\"" + groupId[0] + "\"/>\n")
					f.write("    <ATOM Name=\"race_code\" Value=\"" + groupId[1] + "\"/>\n")
					if len(assists) > 0:
						f.write("    <ATOM Name=\"group_assist\" Value=\"" + assists + "\"/>\n")
					if len(aggros) > 0:
						f.write("    <ATOM Name=\"group_attack\" Value=\"" + aggros + "\"/>\n")
					f.write("    <ATOM Name=\"creature_level\" Value=\"" + str(avgLevel) + "\"/>\n")
					f.write("    <ATOM Name=\"group_id\" Value=\"" + groupId + "\"/>\n")
					f.write("  </STRUCT>\n")
					f.write("</FORM>\n")
					f.flush()
