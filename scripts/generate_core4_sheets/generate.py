# Generates the bricks and phrases of Ryzom Core (see framework.py and README.md).
#
#   python generate.py                check every domain, write nothing, report what would change
#   python generate.py --write        the same, then write the sheets and remove the ones it replaces
#   python generate.py --domain fight check (or write) one domain; references to sheets of other domains then fail
#   python generate.py --complete     also require a sheet or a stated reason for every translation id, and the sheets
#                                     the code names
#   python generate.py --coverage     list the translation ids that have no sheet yet, by family prefix
#   python generate.py --atlas <dir>  read the interface atlas lists the icons are checked against from that folder, not
#                                     from the pipeline beside the leveldesign (interface_atlas.py)

import argparse, collections, importlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import framework
import interface_atlas
import plan_items

DOMAINS = [ "fight", "magic", "forage", "craft", "plans", "powers", "misc" ] # plans after craft: it checks the roots that offer its families

parser = argparse.ArgumentParser()
parser.add_argument("--write", action="store_true")
parser.add_argument("--complete", action="store_true")
parser.add_argument("--coverage", action="store_true")
parser.add_argument("--domain", action="append")
parser.add_argument("--atlas", help="the folder of the interface atlas lists " + " and ".join(interface_atlas.LISTS)
	+ " (default: " + interface_atlas.DEFAULT_FOLDER + ")")
args = parser.parse_args()
if args.atlas:
	interface_atlas.setFolder(args.atlas)

try:
	gen = framework.Generator()
	domains = args.domain or [ d for d in DOMAINS if os.path.isfile(os.path.join(HERE, "domains", d + ".py")) ]
	for d in domains:
		module = importlib.import_module("domains." + d)
		gen.domain = d
		for folder in module.OWNS:
			gen.own(folder)
		module.generate(gen)
	gen.domain = None
	gen.check(args.complete)
except (framework.Stop, plan_items.Missing) as e:
	sys.stderr.write("error: " + str(e) + "\n")
	sys.exit(1)

for n in gen.notes:
	print("note: " + n)
if args.coverage:
	left = collections.Counter()
	examples = {}
	for sheetType, i in gen.coverage():
		key = sheetType + " " + re.sub(r"[0-9_].*$", "", i)
		left[key] += 1
		examples.setdefault(key, i)
	for key, n in sorted(left.items()):
		print("no sheet yet: %-22s %5d  (%s)" % (key, n, examples[key]))
	reasons = collections.Counter(r for r in gen.excluded.values())
	for r, n in sorted(reasons.items(), key=lambda x: -x[1]):
		print("excluded %5d: %s" % (n, r))
if gen.errors:
	for e in gen.errors:
		sys.stderr.write("error: " + e + "\n")
	sys.stderr.write(str(len(gen.errors)) + " errors, nothing was written\n")
	sys.exit(1)
try:
	counts, removed = gen.write(not args.write)
except framework.Stop as e:
	sys.stderr.write("error: " + str(e) + "\n")
	sys.exit(1)
print("%s: %d bricks, %d parents, %d phrases from %s; %s" % ("written" if args.write else "dry run", len(gen.bricks), len(gen.parents),
	len(gen.phrases), ", ".join(domains), ", ".join("%d %s" % (n, k) for k, n in sorted(counts.items()))))
if removed and not args.write:
	for path in removed[:40]:
		print("would remove " + path)
