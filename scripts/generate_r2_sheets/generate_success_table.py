
import os

if not os.path.isdir("../../game_elem"):
	print("Script run from wrong folder")
	exit(1)

tables = None
headers = None
valueHeaders = None
columnToTable = {}

with open("success_chances.tsv", "r") as f:
	for l in f:
		# split row and cleanup values
		row = l.split("\t")
		for i in range(0, len(row)):
			row[i] = row[i].strip()
			if len(row[i]) >= 2 and row[0] == "\"" and row[-1] == "\"":
				row[i] = row[i][1:-1]
		# process lines
		if not tables:
			tables = {}
			currentTable = None
			for i in range(0, len(row)):
				if len(row[i]) > 0:
					currentTable = {}
					currentTable["name"] = row[i]
					tables[row[i]] = currentTable
				if currentTable:
					columnToTable[i] = currentTable
					#print(str(i) + " " + str(currentTable))
		elif not headers:
			headers = row
			for i in range(0, len(row)):
				if len(headers[i]) > 0:
					if i in columnToTable:
						# add new column
						#print(columnToTable[i])
						columnToTable[i][headers[i]] = []
					else:
						for k in tables:
							tables[k][headers[i]] = []
		elif valueHeaders:
			# add row into values
			for i in range(0, len(row)):
				if len(valueHeaders[i]) > 0:
					if i in columnToTable:
						# add new column
						columnToTable[i][valueHeaders[i]] = row[i]
					else:
						for k in tables:
							tables[k][valueHeaders[i]] = row[i] 
		elif len(row[0]) == 0:
			# special values
			valueHeaders = row
		else:
			# add row into tables
			for i in range(0, len(row)):
				if len(headers[i]) > 0:
					if i in columnToTable:
						# add new column
						columnToTable[i][headers[i]] += [ row[i] ]
					else:
						for k in tables:
							tables[k][headers[i]] += [ row[i] ]

for k in tables:
	tables[k]["lists"] = []
	tables[k]["values"] = []
if headers:
	for i in range(0, len(headers)):
		if len(headers[i]) > 0:
			if i in columnToTable:
				columnToTable[i]["lists"] += [ headers[i] ]
				#print columnToTable[i]["lists"]
			else:
				for k in tables:
					tables[k]["lists"] += [ headers[i] ]
if valueHeaders:
	for i in range(0, len(valueHeaders)):
		if len(valueHeaders[i]) > 0:
			if i in columnToTable:
				columnToTable[i]["values"] += [ valueHeaders[i] ]
				#print columnToTable[i]["values"]
			else:
				for k in tables:
					tables[k]["values"] += [ valueHeaders[i] ]

#print(tables)

for k in tables:
	table = tables[k]
	rowNb = len(table[headers[0]])
	with open("../../game_element/xp_table/" + k + ".succes_chances_table", "w") as f:
		f.write("<?xml version=\"1.0\"?>\n")
		f.write("<FORM Version=\"4.0\" State=\"modified\">\n")
		f.write("  <STRUCT>\n")
		f.write("    <ARRAY Name=\"Chances\">\n")
		for i in range(0, rowNb):
			f.write("      <STRUCT>\n")
			for name in table["lists"]:
				f.write("        <ATOM Name=\"" + name + "\" Value=\"" + table[name][i] + "\"/>\n")
			f.write("      </STRUCT>\n")
		f.write("    </ARRAY>\n")
		for name in table["values"]:
			f.write("        <ATOM Name=\"" + name + "\" Value=\"" + table[name] + "\"/>\n")
		f.write("  </STRUCT>\n")
		f.write("</FORM>\n")

# end of file
