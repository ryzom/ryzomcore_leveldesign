# The misc domain of Ryzom Core: everything that is not fight, magic, forage, craft or powers.
#
# - Interface bricks, never learnt, which the client draws: the fight restriction icons (BIF, one per fight skill, shown
#   by the action composer) and the general icons (BIG: the effect icons the server sends by sheet id, the weapon
#   enchantment icons, the equip latency, the composer's "remove" slot, the xp catalyser and outpost pvp flags).
# - The timed actions (BAPA) the code runs by sheet name: teleport, disconnection, mount, dismount, consume.
# - The proc enchantment root (BEPA) and its phrase abe_use_item_power, which every starting role gives.
# - Training (BT*, score upgrades) and characteristic upgrades (BPP*) with their phrases, permanent bonuses (BPB*) and
#   titles (BPTEA).
#
# What the code does with them is in survey_server.md 7 and 8 and survey_format_client.md 2.6; the numbers and why they
# are what they are in balancing/misc.py.
#
# Rearranged against the Nevrax copies this replaces (survey_format_client.md 3.2):
# - every family has a parent sheet (_bif, _big and its groups, _bapa ...) that carries the family, the level 0 that
#   keeps the client from drawing a digit taken from the file name, and the icon layers the family shares; the
#   enchant_weapon_* icons no longer use the real sheet enchant_weapon.sbrick as their parent;
# - the BIF bricks move from sbrick/fight/interface to sbrick/interface/fight_restriction, one per live fight skill;
# - training, characteristics, bonuses and titles get folders of their own (sbrick/training, sbrick/characteristic,
#   sbrick/bonus, sbrick/title, and the phrases under sphrase/training and sphrase/characteristic).

import os, re
import framework
from balancing import misc as B

OWNS = [
	"sbrick/interface",        # BIF and BIG; the Nevrax copies here are replaced
	"sbrick/timed_action",
	"sbrick/enchantment",
	"sbrick/training",
	"sbrick/characteristic",
	"sbrick/bonus",
	"sbrick/title",
	"sphrase/enchantment",
	"sphrase/training",
	"sphrase/characteristic",
]

ATLASES = [ "texture_interfaces_dxtc.txt", "texture_interfaces_v3.txt" ] # in pipeline/install/interfaces

# ------------------------------------------------------------------------------------------- fight restriction (BIF)
# The action composer shows, for a combat phrase, which weapons it can be used with: one icon per skill of
# phrase_def_skill_restrict_combat (client/data/gamedev/interfaces_v3/phrase.xml: the fifteen master weapon skills),
# the BIF brick whose Skill is that skill (CSBrickManager::makeVisualBrickForSkill, which keeps one brick per skill).
# The tooltip is the brick's name, "%comp with One-handed Mace", with %comp replaced by "[Action compatible]" or
# "[Action NOT compatible]". So a master skill gets the brick whose text names its weapon; every other fight skill gets
# one of the plain "%comp" bricks, so that each of the 47 fight skills has its icon should the list ever name it. The
# ids are given in the order of the skill tree (skills.h), each skill taking the first fitting id after the last one
# given, which keeps the numbers in the tree's order.
WEAPON_WORDS = {
	"One-handed Mace": "SFM1BMM",
	"Staff": "SFM1BSM",
	"Spear": "SFM1PSM",
	"One-handed Axe": "SFM1SAM",
	"One-handed Sword": "SFM1SSM",
	"Two-handed Mace": "SFM2BMM",
	"Pike": "SFM2PPM",
	"Two-handed Axe": "SFM2SAM",
	"Two-handed Sword": "SFM2SSM",
	"Dagger": "SFMCADM",
	"Hand to Hand Combat": "SFMCAHM",
	"Pistol": "SFR1APM",
	"Autolauncher": "SFR2AAM",
	"Launcher": "SFR2ALM",
	"Rifle": "SFR2ARM",
	"Bowpistol": None, # weapons the live skill tree no longer has (the old SFR1AB and SFR2AB)
	"Bowrifle": None,
}

# the icon of a weapon skill (its master skill has the same); the other fight skills show their branch
WEAPON_ICONS = {
	"SFM1BM": "mw_mace.png",
	"SFM1BS": "mw_staff.png",
	"SFM1PS": "mw_lance.png",
	"SFM1SA": "mw_axe.png",
	"SFM1SS": "mw_sword.png",
	"SFM2BM": "mw_2h_mace.png",
	"SFM2PP": "mw_2h_lance.png",
	"SFM2SA": "mw_2h_axe.png",
	"SFM2SS": "mw_2h_sword.png",
	"SFMCAD": "mw_dagger.png",
	"SFMCAH": "cb_main_nue.png",
	"SFR1AP": "rw_pistol.png",
	"SFR2AA": "rw_autolaunch.png",
	"SFR2AL": "rw_launcher.png",
	"SFR2AR": "rw_rifle.png",
}

def bifClient(skill):
	"""the icon layers of the BIF brick of a fight skill, over the family's back and over layers"""
	weapon = skill if skill in WEAPON_ICONS else skill[:-1]
	if weapon in WEAPON_ICONS:
		return { "Icon": WEAPON_ICONS[weapon] }
	if skill == "SF":
		return { "Icon": "ico_multi_fight.png" }
	client = { "Icon": "fp_melee.png" if skill.startswith("SFM") else "fp_range.png" }
	# the one and two handed branches show the hand count, as the weapon icons do not
	if skill[:4] in ( "SFM1", "SFR1" ):
		client["IconOver2"] = "1h_over.png"
	elif skill[:4] in ( "SFM2", "SFR2" ):
		client["IconOver2"] = "2h_over.png"
	return client

def makeBif(gen):
	folder = "sbrick/interface/fight_restriction"
	parent = gen.parent("_bif", folder, basics={ "FamilyId": "BIF", "Level": 0 },
		client={ "IconBack": "bk_generic_brick.png", "IconOver": "mf_over.png" })
	fightSkills = [ s for s in framework.CT.SKILLS if s.startswith("SF") ]
	masters = set(s for s in fightSkills if len(s) == 7) # the seventh letter is the master level (250)
	if masters != set(s for s in WEAPON_WORDS.values() if s):
		gen.error("misc: the weapon words of the BIF texts name " + ", ".join(sorted(s for s in WEAPON_WORDS.values() if s))
			+ ", the code's master fight skills are " + ", ".join(sorted(masters)))
	ids = sorted(gen.sbrickWords.ids(r"^bif\d+$"), key=lambda i: int(i[3:]))
	named = {} # master skill: its ids in order
	plain = []
	obsolete = {}
	for i in ids:
		m = re.match(r"^%comp(?: with (.+))?$", gen.sbrickWords.get(i).name.strip())
		if not m:
			gen.error("misc: the text of " + i + " is neither %comp nor %comp with <weapon>: '" + gen.sbrickWords.get(i).name + "'")
			continue
		if m.group(1) is None:
			plain.append(i)
		elif m.group(1) not in WEAPON_WORDS:
			gen.error("misc: " + i + " names the weapon '" + m.group(1) + "', which WEAPON_WORDS does not know")
		elif WEAPON_WORDS[m.group(1)] is None:
			obsolete[i] = m.group(1)
		else:
			named.setdefault(WEAPON_WORDS[m.group(1)], []).append(i)
	given = {}
	last = 0
	for skill in fightSkills:
		pool = named.get(skill, []) if skill in masters else plain
		choice = next((i for i in pool if int(i[3:]) > last and i not in given), None)
		if choice is None:
			gen.error("misc: no BIF id is left after bif%02d for the fight skill %s" % (last, skill))
			continue
		given[choice] = skill
		last = int(choice[3:])
		gen.brick(choice, folder, "fight restriction icon of " + skill, parent=parent,
			basics={ "IndexInFamily": last, "Skill": skill }, client=bifClient(skill))
	for i in ids:
		if i in given:
			continue
		if i in obsolete:
			gen.exclude("sbrick", i, "names a weapon the live skill tree no longer has (bowpistol, bowrifle): no fight skill to show it for")
		elif any(i in v for v in named.values()):
			gen.exclude("sbrick", i, "a second fight restriction icon for a skill that has one: the client keeps one per skill "
				+ "(CSBrickManager::makeVisualBrickForSkill), and which would win depends on the order the sheets load")
		else:
			gen.exclude("sbrick", i, "a %comp fight restriction icon left over once each of the 47 live fight skills has its own: "
				+ "without a skill the client never shows it")

# ------------------------------------------------------------------------------------------ general interface (BIG)
# The names the code gives, and why each must exist. The effect icons and the weapon enchantment icons come from the
# code tables (the server writes their sheet ids into the bonus and malus lists, character.cpp setDatabase); the others
# are named in code or in the client's interface scripts.
NAMED_BIG = [
	( "big_equip_item", "the equip latency shown as the action in progress (gear_latency.cpp)" ),
	( "big_remove", "the 'remove' slot of the action composer (client sbrick_manager.cpp)" ),
	( "hatred", "the halo effect (s_effect.h)" ),
	( "shoot_again", "the shoot again effect (shoot_again_effect.cpp)" ),
	( "death_penalty", "the death penalty malus (client player.lua)" ),
]
XPCAT_LEVELS = range(50, 251, 50) # player.lua picks big_xpcat_<level> and big_ring_xpcat_<level> for i = 50, 250, 50

# The tooltips of the defense, dodge and parry modifiers (action_handler_help.cpp setConsoModSuccessTooltip) name
# mod_defense, mod_dodge and mod_parry, the sheets the server sends for those effects (effect_families.cpp
# sheetIdTable); until core4 of 2026-11-23 the client named mod_*_success ids that have no rows and never came.

# icon of each effect icon brick, by the back it is drawn on: malus and temporary modifiers on the effect back, auras
# on the aura back (icon names are art: mostly those the Nevrax sheets used, where the atlas has them)
EFFECT_ICONS = {
	"mezz": "ico_mezz.png", "stun": "ico_stunn.png", "root": "ico_root.png", "fear": "ico_fear.png",
	"blind": "ico_blind.png", "snare": "ico_slow.png", "slow": "ico_slow.png",
	"stench": "ico_sickness.png", # the Nevrax sheet named ico_stench, which no atlas has
	"rot": "ico_rot.png", "cold": "ico_cold.png", "fire": "ico_fire.png", "electric": "ico_electric.png",
	"acid": "ico_acid.png", "poison": "ico_poison.png", "shockwave": "ico_shockwave.png",
	"debuff_dodge": "ico_dodge.png", "debuff_combat_skills": "ico_debuff_skill.png", "shielding": "ico_shielding.png",
	"invulnerability": "ico_invulnerability.png", "speeding_up": "ico_speeding_up.png", "berserk": "ico_berserk.png",
	"chg_charac": "ico_level.png",
	"mod_defense": "ico_shield_buff.png", "mod_dodge": "ico_dodge.png", "mod_parry": "ico_parry.png",
	"mod_craft_success": "ico_craft_buff.png", "mod_melee_success": "ico_melee_action_buff.png",
	"mod_range_success": "ico_range_action_buff.png", "mod_magic_success": "ico_magic_action_buff.png",
	"mod_forage_success": "ico_forage_buff.png", "mod_desert_forage_success": "ico_desert.png",
	"mod_forest_forage_success": "ico_forest.png", "mod_lacustre_forage_success": "ico_lacustre.png",
	"mod_jungle_forage_success": "ico_jungle.png", "mod_primary_root_forage_success": "ico_prime_roots.png",
	"mod_protect_magic": "ico_shield_up.png", "hatred": "ico_hatred.png", "death_penalty": "mp_skull.png",
}
EFFECT_OVERS = { "debuff_dodge": "ef_over_less.png" } # the dodge malus, against the dodge bonus mod_dodge
AURA_ICONS = {
	"life_aura": "ico_heal.png", "stamina_aura": "ico_stamina.png", "sap_aura": "ico_sap.png",
	"umbrella_aura": "ico_umbrella.png", "melee_protection_aura": "ico_shielding.png",
	"anti_magic_shield_aura": "ico_anti_magic_shield.png", "war_cry_aura": "ico_war_cry.png",
	"fire_wall_aura": "ico_fire.png", "thorn_wall_aura": "ico_pointe.png", "water_wall_aura": "ico_shockwave.png",
	"lightning_wall_aura": "ico_electric.png",
}
ENCHANT_ICONS = {
	"rot": "ico_rot.png", "acid": "ico_acid.png", "cold": "ico_cold.png", "fire": "ico_fire.png",
	"poison": "ico_poison.png", "electricity": "ico_electric.png", "shockwave": "ico_shockwave.png",
}

def bigNames(gen):
	"""(name, why it must exist) for every BIG brick, without repeats, in the order of the code"""
	found = []
	for key, why in ( ("effect_families:TEffectFamily:sheetIdTable", "effect icon (effect_families.cpp)"),
			("enchant_weapon_effect:EDamageType:sheetIdTable", "weapon enchantment icon (enchant_weapon_effect.cpp)") ):
		for n in framework.table(key):
			if n.lower().endswith(".sbrick"):
				found.append((n[:-len(".sbrick")].lower(), why))
	found += NAMED_BIG
	for level in XPCAT_LEVELS:
		found.append(("big_xpcat_%d" % level, "xp catalyser bonus icon (client player.lua)"))
		found.append(("big_ring_xpcat_%d" % level, "Ring xp catalyser bonus icon (client player.lua)"))
	# player.lua names big_outpost_pvp_<round>, 0 outside a round; the translation sets how many rounds have an icon
	rounds = sorted(int(i[len("big_outpost_pvp_"):]) for i in gen.sbrickWords.ids(r"^big_outpost_pvp_\d+$"))
	if rounds != list(range(len(rounds))):
		gen.error("misc: the big_outpost_pvp_ ids of the translation are not 0 to " + str(len(rounds) - 1) + " without a gap")
	for r in rounds:
		found.append(("big_outpost_pvp_%d" % r, "outpost pvp round icon (client player.lua)"))
	names = []
	seen = set()
	for n, why in found:
		if n not in seen:
			seen.add(n)
			names.append((n, why))
	return names

def makeBig(gen):
	base = "sbrick/interface"
	big = gen.parent("_big", base, basics={ "FamilyId": "BIG", "Level": 0 })
	parents = {
		"effect": gen.parent("_big_effect", base + "/effect", parent=big, client={ "IconBack": "ef_back.png" }),
		"aura": gen.parent("_big_aura", base + "/aura", parent=big, client={ "IconBack": "bk_aura.png" }),
		"power": gen.parent("_big_power", base + "/effect", parent=big, client={ "IconBack": "bk_power.png" }),
		"xpcat": gen.parent("_big_xpcat", base + "/bonus", parent=big, client={ "IconBack": "bk_power.png", "Icon": "ico_cataliseur_xp.png" }),
		"ring_xpcat": gen.parent("_big_ring_xpcat", base + "/bonus", parent=big, client={ "IconBack": "bk_aura.png", "Icon": "ico_cataliseur_xp.png" }),
		"outpost": gen.parent("_big_outpost_pvp", base + "/bonus", parent=big, client={ "IconBack": "bk_outpost.png", "Icon": "ico_multi_fight.png" }),
	}
	parents["enchant"] = gen.parent("_big_enchant_weapon", base + "/enchant_weapon", parent=parents["power"], client={ "Icon": "fp_melee.png" })
	names = bigNames(gen)
	order = { i: n for n, i in enumerate(gen.sbrickWords.ids()) }
	missing = [ n for n, why in names if n not in order ]
	for n in missing:
		gen.error("misc: the code names " + n + ".sbrick (" + dict(names)[n] + "), which has no translation row")
	names = sorted([ (n, why) for n, why in names if n in order ], key=lambda x: order[x[0]])
	index = 0
	placeholders = []
	for n, why in names:
		index += 1 # never learnt, so the index only has to be unique: the order of the translation
		if n in EFFECT_ICONS:
			parent, folder, client = parents["effect"], base + "/effect", { "Icon": EFFECT_ICONS[n] }
			if n in EFFECT_OVERS:
				client["IconOver"] = EFFECT_OVERS[n]
		elif n in AURA_ICONS:
			parent, folder, client = parents["aura"], base + "/aura", { "Icon": AURA_ICONS[n] }
		elif n == "enchant_weapon":
			parent, folder, client = parents["enchant"], base + "/enchant_weapon", {}
		elif n.startswith("enchant_weapon_"):
			element = n[len("enchant_weapon_"):]
			if element not in ENCHANT_ICONS:
				gen.error("misc: no icon for the weapon enchantment " + n)
				continue
			parent, folder, client = parents["enchant"], base + "/enchant_weapon", { "IconOver2": ENCHANT_ICONS[element] }
		elif n == "shoot_again":
			parent, folder, client = parents["power"], base + "/effect", { "Icon": "ico_hit_rate.png" }
		elif n.startswith("big_xpcat_"):
			parent, folder, client = parents["xpcat"], base + "/bonus", {}
		elif n.startswith("big_ring_xpcat_"):
			parent, folder, client = parents["ring_xpcat"], base + "/bonus", {}
		elif n.startswith("big_outpost_pvp_"):
			parent, folder, client = parents["outpost"], base + "/bonus", {}
		elif n == "big_equip_item":
			parent, folder, client = big, base, { "Icon": "ico_armor.png", "IconBack": "bk_generic.png" }
		elif n == "big_remove":
			parent, folder, client = big, base, { "Icon": "no_action.png" }
		else:
			gen.error("misc: no icon for the interface brick " + n + " (" + why + ")")
			continue
		gen.brick(n, folder, why, parent=parent, basics={ "IndexInFamily": index }, client=client)
		# the client gives the xp catalyser and outpost icons tooltips of their own and opens no help for them
		# (action_handler_help.cpp), the others show their name
		if gen.sbrickWords.get(n).name.startswith("<GEN>") and not re.match(r"^big_(ring_)?(xpcat|outpost_pvp)_", n):
			placeholders.append(n)
	if placeholders:
		gen.note("misc: these interface bricks show their name as a tooltip and have a <GEN> placeholder for it: " + ", ".join(placeholders))
	gen.exclude("sbrick", "sleep", "a second sleep icon: the code's Mezz effect draws mezz.sbrick, whose row says 'Sleep', and nothing names sleep.sbrick")

# ------------------------------------------------------------------------------------------------ timed actions (BAPA)
# The code runs each by sheet name and reads one property (timed_action_phrase.cpp); the durations come from the
# configuration (DelayBeforeItemTP, TimeBeforeDisconnection, MountDuration, UnmountDuration) or the item eaten. The root
# sheet is shown as the action in progress. No phrase: the translation has none, and the player never composes them.
TIMED_ACTIONS = [
	( "bapa01", "TA_TELEPORT", "ico_task_travel.png", "teleport ticket (character_inventory_manipulation.cpp)" ),
	( "bapa02", "TA_DISCONNECT", "ico_time.png", "disconnection (client_messages.cpp)" ),
	( "bapa03", "TA_MOUNT", "mektoub_steed.png", "mount (entity_callbacks.cpp, character.cpp)" ),
	( "bapa04", "TA_UNMOUNT", "mektoub_steed.png", "dismount (entity_callbacks.cpp, character.cpp)" ),
	( "bapa05", "TA_CONSUME", "ico_mission_medicine.png", "consume an item (character.cpp)" ),
]

def makeTimedActions(gen):
	folder = "sbrick/timed_action"
	parent = gen.parent("_bapa", folder, basics={ "FamilyId": "BAPA", "Level": 0 }, client={ "IconBack": "bk_generic.png" })
	for n, (name, tag, icon, why) in enumerate(TIMED_ACTIONS):
		client = { "Icon": icon }
		if tag == "TA_CONSUME":
			client["IconBack"] = "bk_conso.png"
		gen.brick(name, folder, why, parent=parent, basics={ "IndexInFamily": n + 1 }, properties=[ tag ], client=client)
		if gen.sbrickWords.get(name) and gen.sbrickWords.get(name).name.startswith("<GEN>"):
			gen.note("misc: " + name + " (" + why + ") has a <GEN> placeholder for its name, which the action in progress shows")

# -------------------------------------------------------------------------------------------- proc enchantment (BEPA)
# Using an enchanted weapon runs the phrase whose first brick is of family BEPA (CPhraseManager::executePhrase): the
# item's own enchantment is cast, paid with its sap (CCharacter::procEnchantment). The brick carries nothing else. Every
# starting role gives abe_use_item_power, and no rolemaster sells it (be is no rolemaster prefix).
def makeProcEnchantment(gen):
	parent = gen.parent("_bepa", "sbrick/enchantment", basics={ "FamilyId": "BEPA", "Level": 0 })
	gen.brick("bepa01", "sbrick/enchantment", "the proc enchantment root", parent=parent, basics={ "IndexInFamily": 1 },
		client={ "Icon": "ico_use_enchantement.png" })
	gen.phrase("abe_use_item_power", "sphrase/enchantment", [ "bepa01" ], "the use item enchantment action of every starting role",
		showInAPOnlyIfLearnt=True)

# --------------------------------------------------------------------------------------------------- training (BT*)
TRAINING = [ # family, id prefix, score (scores.cpp), icon
	( "BTHP", "bthp", "HitPoints", "ico_heal.png" ),
	( "BTSAP", "btsap", "Sap", "ico_sap.png" ),
	( "BTSTA", "btsta", "Stamina", "ico_stamina.png" ),
	( "BTFOC", "btfoc", "Focus", "ico_focus.png" ),
]

def makeTraining(gen):
	scores = framework.table("scores:TScores:stringTable")
	training = gen.parent("_bt", "sbrick/training", basics={ "Level": 0 }, client={ "IconBack": "ch_back.png" })
	modifier = B.trainingModifier()
	for family, prefix, score, icon in TRAINING:
		if score not in scores:
			gen.error("misc: the score " + score + " is not one of the code (" + ", ".join(scores) + ")")
		folder = "sbrick/training"
		parent = gen.parent("_" + prefix, folder, parent=training, basics={ "FamilyId": family }, client={ "Icon": icon })
		for i in gen.sbrickWords.ids(r"^" + prefix + r"\d+$"):
			gen.brick(i, folder, "score upgrade of " + score, parent=parent, basics={ "IndexInFamily": int(i[len(prefix):]) },
				properties=[ "SCORE_UPGRADE: %s:%d" % (score, modifier) ])
		# The phrases teach the brick of their number. A mission gives them (learn_action); no rolemaster sells them, and
		# the action progression window would list rewards nobody can buy, so they show only once learnt.
		for p in gen.sphraseWords.ids(r"^a" + prefix + r"\d+$"):
			gen.phrase(p, "sphrase/training", [ p[1:] ], "teaches the score upgrade " + p[1:], castable=False,
				showInActionProgression=False, showInAPOnlyIfLearnt=True)

# ------------------------------------------------------------------------------------------ characteristics (BPP*)
# The rolemaster types that sell each characteristic (rolemaster_flags.cpp canSellPhrase) and the skill families of
# those types: the gate is "one of" their skills, so constitution and metabolism are reached by any domain and the
# others by the domain that sells them. Characteristics are paid in the skill points of the rolemaster that sells them.
CHARAC_SKILLS = {
	"c": [ "SF", "SM", "SH", "SC" ],
	"m": [ "SF", "SM", "SH", "SC" ],
	"s": [ "SF" ],
	"b": [ "SF" ],
	"i": [ "SM" ],
	"w": [ "SM" ],
	"d": [ "SH", "SC" ],
	"l": [ "SH", "SC" ],
}

def makeCharacteristics(gen):
	codes = framework.table("characteristics:TCharacteristics:codeTable")
	names = framework.table("characteristics:TCharacteristics:stringTable")
	charac = gen.parent("_bpp", "sbrick/characteristic", client={ "IconBack": "ch_back.png" })
	for code, name in zip(codes, names):
		if code not in CHARAC_SKILLS:
			gen.error("misc: the code's characteristic " + name + " (" + code + ") has no rolemaster skills in CHARAC_SKILLS")
			continue
		family = "BPP" + code.upper()
		prefix = "bpp" + code
		folder = "sbrick/characteristic/" + name.lower()
		ids = gen.sbrickWords.ids(r"^" + prefix + r"\d+$")
		step = B.characStep(len(ids))
		if step is None:
			gen.error("misc: the %d upgrades of %s cannot share the %d points from %d to %d evenly" % (len(ids), name,
				B.CHARAC_MAX - B.CHARAC_START, B.CHARAC_START, B.CHARAC_MAX))
			continue
		if sorted(int(i[len(prefix):]) for i in ids) != list(range(1, len(ids) + 1)):
			gen.error("misc: the " + prefix + " ids of the translation are not 1 to " + str(len(ids)) + " without a gap")
		parent = gen.parent("_" + prefix, folder, parent=charac, basics={ "FamilyId": family, "SPCost": B.characPrice(step) },
			client={ "Icon": "ico_" + name.lower() + ".png" })
		for i in ids:
			index = int(i[len(prefix):])
			gate = B.characGate(index, step)
			basics = { "IndexInFamily": index, "Level": B.characLevel(index, step),
				"LearnRequiresOneOfSkills": ":".join("%s %d" % (s, gate) for s in CHARAC_SKILLS[code]) }
			# Each upgrade needs the one before it. The rolemaster then offers one upgrade per characteristic, the next one,
			# instead of every upgrade up to the character's skill at once (a level 100 fighter would see 80 lines), and the
			# client lists the next one as soon as a purchase teaches the previous brick (CPhrasePriceCB::onBrickLearned).
			# All upgrades give the same points, so the order costs the buyer nothing; the server checks the chain too
			# (isPlayerAllowedToGetAllBricksFromPhrase).
			if index > 1:
				basics["LearnRequiresBricks"] = "%s%02d" % (prefix, index - 1)
			gen.brick(i, folder, "%s upgrade %d" % (name, index), parent=parent, basics=basics,
				properties=[ "CHARAC_UPGRADE: %s:%d" % (name, step) ])
		# The rolemasters sell them by the abpp<code> prefix; the client draws them as characteristic buys, not actions.
		# They stay in the action progression (ShowInActionProgression true): the client keeps the skill requirement of a
		# phrase only for the phrases of that window (CSPhraseManager::computePhraseProgression fills _PhraseReqSkillMap
		# after skipping the others), and the rolemaster list checks the skill gate with that formula (phraseRequirementOk).
		# Out of the window, every upgrade would be offered at any skill and the server would refuse most of them.
		for p in gen.sphraseWords.ids(r"^a" + prefix + r"\d+$"):
			gen.phrase(p, "sphrase/characteristic/" + name.lower(), [ p[1:] ], "teaches the characteristic upgrade " + p[1:],
				castable=False)

# ------------------------------------------------------------------------------------------- permanent bonuses (BPB*)
def makeBonuses(gen):
	bonus = gen.parent("_bpb", "sbrick/bonus", basics={ "Level": 0 }, client={ "IconBack": "ch_back.png" })
	families = [
		( "BPBCA", "bpbca", "ico_durability.png", lambda n: "BONUS_CR_DURABILITY: %s" % framework.formatValue(B.durabilityBonus(n)),
			"craft durability bonus (faber_action.cpp)" ),
		( "BPBHFEA", "bpbhfea", "ico_time_bonus.png", lambda n: "BONUS_FG_EXTRACTION_TIME_GC: %d" % B.extractionTimeBonus(n),
			"extraction time bonus (character.cpp computeForageBonus)" ),
	]
	for family, prefix, icon, prop, why in families:
		ids = gen.sbrickWords.ids(r"^" + prefix + r"\d+$")
		parent = gen.parent("_" + prefix, "sbrick/bonus", parent=bonus, basics={ "FamilyId": family }, client={ "Icon": icon },
			properties=[ prop(len(ids)) ])
		for i in ids:
			gen.brick(i, "sbrick/bonus", why, parent=parent, basics={ "IndexInFamily": int(i[len(prefix):]) })
	for i in gen.sbrickWords.ids(r"^bpbgla\d+$"):
		gen.exclude("sbrick", i, "landmark bonus: the client has had no landmark limit since dda809d34 (2017), BONUS_LANDMARK_NUMBER only "
			+ "sets INTERFACES:NB_BONUS_LANDMARKS, which nothing reads")

# ---------------------------------------------------------------------------------------------------- titles (BPTEA)
# A title brick does nothing on the server: the client unlocks a character title when every brick unblock.titles names
# for it is known (CSkillManager, BricksNeeded), and missions give the bricks (learn_brick). No rolemaster sells them.
# Indices: casino_title_<n>_index<k> says its index; the others take the lowest free ones in the order of the
# translation.
def makeTitles(gen):
	folder = "sbrick/title"
	parent = gen.parent("_bptea", folder, basics={ "FamilyId": "BPTEA", "Level": 0 },
		client={ "Icon": "ico_task_rite.png", "IconBack": "ch_back.png" })
	ids = gen.sbrickWords.ids(r"^(bptea\d+|slaughter_week_title_\d+|casino_title_\d+_index\d+|titre_gloire_.+)$")
	taken = {}
	for i in ids:
		m = re.match(r"^casino_title_\d+_index(\d+)$", i)
		if m:
			taken[i] = int(m.group(1))
	free = ( n for n in range(1, 65) if n not in taken.values() )
	backs = { "bptea01": "bk_kami.png", "bptea02": "bk_karavan.png" } # the kami and karavan champions
	for i in ids:
		index = taken.get(i) or next(free)
		client = { "IconBack": backs[i] } if i in backs else {}
		gen.brick(i, folder, "title", parent=parent, basics={ "IndexInFamily": index }, client=client)
		if gen.sbrickWords.get(i).name.startswith("<GEN>"):
			gen.note("misc: the title brick " + i + " has a <GEN> placeholder for its name")
	gen.note("misc: unblock.titles (game_element/xp_table) names none of the title bricks, so learning one unlocks no title yet")
	for i in gen.sbrickWords.ids(r"^government_title_"):
		gen.exclude("sbrick", i, "a <GEN> placeholder without text that no code, character title or unblock.titles entry names")
	for i in gen.sbrickWords.ids(r"^rpjob_\d+$"):
		gen.exclude("sbrick", i, "a <GEN> placeholder without text that nothing names (the client's rpjob_ checks are on item sheets)")

# ----------------------------------------------------------------------------------------------------------- checks
def loadAtlas(gen):
	folder = os.path.normpath(os.path.join(framework.LEVELDESIGN, "..", "pipeline", "install", "interfaces"))
	names = set()
	for a in ATLASES:
		path = os.path.join(folder, a)
		if not os.path.isfile(path):
			gen.error("misc: the interface atlas list " + path + " does not exist, so the icons cannot be checked: build the interfaces or fix the path")
			continue
		with open(path, "r", encoding="utf-8", errors="replace") as f:
			for l in f:
				if l.strip():
					names.add(l.split()[0].lower())
	return names

TOKEN = re.compile(r"\$(\$|[|0-9]*)([A-Za-z_]*)")

def checkText(gen, brick):
	"""every $ token of the brick's texts names a property the brick has, with the argument it reads"""
	row = gen.sbrickWords.get(brick.name)
	if not row:
		return
	properties = {}
	for p in brick.effective()[1]:
		keyword, sep, tail = p.partition(":")
		properties[keyword.strip().lower()] = [ a for a in tail.strip().split(":") if a ] if tail.strip() else []
	for text in ( row.name, row.description, row.description2 ):
		for m in TOKEN.finditer(text or ""):
			if m.group(1) == "$":
				continue
			digits = [ c for c in m.group(1) if c.isdigit() ]
			arg = int(digits[0]) if digits else 0
			key = m.group(2).lower()
			if not key or key in framework.CLIENT_ONLY_KEYWORDS:
				continue
			if key not in properties or arg >= len(properties[key]):
				gen.error("misc: the text of " + brick.name + " shows $" + m.group(1) + m.group(2) + ", which its properties do not give")

def generate(gen):
	first = len(gen.bricks), len(gen.parents)
	makeBif(gen)
	makeBig(gen)
	makeTimedActions(gen)
	makeProcEnchantment(gen)
	makeTraining(gen)
	makeCharacteristics(gen)
	makeBonuses(gen)
	makeTitles(gen)
	atlas = loadAtlas(gen)
	made = list(gen.bricks.values())[first[0]:] + list(gen.parents.values())[first[1]:]
	for s in made:
		for k in ( "Icon", "IconBack", "IconOver", "IconOver2" ):
			v = s.client.get(k)
			if v and atlas and v.lower() not in atlas:
				gen.error("misc: " + s.name + " " + k + " " + v + " is in no interface atlas (" + ", ".join(ATLASES) + ")")
		if not s.isParent:
			checkText(gen, s)
