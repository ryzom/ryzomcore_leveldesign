# Mission checks

Python 3 checks for a level design tree with mission primitives (`primitives/<continent>/<region>/task_*.primitive`
and friends). They read `game_elem`/`game_element` sheets, the DFN and `translation/translated/phrase_en.txt`
for the facts they compare against. Folders named `_unpublished_` are skipped.

| Script | Finds |
|---|---|
| `race_check.py ROOT` | `kill_race`/`target_race` steps bound to a region whose race no primitive of that region's folder spawns. `--races REGION...` lists the spawned races and levels of regions. |
| `scan_rewards.py PRIMITIVESDIR` | Two or more item rewards behind one `failure` marker: when a later item fails for room, the retry grants the earlier ones again. |
| `craft_titles.py PRIMITIVESDIR [--fix]` | Craft tasks whose nation title (`TEMPLATE_TASK_CRAFT_11..14_TITLE`) does not match the nation of the crafted items. |
| `dup_titles.py PRIMITIVESDIR` | Givers that list two missions under the same title (same title phrase and parameters). Hand-written missions shown one at a time through prerequisites appear here too. |
| `dedup_titles.py ROOT [--fix]` | Gives duplicate generated tasks (`TEMPLATE_TASK_*_TITLE`) unused title variants, and moves the intro variant along where it matched. Variants with the same text in a language still read the same there. |
| `ammo_scan.py ROOT [--cap BULK] [--fix]` | Craft steps whose built items exceed the bag bulk (300 by default); with `--fix`, lowers the heavy items to whole crafts that fit. |
| `mission_givers.py FILE...` | Lists the kill and target race missions per giver bot. |

Run without `--fix` first and read the list; the fixes edit the primitives in place.
