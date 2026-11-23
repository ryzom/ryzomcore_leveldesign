# The icon names of the interface atlases the client loads (texture_interfaces_dxtc.txt and texture_interfaces_v3.txt,
# a .png name standing for its .tga): every icon a sheet names must be one of them. One reader for the domains of the
# sheet generator (framework.atlasNames) and for ../generate_r2_sheets/generate_sitem.py.
#
# The lists are read from the pipeline beside the leveldesign that holds this script
# (<leveldesign>/../pipeline/install/interfaces), found from the script's place, or from the folder the --atlas option
# of generate.py or generate_sitem.py names (setFolder). A list that is missing stops the run with its path and that
# option, as raw_material_tables/make_tables.py does.

import os

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELDESIGN = os.path.normpath(os.path.join(HERE, "..", ".."))
DEFAULT_FOLDER = os.path.normpath(os.path.join(LEVELDESIGN, "..", "pipeline", "install", "interfaces"))
LISTS = [ "texture_interfaces_dxtc.txt", "texture_interfaces_v3.txt" ]

folder = DEFAULT_FOLDER
_names = None

class Missing(Exception):
	"""a list that cannot be read, with its path, the rule and the remedy"""

def setFolder(path):
	"""read the lists from this folder (the --atlas option)"""
	global folder, _names
	folder = os.path.normpath(os.path.abspath(path))
	_names = None

def names():
	"""the icon names of the lists, lower case"""
	global _names
	if _names is None:
		where = folder + ("; by default the one beside the leveldesign" if folder == DEFAULT_FOLDER else ", given by --atlas")
		result = set()
		for name in LISTS:
			path = os.path.join(folder, name)
			if not os.path.isfile(path):
				raise Missing(path + " not found: the icons are checked against the interface atlas lists of the pipeline (" + where
					+ "): build the interfaces, or pass --atlas <folder of the lists> to name another")
			try:
				with open(path, "r", encoding="utf-8-sig") as f:
					text = f.read()
			except UnicodeDecodeError as e:
				raise Missing(path + " is not UTF-8 text (" + str(e) + "): the interface atlas lists are read as the build writes them")
			for line in text.split("\n"):
				if line.strip():
					result.add(line.split()[0].lower())
		_names = result
	return _names
