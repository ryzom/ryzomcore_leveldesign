
import os

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
					entry[columns[i]] = row[i]
				table[name] = entry
	return table;

creatureFauna = loadTsvWithHeaders("creature_fauna.tsv")

for sheet in creatureFauna:
	entry = creatureFauna[sheet]
	listFolder = "R:\\leveldesign\\game_elem\\creature\\" + entry["folder"] + "\\actionlist"
	if not os.path.isdir(listFolder):
		os.makedirs(listFolder)
	actionFolder = "R:\\leveldesign\\game_elem\\creature\\" + entry["folder"] + "\\aiaction"
	attack = entry["attack"]
	if attack != "_none" and attack != "_inherit":
		with open(listFolder + "\\" + sheet + "_attack.actionlist", "w") as f:
			f.write("<?xml version=\"1.0\"?>\n")
			f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
			f.write("  <STRUCT>\n")
			f.write("    <ARRAY Name=\"actions\">\n")
			if os.path.isfile(actionFolder + "\\" + sheet + "_attack.aiaction"):
				f.write("      <ATOM Value=\"" + sheet + "_attack.aiaction\"/>\n")
			if os.path.isfile(actionFolder + "\\" + sheet + "_attack2.aiaction"):
				f.write("      <ATOM Value=\"" + sheet + "_attack2.aiaction\"/>\n")
			if not attack.startswith("_"):
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
				f.write("      <ATOM Value=\"combat_fauna_" + attack + ".aiaction\"/>\n")
			f.write("    </ARRAY>\n")
			f.write("  </STRUCT>\n")
			f.write("</FORM>\n")
			f.flush()
