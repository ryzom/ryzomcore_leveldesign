# Writes code_tables.py, the tables of the Ryzom Core code that the sheet generator checks its sheets against: the brick
# families and their ranges, the brick types, the brick property keywords and their arguments, the skills, the string
# conversion tables of game_share and of the entities game service, and the magic action types the service builds.
#
# Run it after a change to those files in the code: python refresh_code_tables.py <code folder of the tree>
# (the folder that holds ryzom/ and nel/). The tables are committed beside it, so the generator runs from the
# leveldesign repository alone and a code change shows in its diff.

import os, re, sys

if len(sys.argv) != 2:
	sys.exit("usage: python refresh_code_tables.py <code folder of the tree, the one that holds ryzom/ and nel/>")
codeRoot = sys.argv[1]
gameShare = os.path.join(codeRoot, "ryzom", "common", "src", "game_share")
egs = os.path.join(codeRoot, "ryzom", "server", "src", "entities_game_service")
for folder in (gameShare, egs):
	if not os.path.isdir(folder):
		sys.exit("Folder " + folder + " does not exist: " + codeRoot + " is not the code folder of a tree")

def read(path):
	with open(path, "r", encoding="latin-1") as f:
		return f.read()

def stripComments(text):
	text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
	return re.sub(r"//[^\n]*", "", text)

# ---- brick families: the enum of brick_families.h, evaluated as the compiler does
header = stripComments(read(os.path.join(gameShare, "brick_families.h")))
m = re.search(r"enum\s+TBrickFamily\s*\{(.*?)\};", header, re.S)
if not m:
	sys.exit("No enum TBrickFamily in brick_families.h")
values = {}
current = -1
for item in m.group(1).split(","):
	item = item.strip()
	if not item:
		continue
	if "=" in item:
		name, expr = [ s.strip() for s in item.split("=", 1) ]
		current = int(expr, 0) if re.match(r"^-?(0x)?[0-9a-fA-F]+$", expr) else values[expr]
	else:
		name = item
		current += 1
	values[name] = current

def predicateRanges(function):
	m = re.search(r"inline\s+bool\s+" + function + r"\s*\(\s*TBrickFamily\s+family\s*\)\s*\{(.*?)\}", header, re.S)
	if not m:
		sys.exit("No " + function + " in brick_families.h")
	return re.findall(r"family\s*>=\s*(\w+)\s*&&\s*family\s*<=\s*(\w+)", m.group(1))

predicates = {}
for key, function in (("root", "isRootFamily"), ("mandatory", "isMandatoryFamily"), ("option", "isOptionFamily"),
	("credit", "isCreditFamily"), ("parameter", "isParameterFamily")):
	predicates[key] = [ (values[b], values[e]) for b, e in predicateRanges(function) ]

source = stripComments(read(os.path.join(gameShare, "brick_families.cpp")))
m = re.search(r"brickType\s*\(\s*TBrickFamily\s+rootFamily\s*\)\s*\{(.*?)return\s+BRICK_TYPE::UNKNOWN", source, re.S)
brickTypes = [ (values[b], values[e], t) for b, e, t in
	re.findall(r"rootFamily\s*>=\s*(\w+)\s*&&\s*rootFamily\s*<=\s*(\w+)\s*\)\s*return\s+BRICK_TYPE::(\w+)", m.group(1)) ]

# ---- every string conversion table: NL_BEGIN_STRING_CONVERSION_TABLE (Type) ... NL_STRING_CONVERSION_TABLE_ENTRY(X)
def conversionTables(folder, recurse):
	tables = {}
	for root, dirs, files in os.walk(folder):
		for f in sorted(files):
			if not f.endswith(".cpp"):
				continue
			text = stripComments(read(os.path.join(root, f)))
			for tm in re.finditer(r"NL_BEGIN_STRING_CONVERSION_TABLE\s*\(\s*(\w+)\s*\)(.*?)NL_END_STRING_CONVERSION_TABLE", text, re.S):
				entries = re.findall(r"NL_STRING_CONVERSION_TABLE_ENTRY\s*\(\s*(\w+)\s*\)", tm.group(2))
				tables[os.path.splitext(f)[0] + ":" + tm.group(1)] = entries
			# the written-out form: CStringConversion<T>::CPair name[] = { { "Text", value }, ... }
			# (a file can hold several tables of one type, so the array name is part of the key)
			for tm in re.finditer(r"CStringConversion\s*<\s*([\w:]+)\s*>\s*::\s*CPair\s+(?:const\s+)?(\w+)\s*\[\s*\]\s*=\s*\{(.*?)\}\s*;", text, re.S):
				entries = re.findall(r"\{\s*\"([^\"]*)\"\s*,\s*[\w:]+\s*\}", tm.group(3))
				tables[os.path.splitext(f)[0] + ":" + tm.group(1).split("::")[-1] + ":" + tm.group(2)] = entries
			# the persistent data form: struct { const char* Name; T Value; } name[] = { { "Text", value }, ... }
			for tm in re.finditer(r"struct\s*\{\s*const\s+char\s*\*\s*Name\s*;\s*([\w:]+)\s+Value\s*;\s*\}\s*(\w+)\s*\[\s*\]\s*=\s*\{(.*?)\}\s*;", text, re.S):
				entries = re.findall(r"\{\s*\"([^\"]*)\"\s*,\s*[\w:]+\s*\}", tm.group(3))
				tables[os.path.splitext(f)[0] + ":" + tm.group(1).split("::")[-1] + ":" + tm.group(2)] = entries
		if not recurse:
			break
	return tables

tables = conversionTables(gameShare, False)
tables.update(conversionTables(egs, True))
families = tables.get("brick_families:TBrickFamily")
if not families:
	sys.exit("No string table of TBrickFamily in brick_families.cpp")
for name in families:
	if name not in values:
		sys.exit("The string table of brick_families.cpp names " + name + ", which the enum does not have")

# ---- the skills, from the string table of skills.cpp
skills = tables.get("skills:ESkills")
if not skills:
	sys.exit("No string table of ESkills in skills.cpp")

# ---- brick properties: the $* comments of addParam give each keyword its structure and arguments, and the parser
# generated from them (egs_static_brick.cpp.h) the argument counts it accepts
brickSource = read(os.path.join(egs, "egs_sheets", "egs_static_brick.cpp"))
body = brickSource[brickSource.index("void addParam("):brickSource.index("} // addParam //")]
generated = read(os.path.join(egs, "egs_sheets", "egs_static_brick.cpp.h"))
structChecks = {}
structArgs = {} # the arguments as the parser reads them: index -> (field type, field name)
for sm in re.finditer(r"struct\s+(CSBrickParam\w+)\s*:\s*public\s+TBrickParam::IId\s*\{(.*?)\n\};", generated, re.S):
	structChecks[sm.group(1)] = re.findall(r"if\s*\(([^)]*args\.size\(\)[^)]*)\)\s*\n?\s*return\s+\*this", sm.group(2))
	fields = dict((n, t) for t, n in re.findall(r"^\s*((?:unsigned\s+|signed\s+)?[\w:<>]+)\s+(\w+)\s*;", sm.group(2), re.M))
	reads = {}
	for am in re.finditer(r"fromString\(\s*args\[(\d+)\]\s*,\s*(\w+)\s*\)|(\w+)\s*=\s*\(\w+\)\s*ato[fil]+\(\s*args\[(\d+)\]|(\w+)\s*=\s*args\[(\d+)\]", sm.group(2)):
		index, name = (am.group(1), am.group(2)) if am.group(1) else ((am.group(4), am.group(3)) if am.group(4) else (am.group(6), am.group(5)))
		reads[int(index)] = (fields.get(name, "?"), name)
	structArgs[sm.group(1)] = reads
properties = {}
for case in re.split(r"\n\s*case\s+TBrickParam::", body)[1:]:
	keyword = case.split(":", 1)[0].strip()
	sm = re.search(r"new\s+(CSBrickParam\w+)\s*\(", case)
	if not sm:
		sys.exit("The case " + keyword + " of addParam builds no parameter")
	args = []
	for am in re.finditer(r"//[ \t]*\$\*-(\w)[ \t]+([\w:<>]+(?:[ \t]+\w+)?)[ \t]+(\w+)(?:[ \t]*=[ \t]*([^\s/]+))?[ \t]*(?://[ \t]*([^\n]*))?", case):
		# the kind the generated parser reads: it follows the declared type (atof for a float), and some comments mark a
		# float -i (STA_WEIGHT_FACTOR, the SP_MOD_* ModifConst)
		cType = am.group(2)
		kind = "f" if ("float" in cType or "double" in cType) else ("s" if "string" in cType else am.group(1))
		args.append((kind, cType, am.group(3), (am.group(5) or "").strip()))
	checks = structChecks.get(sm.group(1))
	if checks is None:
		sys.exit("The structure " + sm.group(1) + " of " + keyword + " is not in egs_static_brick.cpp.h")
	# the generated parser is the truth (some structures were changed after generation, AREA_BOMB reads a third
	# argument its comment does not name): its reads give the arguments, the comments only their descriptions
	reads = structArgs.get(sm.group(1), {})
	if reads and sorted(reads) == list(range(len(reads))):
		described = dict((a[2], a[3]) for a in args)
		args = []
		for i in range(len(reads)):
			cType, name = reads[i]
			kind = "f" if ("float" in cType or "double" in cType) else ("s" if "string" in cType else "i")
			args.append((kind, cType, name, described.get(name, "")))
	# the parse is refused when one of these holds; keep them as the accepted argument counts
	accepted = [ n for n in range(0, 12) if not any(eval(c.replace("args.size()", str(n)).replace("&&", " and ").replace("||", " or ")) for c in checks) ]
	properties[keyword.lower()] = { "keyword": keyword, "struct": sm.group(1), "args": args, "counts": accepted }

# ---- the magic action types of the files the service builds (CMakeLists removes some of the globbed ones)
cmake = read(os.path.join(egs, "CMakeLists.txt"))
removed = set(os.path.basename(p) for p in re.findall(r"phrase_manager/(\w+\.cpp)", cmake.split("LIST(REMOVE_ITEM SRC_PHRASE_MANAGER", 1)[1].split(")", 1)[0])) if "LIST(REMOVE_ITEM SRC_PHRASE_MANAGER" in cmake else set()
magicActions = {}
for f in sorted(os.listdir(os.path.join(egs, "phrase_manager"))):
	if f.endswith(".cpp") and f not in removed:
		for name in re.findall(r"ADD_MAGIC_ACTION_TYPE\s*\(\s*\"(\w+)\"\s*\)", stripComments(read(os.path.join(egs, "phrase_manager", f)))):
			magicActions[name] = f

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "code_tables.py")
with open(out, "w", encoding="utf-8", newline="\n") as f:
	f.write("# Made by refresh_code_tables.py from the Ryzom Core code; do not edit, run it again after a change to the code.\n\n")
	f.write("FAMILY_VALUES = {\n" + "".join("\t%r: %d,\n" % (k, values[k]) for k in sorted(values)) + "}\n\n")
	f.write("FAMILIES = [\n" + "".join("\t%r,\n" % k for k in families) + "]\n\n")
	f.write("FAMILY_PREDICATES = {\n" + "".join("\t%r: %r,\n" % (k, predicates[k]) for k in sorted(predicates)) + "}\n\n")
	f.write("BRICK_TYPES = [\n" + "".join("\t%r,\n" % (t,) for t in brickTypes) + "]\n\n")
	f.write("SKILLS = [\n" + "".join("\t%r,\n" % k for k in skills) + "]\n\n")
	f.write("PROPERTIES = {\n" + "".join("\t%r: %r,\n" % (k, properties[k]) for k in sorted(properties)) + "}\n\n")
	f.write("MAGIC_ACTIONS = {\n" + "".join("\t%r: %r,\n" % (k, magicActions[k]) for k in sorted(magicActions)) + "}\n\n")
	f.write("TABLES = {\n" + "".join("\t%r: %r,\n" % (k, tables[k]) for k in sorted(tables)) + "}\n")
print("wrote " + out + ": " + str(len(families)) + " families, " + str(len(skills)) + " skills, " + str(len(properties))
	+ " property keywords, " + str(len(magicActions)) + " magic action types, " + str(len(tables)) + " conversion tables")
