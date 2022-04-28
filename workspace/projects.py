#!/usr/bin/python
# 
# \file projects.py
# \brief Projects configuration
# \date 2010-05-24-09-19-GMT
# \author Jan Boon (Kaetemi)
# Python port of game data build pipeline.
# Projects configuration.
# 
# NeL - MMORPG Framework <http://dev.ryzom.com/projects/nel/>
# Copyright (C) 2010  Winch Gate Property Limited
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 


from scripts import *
from buildsite_local import *
import os


ProductName = "ryzom"


ProjectsToProcess = [ ]

# Common asset export and build projects
ProjectsToProcess += [ "common/interface" ]
ProjectsToProcess += [ "common/objects" ]
ProjectsToProcess += [ "common/sfx" ]
ProjectsToProcess += [ "common/fauna" ]
ProjectsToProcess += [ "common/construction" ]
ProjectsToProcess += [ "common/outgame" ]
ProjectsToProcess += [ "common/sky" ]
ProjectsToProcess += [ "common/characters" ]
ProjectsToProcess += [ "common/characters_maps_hr" ]
ProjectsToProcess += [ "common/sound" ]

# Common client data and leveldesign projects
ProjectsToProcess += [ "common/fonts" ]
ProjectsToProcess += [ "common/gamedev" ]
ProjectsToProcess += [ "common/leveldesign" ]
ProjectsToProcess += [ "common/data_common" ]
ProjectsToProcess += [ "common/exedll" ]
ProjectsToProcess += [ "common/cfg" ]

# Shard specific
ProjectsToProcess += [ "shard/data_shard" ]
ProjectsToProcess += [ "shard/data_language" ]
ProjectsToProcess += [ "shard/data_leveldesign" ]

# Ecosystem projects
ProjectsToProcess += [ "ecosystems/desert" ]
ProjectsToProcess += [ "ecosystems/jungle" ]
ProjectsToProcess += [ "ecosystems/primes_racines" ]
ProjectsToProcess += [ "ecosystems/lacustre" ]

# Continent projects
ProjectsToProcess += [ "continents/fyros" ]
ProjectsToProcess += [ "continents/tryker" ]
ProjectsToProcess += [ "continents/matis" ]
ProjectsToProcess += [ "continents/zorai" ]
ProjectsToProcess += [ "continents/fyros_newbie" ] # Depends on continents/fyros
ProjectsToProcess += [ "continents/fyros_island" ] # Depends on continents/fyros (maybe)
ProjectsToProcess += [ "continents/tryker_newbie" ] # Depends on continents/tryker
ProjectsToProcess += [ "continents/tryker_island" ] # Depends on continents/tryker
ProjectsToProcess += [ "continents/zorai_island" ] # Depends on continents/zorai (maybe)
ProjectsToProcess += [ "continents/matis_island" ] # Depends on continents/matis (maybe)
ProjectsToProcess += [ "continents/nexus" ] # Depends on continents/matis (maybe)
ProjectsToProcess += [ "continents/bagne" ]
ProjectsToProcess += [ "continents/route_gouffre" ]
ProjectsToProcess += [ "continents/terre" ]
ProjectsToProcess += [ "continents/sources" ]
ProjectsToProcess += [ "continents/newbieland" ] # Note: must be after other continents due to dependencies on fy/ma/zo/tr
ProjectsToProcess += [ "continents/kitiniere" ] # Depends on continents/terre
ProjectsToProcess += [ "continents/corrupted_moor" ] # Depends on continents/matis (maybe)
ProjectsToProcess += [ "continents/r2_desert" ] # Depends on continents/fyros (maybe)
ProjectsToProcess += [ "continents/r2_lakes" ] # Depends on continents/tryker (maybe)
ProjectsToProcess += [ "continents/r2_jungle" ] # Depends on continents/zorai (maybe)
ProjectsToProcess += [ "continents/r2_forest" ] # Depends on continents/matis (maybe)
ProjectsToProcess += [ "continents/r2_roots" ]
ProjectsToProcess += [ "continents/indoors" ] # Note: must be after other continents due to dependencies on fy/ma/zo/tr


InstallShardDataDirectories = [ ]
InstallShardDataDirectories += [ "data_common" ]
InstallShardDataDirectories += [ "data_language" ]
InstallShardDataDirectories += [ "data_leveldesign" ]
InstallShardDataDirectories += [ "data_www" ] # TODO

# [ [ "<target_package>", [ "<source_file>", "<source_file>" ] ] ] target_package under shard data, source_file under install
InstallShardDataFiles = [ ]

# [ [ "<target_package>", [ "<source_dir>", "<source_dir>" ] ] ] target_package under shard data, source_dir under install
InstallShardDataMultiDirectories = [ ]
InstallShardDataMultiDirectories += [ [ "cfg", [ ] ] ]
InstallShardDataMultiDirectories += [ [ "data_www", [ ] ] ]
InstallShardDataMultiDirectories += [ [ "data_fyros", [ "fyros_newbie_ai", "fyros_newbie_ig", "fyros_newbie_pacs", "fyros_island_ai", "fyros_island_ig", "fyros_island_pacs", "fyros_ai", "fyros_ig", "fyros_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_tryker", [ "tryker_newbie_ai", "tryker_newbie_ig", "tryker_newbie_pacs", "tryker_island_ai", "tryker_island_ig", "tryker_island_pacs", "tryker_ai", "tryker_ig", "tryker_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_zorai", [ "zorai_island_ai", "zorai_island_ig", "zorai_island_pacs", "zorai_ai", "zorai_ig", "zorai_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_matis", [ "matis_island_ai", "matis_island_ig", "matis_island_pacs", "matis_ai", "matis_ig", "matis_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_roots", [ "nexus_ai", "nexus_ig", "nexus_pacs", "bagne_ai", "bagne_ig", "bagne_pacs", "route_gouffre_ai", "route_gouffre_ig", "route_gouffre_pacs", "terre_ai", "terre_ig", "terre_pacs", "sources_ai", "sources_ig", "sources_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_newbieland", [ "newbieland_ai", "newbieland_ig", "newbieland_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_kitiniere", [ "kitiniere_ai", "kitiniere_ig", "kitiniere_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_corrupted_moor", [ "corrupted_moor_ai", "corrupted_moor_ig", "corrupted_moor_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_indoors", [ "indoors_ai", "indoors_ig", "indoors_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_pacs_prim", [ "desert_pacs_prim", "jungle_pacs_prim", "lacustre_pacs_prim", "primes_racines_pacs_prim" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_r2_desert", [ "r2_desert_ai", "r2_desert_ig", "r2_desert_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_r2_lakes", [ "r2_lakes_ai", "r2_lakes_ig", "r2_lakes_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_r2_jungle", [ "r2_jungle_ai", "r2_jungle_ig", "r2_jungle_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_r2_forest", [ "r2_forest_ai", "r2_forest_ig", "r2_forest_pacs" ] ] ]
InstallShardDataMultiDirectories += [ [ "data_r2_roots", [  "r2_roots_ai", "r2_roots_ig", "r2_roots_pacs" ] ] ]

# [ [ "<target_package>", [ "<source_dir>", "<source_dir>" ] ] ] target_dir under shard data, source_dir under primitives
InstallShardDataPrimitivesDirectories = [ ]
InstallShardDataPrimitivesDirectories += [ [ "data_game_share", [ "" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_mainland_common_primitives", [ "indoors", "test" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_r2_common_primitives", [ "r2" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_fyros_primitives", [ "fyros", "fyros/nland", "fyros/dunesofexil", "fyros/frahartowers", "fyros/imperialdunes", "fyros/oflovaksoasis", "fyros/outlawcanyon", "fyros/sawdustmines", "fyros/thesavagedunes", "fyros/thescorchedcorridor", "storyline/episode_2/fyros_island" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_tryker_primitives", [ "tryker", "tryker/nland", "tryker/bountybeaches", "tryker/dewdrops", "tryker/enchantedisle", "tryker/lagoonsofloria", "tryker/libertylake", "tryker/restingwater", "tryker/thefount", "tryker/windsofmuse", "storyline/episode_2/tryker_island" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_zorai_primitives", [ "zorai", "zorai/nland", "zorai/citiesofintuition", "zorai/groveofumbra", "zorai/havenofpurity", "zorai/knotofdementia", "zorai/maidengrove", "zorai/thevoid" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_matis_primitives", [ "matis", "matis/nland", "matis/matis_island", "matis/fleetinggarden", "matis/groveofconfusion", "matis/hereticshovel", "matis/hiddensource", "matis/knollofdissent", "matis/majesticgarden", "matis/upperbog", "storyline/episode_2/matis_island" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_roots_primitives", [ "primeroots", "primeroots/nexus", "primeroots/forbidden_depths", "primeroots/gate_of_obscurity", "primeroots/the_abyss_of_ichor", "primeroots/the_elusive_forest", "primeroots/the_land_of_continuty", "primeroots/the_sunken_city", "primeroots/the_trench_of_trials", "primeroots/the_under_spring", "primeroots/the_windy_gate" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_newbieland_primitives", [ "newbieland" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_kitiniere_primitives", [ "_unpublished_/kitinieres/kitiniere_250" ] ] ]
InstallShardDataPrimitivesDirectories += [ [ "data_corrupted_moor_primitives", [ "_unpublished_/corrupted_moor" ] ] ]

# [ [ "<target_package>", [ "<target_executable>", "<source_executable>" ], [ "<default_config>", "<default_config>" ], [ "<data_file>", "<data_file>" ] ] ]
psFileList = [ ]
if os.path.isdir(InstallDirectory + "/data_shard"):
	psFileList = os.listdir(InstallDirectory + "/data_shard")
psDatasets = [ "data_shard/datasets.packed_sheets" ]
psIOS = [ "data_shard/ios_sheets.packed_sheets" ]
psGPMS = [ "data_shard/gpms.packed_sheets" ]
psContinents = [ "data_shard/continents.packed_sheets" ]
psEGS = [ ]
for fileName in psFileList:
	if fileName != ".svn" and fileName != ".." and fileName != "." and fileName != "*.*":
		if ("egs_" in fileName) or ("egs." in fileName):
			psEGS += [ "data_shard/" + fileName ]
psLightCycles = [ "data_shard/light_cycles.packed_sheets" ]
psAIS = [ ]
for fileName in psFileList:
	if fileName != ".svn" and fileName != ".." and fileName != "." and fileName != "*.*":
		if ("ais_" in fileName) or ("ais." in fileName):
			psAIS += [ "data_shard/" + fileName ]
InstallShardDataExecutables = [ ]
# Unifier
InstallShardDataExecutables += [ [ "service_ryzom_admin_service", [ "ryzom_admin_service", "ryzom_admin_service" ], [ "ryzom_as.cfg" ], [ ] ] ]
InstallShardDataExecutables += [ [ "service_shard_unifier_service", [ "shard_unifier_service", "ryzom_shard_unifier_service" ], [ "shard_unifier_service.cfg" ], [ "data_shard/reserved_names.xml", "data_shard/dev_gm_names.xml", "data_shard/invalid_entity_names.txt" ] ] ]
InstallShardDataExecutables += [ [ "service_mail_forum_service", [ "mail_forum_service", "ryzom_mail_forum_service" ], [ "mail_forum_service.cfg" ], [ ] ] ]
# Backup
InstallShardDataExecutables += [ [ "service_logger_service", [ "logger_service", "ryzom_logger_service" ], [ "logger_service.cfg" ], [ ] ] ]
InstallShardDataExecutables += [ [ "service_backup_service", [ "backup_service", "ryzom_backup_service" ], [ "backup_service.cfg" ], [ ] ] ]
InstallShardDataExecutables += [ [ "service_pd_support_service", [ "pd_support_service", "ryzom_pd_support_service" ], [ ], [ ] ] ]
# LAS
# InstallShardDataExecutables += [ [ "service_log_analyser_service", [ "log_analyser_service", "ryzom_log_analyser_service" ], [ "log_analyser_service.cfg" ], [ ] ] ]
# Mainland
InstallShardDataExecutables += [ [ "service_ryzom_naming_service", [ "ryzom_naming_service", "ryzom_naming_service" ], [ "naming_service.cfg" ], [ ] ] ]
InstallShardDataExecutables += [ [ "service_ryzom_welcome_service", [ "ryzom_welcome_service", "ryzom_welcome_service" ], [ "welcome_service.cfg" ], [ ] ] ]
InstallShardDataExecutables += [ [ "service_tick_service", [ "tick_service", "ryzom_tick_service" ], [ "tick_service.cfg" ], [ ] + psDatasets ] ]
InstallShardDataExecutables += [ [ "service_mirror_service", [ "mirror_service", "ryzom_mirror_service" ], [ "mirror_service.cfg" ], [ ] + psDatasets ] ]
InstallShardDataExecutables += [ [ "service_input_output_service", [ "input_output_service", "ryzom_ios_service" ], [ "input_output_service.cfg" ], [ ] + psDatasets + psIOS ] ]
InstallShardDataExecutables += [ [ "service_gpm_service", [ "gpm_service", "ryzom_gpm_service" ], [ "gpm_service.cfg" ], [ ] + psDatasets + psGPMS + psContinents ] ]
InstallShardDataExecutables += [ [ "service_session_browser_server", [ "session_browser_server", "ryzom_session_browser_service" ], [ ], [ ] ] ]
InstallShardDataExecutables += [ [ "service_entities_game_service", [ "entities_game_service", "ryzom_entities_game_service" ], [ "entities_game_service.cfg" ], [ "data_shard/shop_category.cfg", "data_shard/client_commands_privileges.txt", "data_shard/client_commands_privileges_open.txt", "data_shard/named_items.txt", "data_shard/mission_queues.txt", "data_shard/game_event.txt" ] + psEGS + psDatasets + psLightCycles ] ]
InstallShardDataExecutables += [ [ "service_ai_service", [ "ai_service", "ryzom_ai_service" ], [ "ai_service.cfg" ], [ "data_shard/shop_category.cfg" ] + psAIS + psDatasets + psLightCycles ] ]
InstallShardDataExecutables += [ [ "service_frontend_service", [ "frontend_service", "ryzom_frontend_service" ], [ "frontend_service.cfg" ], [ ] + psDatasets ] ]
# Ring
InstallShardDataExecutables += [ [ "service_dynamic_scenario_service", [ "dynamic_scenario_service", "ryzom_dynamic_scenario_service" ], [ "dynamic_scenario_service.cfg" ], [ "r2_desert_pz/r2_desert_islands.xml", "r2_lakes_pz/r2_lakes_islands.xml", "r2_jungle_pz/r2_jungle_islands.xml", "r2_forest_pz/r2_forest_islands.xml", "r2_roots_pz/r2_roots_islands.xml" ] ] ]


WorldEditEcosystems = [ ]
WorldEditEcosystems += [ [ "desert", [ "fyros", "fyros_island", "fyros_newbie", "r2_desert" ] ] ]
WorldEditEcosystems += [ [ "jungle", [ "indoors", "zorai", "zorai_island", "matis", "matis_island", "nexus", "newbieland", "corrupted_moor", "r2_jungle", "r2_forest" ] ] ]
WorldEditEcosystems += [ [ "primes_racines", [ "bagne", "route_gouffre", "terre", "sources", "kitiniere", "r2_roots" ] ] ]
WorldEditEcosystems += [ [ "lacustre", [ "tryker", "tryker_island", "tryker_newbie", "r2_lakes" ] ] ]


InstallClientData = [ ]

ICMain = { }
ICMain["Name"] = "main"
ICMain["UnpackTo"] = None
ICMain["IsOptional"] = 0
ICMain["IsIncremental"] = 1
ICMain["StreamedPackages"] = False
ICMain["Packages"] = [ ]
ICMain["Packages"] += [ [ "data_common", [ ] ] ]
ICMain["Packages"] += [ [ "gamedev", [ ] ] ]
ICMain["Packages"] += [ [ "interfaces", [ ] ] ]
ICMain["Packages"] += [ [ "leveldesign", [ ] ] ]
ICMain["Packages"] += [ [ "outgame", [ ] ] ]
ICMain["Refs"] = [ ]
ICMain["Refs"] += [ "cfg" ]
ICMain["Refs"] += [ "exedll" ]
ICMain["Refs"] += [ "fonts" ]
ICMain["Refs"] += [ "packedsheets" ]
InstallClientData += [ ICMain ]

ICMainCfg = { }
ICMainCfg["Name"] = "main_cfg"
ICMainCfg["UnpackTo"] = "cfg" # ->  = "./cfg/"
ICMainCfg["IsOptional"] = 0
ICMainCfg["IsIncremental"] = 0
ICMainCfg["StreamedPackages"] = False
ICMainCfg["Packages"] = [ [ "cfg", [ ] ] ]
ICMainCfg["Refs"] = [ ]
InstallClientData += [ ICMainCfg ]

ICMainExedll = { }
ICMainExedll["Name"] = "main_exedll"
ICMainExedll["UnpackTo"] = "" # -> "./", to not unpack set to None
ICMainExedll["IsOptional"] = 0
ICMainExedll["IsIncremental"] = 0
ICMainExedll["StreamedPackages"] = False
ICMainExedll["Packages"] = [ [ "exedll", [ ] ] ]
ICMainExedll["Refs"] = [ ]
InstallClientData += [ ICMainExedll ]

ICMainFonts = { }
ICMainFonts["Name"] = "main_fonts"
ICMainFonts["UnpackTo"] = "data/fonts"
ICMainFonts["IsOptional"] = 0
ICMainFonts["IsIncremental"] = 0
ICMainFonts["StreamedPackages"] = False
ICMainFonts["Packages"] = [ [ "fonts", [ ] ] ]
ICMainFonts["Refs"] = [ ]
InstallClientData += [ ICMainFonts ]

ICMainPacked = { }
ICMainPacked["Name"] = "main_packed"
ICMainPacked["UnpackTo"] = "data"
ICMainPacked["IsOptional"] = 0
ICMainPacked["IsIncremental"] = 0
ICMainPacked["StreamedPackages"] = False
ICMainPacked["Packages"] = [ [ "packedsheets", [ ] ] ]
ICMainPacked["Refs"] = [ ]
InstallClientData += [ ICMainPacked ]

ICUser = { }
ICUser["Name"] = "user"
ICUser["UnpackTo"] = "user"
ICUser["IsOptional"] = 0
ICUser["IsIncremental"] = 1
ICUser["StreamedPackages"] = False
ICUser["Packages"] = [ [ "user", [ ] ] ]
ICUser["Refs"] = [ ]
InstallClientData += [ ICUser ]

ICExamples = { }
ICExamples["Name"] = "examples"
ICExamples["UnpackTo"] = "examples"
ICExamples["IsOptional"] = 0
ICExamples["IsIncremental"] = 1
ICExamples["StreamedPackages"] = False
ICExamples["Packages"] = [ [ "examples", [ ] ] ]
ICExamples["Refs"] = [ ]
InstallClientData += [ ICExamples ]

ICCommon = { }
ICCommon["Name"] = "common"
ICCommon["UnpackTo"] = None
ICCommon["IsOptional"] = 0
ICCommon["IsIncremental"] = 1
ICCommon["StreamedPackages"] = False
ICCommon["Packages"] = [ ]
ICCommon["Packages"] += [ [ "construction", [ ] ] ]
ICCommon["Packages"] += [ [ "objects", [ ] ] ]
ICCommon["Packages"] += [ [ "fauna_animations", [ ] ] ]
ICCommon["Packages"] += [ [ "fauna_maps", [ ] ] ]
ICCommon["Packages"] += [ [ "fauna_shapes", [ ] ] ]
ICCommon["Packages"] += [ [ "fauna_skeletons", [ ] ] ]
ICCommon["Packages"] += [ [ "fauna_swt", [ ] ] ] # CHECK IF NECESSARY
ICCommon["Packages"] += [ [ "sfx", [ ] ] ]
ICCommon["Packages"] += [ [ "sky", [ ] ] ]
ICCommon["Packages"] += [ [ "sound", [ ] ] ]
ICCommon["Refs"] = [ ]
InstallClientData += [ ICCommon ]

ICCharacterArmors = [ ]
ICCharacterArmors += [ "zo_hom_visage" ]
ICCharacterArmors += [ "zo_hom_underwear" ]
ICCharacterArmors += [ "zo_hom_civil01" ]
ICCharacterArmors += [ "zo_hom_cheveux" ]
ICCharacterArmors += [ "zo_hom_caster01" ]
ICCharacterArmors += [ "zo_hom_armor01" ]
ICCharacterArmors += [ "zo_hom_armor00" ]
ICCharacterArmors += [ "zo_hof_visage" ]
ICCharacterArmors += [ "zo_hof_underwear" ]
ICCharacterArmors += [ "zo_hof_civil01" ]
ICCharacterArmors += [ "zo_hof_cheveux" ]
ICCharacterArmors += [ "zo_hof_caster01" ]
ICCharacterArmors += [ "zo_hof_armor01" ]
ICCharacterArmors += [ "zo_hof_armor00" ]
ICCharacterArmors += [ "zo_casque01" ]
ICCharacterArmors += [ "tr_hom_visage" ]
ICCharacterArmors += [ "tr_hom_underwear" ]
ICCharacterArmors += [ "tr_hom_refugee" ]
ICCharacterArmors += [ "tr_hom_civil01" ]
ICCharacterArmors += [ "tr_hom_cheveux" ]
ICCharacterArmors += [ "tr_hom_caster01" ]
ICCharacterArmors += [ "tr_hom_armor01" ]
ICCharacterArmors += [ "tr_hom_armor00" ]
ICCharacterArmors += [ "tr_hof_visage" ]
ICCharacterArmors += [ "tr_hof_underwear" ]
ICCharacterArmors += [ "tr_hof_refugee" ]
ICCharacterArmors += [ "tr_hof_civil01" ]
ICCharacterArmors += [ "tr_hof_cheveux" ]
ICCharacterArmors += [ "tr_hof_caster01" ]
ICCharacterArmors += [ "tr_hof_armor01" ]
ICCharacterArmors += [ "tr_hof_armor00" ]
ICCharacterArmors += [ "tr_casque01" ]
ICCharacterArmors += [ "ma_hom_visage" ]
ICCharacterArmors += [ "ma_hom_underwear" ]
ICCharacterArmors += [ "ma_hom_civil01" ]
ICCharacterArmors += [ "ma_hom_cheveux" ]
ICCharacterArmors += [ "ma_hom_caster01" ]
ICCharacterArmors += [ "ma_hom_armor01" ]
ICCharacterArmors += [ "ma_hom_armor00" ]
ICCharacterArmors += [ "ma_hof_visage" ]
ICCharacterArmors += [ "ma_hof_underwear" ]
ICCharacterArmors += [ "ma_hof_civil01" ]
ICCharacterArmors += [ "ma_hof_cheveux" ]
ICCharacterArmors += [ "ma_hof_caster01" ]
ICCharacterArmors += [ "ma_hof_casque01" ]
ICCharacterArmors += [ "ma_hof_armor04" ]
ICCharacterArmors += [ "ma_hof_armor01" ]
ICCharacterArmors += [ "ma_hof_armor00" ]
ICCharacterArmors += [ "fy_hom_visage" ]
ICCharacterArmors += [ "fy_hom_underwear" ]
ICCharacterArmors += [ "fy_hom_ruflaket" ]
ICCharacterArmors += [ "fy_hom_civil01" ]
ICCharacterArmors += [ "fy_hom_cheveux" ]
ICCharacterArmors += [ "fy_hom_caster01" ]
ICCharacterArmors += [ "fy_hom_barman" ]
ICCharacterArmors += [ "fy_hom_armor01" ]
ICCharacterArmors += [ "fy_hom_armor00" ]
ICCharacterArmors += [ "fy_hof_visage" ]
ICCharacterArmors += [ "fy_hof_underwear" ]
ICCharacterArmors += [ "fy_hof_civil01" ]
ICCharacterArmors += [ "fy_hof_cheveux" ]
ICCharacterArmors += [ "fy_hof_caster01" ]
ICCharacterArmors += [ "fy_hof_armor01" ]
ICCharacterArmors += [ "fy_hof_armor00" ]
ICCharacterArmors += [ "ge_hof_armor02" ]
ICCharacterArmors += [ "ge_hof_armor03" ]
ICCharacterArmors += [ "ge_hof_armor04" ]
ICCharacterArmors += [ "ge_hof_caster00" ]
ICCharacterArmors += [ "ge_hom_armor02" ]
ICCharacterArmors += [ "ge_hom_armor03" ]
ICCharacterArmors += [ "ge_hom_armor04" ]
ICCharacterArmors += [ "ge_hom_caster00" ]
ICCharacter = { }
ICCharacter["Name"] = "character"
ICCharacter["UnpackTo"] = None
ICCharacter["IsOptional"] = 0
ICCharacter["IsIncremental"] = 1
ICCharacter["StreamedPackages"] = False
ICCharacter["Packages"] = [ ]
ICCharacter["Packages"] += [ [ "characters_swt", [ ] ] ]
ICCharacter["Packages"] += [ [ "characters_skeletons", [ ] ] ]
ICCharacter["Packages"] += [ [ "characters_shapes", [ ] ] ]
ICCharacter["Packages"] += [ [ "characters_animations", [ ] ] ]
ICCharacterMapsConditions = [ ]
for armor in ICCharacterArmors:
	ICCharacterMapsConditions += [ "--ifnot" ]
	ICCharacterMapsConditions += [ armor + "*" ]
ICCharacter["Packages"] += [ [ "characters_maps_hr", [ "characters_maps_hr.bnp" ] + ICCharacterMapsConditions, "characters.hlsbank" ] ]
for armor in ICCharacterArmors:
	ICCharacter["Packages"] += [ [ "characters_maps_hr", [ "characters_maps_" + armor + "_hr.bnp", "--if", armor + "*" ], "characters.hlsbank" ] ]
# ICCharacter["Packages"] += [ [ "characters_maps_hr", [ "characters_hlsbank.bnp", "--if", "*.hlsbank" ] ] ]
ICCharacter["Refs"] = [ ]
InstallClientData += [ ICCharacter ]

# ICCharacterMaps = { }
# ICCharacterMaps["Name"] = "character_maps"
# ICCharacterMaps["UnpackTo"] = None
# ICCharacterMaps["IsOptional"] = 0
# ICCharacterMaps["IsIncremental"] = 1
# ICCharacterMaps["StreamedPackages"] = True
# ICCharacterMaps["Packages"] = [ ]
# ICCharacterMaps["Packages"] += [ [ "characters_maps_hr", [ "characters_maps_hr.snp", "-ifnot", "*.hlsbank" ] ] ]
# ICCharacterMaps["Refs"] = [ ]
# InstallClientData += [ ICCharacterMaps ]

ICEsPrimesRacines = { }
ICEsPrimesRacines["Name"] = "es_primes_racines"
ICEsPrimesRacines["UnpackTo"] = None
ICEsPrimesRacines["IsOptional"] = 0
ICEsPrimesRacines["IsIncremental"] = 1
ICEsPrimesRacines["StreamedPackages"] = False
ICEsPrimesRacines["Packages"] = [ ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_vegetable_sets", [ ] ] ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_vegetables", [ ] ] ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_tiles", [ ] ] ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_shapes", [ ] ] ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_pacs_prim", [ ] ] ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_maps", [ ] ] ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_lightmaps", [ ] ] ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_displaces", [ ] ] ]
ICEsPrimesRacines["Packages"] += [ [ "primes_racines_bank", [ ] ] ]
ICEsPrimesRacines["Refs"] = [ ]
InstallClientData += [ ICEsPrimesRacines ]

ICEsDesert = { }
ICEsDesert["Name"] = "es_desert"
ICEsDesert["UnpackTo"] = None
ICEsDesert["IsOptional"] = 0 # 1
ICEsDesert["IsIncremental"] = 1
ICEsDesert["StreamedPackages"] = False
ICEsDesert["Packages"] = [ ]
ICEsDesert["Packages"] += [ [ "desert_vegetable_sets", [ ] ] ]
ICEsDesert["Packages"] += [ [ "desert_vegetables", [ ] ] ]
ICEsDesert["Packages"] += [ [ "desert_tiles", [ ] ] ]
ICEsDesert["Packages"] += [ [ "desert_shapes", [ ] ] ]
ICEsDesert["Packages"] += [ [ "desert_pacs_prim", [ ] ] ]
ICEsDesert["Packages"] += [ [ "desert_maps", [ ] ] ]
ICEsDesert["Packages"] += [ [ "desert_lightmaps", [ ] ] ]
ICEsDesert["Packages"] += [ [ "desert_displaces", [ ] ] ]
ICEsDesert["Packages"] += [ [ "desert_bank", [ ] ] ]
ICEsDesert["Refs"] = [ ]
InstallClientData += [ ICEsDesert ]

ICEsLacustre = { }
ICEsLacustre["Name"] = "es_lacustre"
ICEsLacustre["UnpackTo"] = None
ICEsLacustre["IsOptional"] = 0 # 1
ICEsLacustre["IsIncremental"] = 1
ICEsLacustre["StreamedPackages"] = False
ICEsLacustre["Packages"] = [ ]
ICEsLacustre["Packages"] += [ [ "lacustre_vegetable_sets", [ ] ] ]
ICEsLacustre["Packages"] += [ [ "lacustre_vegetables", [ ] ] ]
ICEsLacustre["Packages"] += [ [ "lacustre_tiles", [ ] ] ]
ICEsLacustre["Packages"] += [ [ "lacustre_shapes", [ ] ] ]
ICEsLacustre["Packages"] += [ [ "lacustre_pacs_prim", [ ] ] ]
ICEsLacustre["Packages"] += [ [ "lacustre_maps", [ ] ] ]
ICEsLacustre["Packages"] += [ [ "lacustre_lightmaps", [ ] ] ]
ICEsLacustre["Packages"] += [ [ "lacustre_displaces", [ ] ] ]
ICEsLacustre["Packages"] += [ [ "lacustre_bank", [ ] ] ]
ICEsLacustre["Refs"] = [ ]
InstallClientData += [ ICEsLacustre ]

ICEsJungle = { }
ICEsJungle["Name"] = "es_jungle"
ICEsJungle["UnpackTo"] = None
ICEsJungle["IsOptional"] = 0 # 1
ICEsJungle["IsIncremental"] = 1
ICEsJungle["StreamedPackages"] = False
ICEsJungle["Packages"] = [ ]
ICEsJungle["Packages"] += [ [ "jungle_vegetable_sets", [ ] ] ]
ICEsJungle["Packages"] += [ [ "jungle_vegetables", [ ] ] ]
ICEsJungle["Packages"] += [ [ "jungle_tiles", [ ] ] ]
ICEsJungle["Packages"] += [ [ "jungle_shapes", [ ] ] ]
ICEsJungle["Packages"] += [ [ "jungle_pacs_prim", [ ] ] ]
ICEsJungle["Packages"] += [ [ "jungle_maps", [ ] ] ]
ICEsJungle["Packages"] += [ [ "jungle_lightmaps", [ ] ] ]
ICEsJungle["Packages"] += [ [ "jungle_displaces", [ ] ] ]
ICEsJungle["Packages"] += [ [ "jungle_bank", [ ] ] ]
ICEsJungle["Refs"] = [ ]
InstallClientData += [ ICEsJungle ]

ICFyros = { }
ICFyros["Name"] = "fyros"
ICFyros["UnpackTo"] = None
ICFyros["IsOptional"] = 0 # 1
ICFyros["IsIncremental"] = 1
ICFyros["StreamedPackages"] = False
ICFyros["Packages"] = [ ]
ICFyros["Packages"] += [ [ "fyros_zones", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_shapes", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_pacs", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_maps", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_lightmaps", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_ig", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_newbie_zones", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_newbie_pacs", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_newbie_ig", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_island_zones", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_island_pacs", [ ] ] ]
ICFyros["Packages"] += [ [ "fyros_island_ig", [ ] ] ]
ICFyros["Refs"] = [ ]
InstallClientData += [ ICFyros ]

ICMatis = { }
ICMatis["Name"] = "matis"
ICMatis["UnpackTo"] = None
ICMatis["IsOptional"] = 0 # 1
ICMatis["IsIncremental"] = 1
ICMatis["StreamedPackages"] = False
ICMatis["Packages"] = [ ]
ICMatis["Packages"] += [ [ "matis_zones", [ ] ] ]
ICMatis["Packages"] += [ [ "matis_shapes", [ ] ] ]
ICMatis["Packages"] += [ [ "matis_pacs", [ ] ] ]
ICMatis["Packages"] += [ [ "matis_maps", [ ] ] ]
ICMatis["Packages"] += [ [ "matis_lightmaps", [ ] ] ]
ICMatis["Packages"] += [ [ "matis_ig", [ ] ] ]
ICMatis["Packages"] += [ [ "matis_island_zones", [ ] ] ]
ICMatis["Packages"] += [ [ "matis_island_pacs", [ ] ] ]
ICMatis["Packages"] += [ [ "matis_island_ig", [ ] ] ]
ICMatis["Refs"] = [ ]
InstallClientData += [ ICMatis ]

ICZorai = { }
ICZorai["Name"] = "zorai"
ICZorai["UnpackTo"] = None
ICZorai["IsOptional"] = 0 # 1
ICZorai["IsIncremental"] = 1
ICZorai["StreamedPackages"] = False
ICZorai["Packages"] = [ ]
ICZorai["Packages"] += [ [ "zorai_zones", [ ] ] ]
ICZorai["Packages"] += [ [ "zorai_shapes", [ ] ] ]
ICZorai["Packages"] += [ [ "zorai_pacs", [ ] ] ]
ICZorai["Packages"] += [ [ "zorai_maps", [ ] ] ]
ICZorai["Packages"] += [ [ "zorai_lightmaps", [ ] ] ]
ICZorai["Packages"] += [ [ "zorai_ig", [ ] ] ]
ICZorai["Packages"] += [ [ "zorai_island_zones", [ ] ] ]
ICZorai["Packages"] += [ [ "zorai_island_pacs", [ ] ] ]
ICZorai["Packages"] += [ [ "zorai_island_ig", [ ] ] ]
ICZorai["Refs"] = [ ]
InstallClientData += [ ICZorai ]

ICTryker = { }
ICTryker["Name"] = "tryker"
ICTryker["UnpackTo"] = None
ICTryker["IsOptional"] = 0 # 1
ICTryker["IsIncremental"] = 1
ICTryker["StreamedPackages"] = False
ICTryker["Packages"] = [ ]
ICTryker["Packages"] += [ [ "tryker_zones", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_shapes", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_pacs", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_maps", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_lightmaps", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_ig", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_newbie_zones", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_newbie_shapes", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_newbie_pacs", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_newbie_ig", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_island_zones", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_island_shapes", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_island_pacs", [ ] ] ]
ICTryker["Packages"] += [ [ "tryker_island_ig", [ ] ] ]
ICTryker["Refs"] = [ ]
InstallClientData += [ ICTryker ]

ICSources = { }
ICSources["Name"] = "sources"
ICSources["UnpackTo"] = None
ICSources["IsOptional"] = 0 # 1
ICSources["IsIncremental"] = 1
ICSources["StreamedPackages"] = False
ICSources["Packages"] = [ ]
ICSources["Packages"] += [ [ "sources_zones", [ ] ] ]
ICSources["Packages"] += [ [ "sources_shapes", [ ] ] ]
ICSources["Packages"] += [ [ "sources_pacs", [ ] ] ]
ICSources["Packages"] += [ [ "sources_maps", [ ] ] ]
ICSources["Packages"] += [ [ "sources_lightmaps", [ ] ] ]
ICSources["Packages"] += [ [ "sources_ig", [ ] ] ]
ICSources["Refs"] = [ ]
InstallClientData += [ ICSources ]

ICRouteGouffre = { }
ICRouteGouffre["Name"] = "route_gouffre"
ICRouteGouffre["UnpackTo"] = None
ICRouteGouffre["IsOptional"] = 0 # 1
ICRouteGouffre["IsIncremental"] = 1
ICRouteGouffre["StreamedPackages"] = False
ICRouteGouffre["Packages"] = [ ]
ICRouteGouffre["Packages"] += [ [ "route_gouffre_zones", [ ] ] ]
ICRouteGouffre["Packages"] += [ [ "route_gouffre_shapes", [ ] ] ]
ICRouteGouffre["Packages"] += [ [ "route_gouffre_pacs", [ ] ] ]
ICRouteGouffre["Packages"] += [ [ "route_gouffre_maps", [ ] ] ]
ICRouteGouffre["Packages"] += [ [ "route_gouffre_lightmaps", [ ] ] ]
ICRouteGouffre["Packages"] += [ [ "route_gouffre_ig", [ ] ] ]
ICRouteGouffre["Refs"] = [ ]
InstallClientData += [ ICRouteGouffre ]

ICBagne = { }
ICBagne["Name"] = "bagne"
ICBagne["UnpackTo"] = None
ICBagne["IsOptional"] = 0 # 1
ICBagne["IsIncremental"] = 1
ICBagne["StreamedPackages"] = False
ICBagne["Packages"] = [ ]
ICBagne["Packages"] += [ [ "bagne_zones", [ ] ] ]
ICBagne["Packages"] += [ [ "bagne_shapes", [ ] ] ]
ICBagne["Packages"] += [ [ "bagne_pacs", [ ] ] ]
ICBagne["Packages"] += [ [ "bagne_maps", [ ] ] ]
ICBagne["Packages"] += [ [ "bagne_lightmaps", [ ] ] ]
ICBagne["Packages"] += [ [ "bagne_ig", [ ] ] ]
ICBagne["Refs"] = [ ]
InstallClientData += [ ICBagne ]

ICTerre = { }
ICTerre["Name"] = "terre"
ICTerre["UnpackTo"] = None
ICTerre["IsOptional"] = 0 # 1
ICTerre["IsIncremental"] = 1
ICTerre["StreamedPackages"] = False
ICTerre["Packages"] = [ ]
ICTerre["Packages"] += [ [ "terre_zones", [ ] ] ]
ICTerre["Packages"] += [ [ "terre_shapes", [ ] ] ]
ICTerre["Packages"] += [ [ "terre_pacs", [ ] ] ]
ICTerre["Packages"] += [ [ "terre_maps", [ ] ] ]
ICTerre["Packages"] += [ [ "terre_lightmaps", [ ] ] ]
ICTerre["Packages"] += [ [ "terre_ig", [ ] ] ]
ICTerre["Refs"] = [ ]
InstallClientData += [ ICTerre ]

ICNexus = { }
ICNexus["Name"] = "nexus"
ICNexus["UnpackTo"] = None
ICNexus["IsOptional"] = 0 # 1
ICNexus["IsIncremental"] = 1
ICNexus["StreamedPackages"] = False
ICNexus["Packages"] = [ ]
ICNexus["Packages"] += [ [ "nexus_zones", [ ] ] ]
ICNexus["Packages"] += [ [ "nexus_shapes", [ ] ] ]
ICNexus["Packages"] += [ [ "nexus_pacs", [ ] ] ]
ICNexus["Packages"] += [ [ "nexus_maps", [ ] ] ]
ICNexus["Packages"] += [ [ "nexus_lightmaps", [ ] ] ]
ICNexus["Packages"] += [ [ "nexus_ig", [ ] ] ]
ICNexus["Refs"] = [ ]
InstallClientData += [ ICNexus ]

ICNewbieland = { }
ICNewbieland["Name"] = "newbieland"
ICNewbieland["UnpackTo"] = None
ICNewbieland["IsOptional"] = 0 # 1
ICNewbieland["IsIncremental"] = 1
ICNewbieland["StreamedPackages"] = False
ICNewbieland["Packages"] = [ ]
ICNewbieland["Packages"] += [ [ "newbieland_zones", [ ] ] ]
ICNewbieland["Packages"] += [ [ "newbieland_shapes", [ ] ] ]
ICNewbieland["Packages"] += [ [ "newbieland_pacs", [ ] ] ]
ICNewbieland["Packages"] += [ [ "newbieland_maps", [ ] ] ]
ICNewbieland["Packages"] += [ [ "newbieland_ig", [ ] ] ]
ICNewbieland["Refs"] = [ ]
InstallClientData += [ ICNewbieland ]

ICKitiniere = { }
ICKitiniere["Name"] = "kitiniere"
ICKitiniere["UnpackTo"] = None
ICKitiniere["IsOptional"] = 0 # 1
ICKitiniere["IsIncremental"] = 1
ICKitiniere["StreamedPackages"] = False
ICKitiniere["Packages"] = [ ]
ICKitiniere["Packages"] += [ [ "kitiniere_zones", [ ] ] ]
ICKitiniere["Packages"] += [ [ "kitiniere_shapes", [ ] ] ]
ICKitiniere["Packages"] += [ [ "kitiniere_pacs", [ ] ] ]
ICKitiniere["Packages"] += [ [ "kitiniere_maps", [ ] ] ]
ICKitiniere["Packages"] += [ [ "kitiniere_lightmaps", [ ] ] ]
ICKitiniere["Packages"] += [ [ "kitiniere_ig", [ ] ] ]
ICKitiniere["Refs"] = [ ]
InstallClientData += [ ICKitiniere ]

ICCorruptedMoor = { }
ICCorruptedMoor["Name"] = "corrupted_moor"
ICCorruptedMoor["UnpackTo"] = None
ICCorruptedMoor["IsOptional"] = 0 # 1
ICCorruptedMoor["IsIncremental"] = 1
ICCorruptedMoor["StreamedPackages"] = False
ICCorruptedMoor["Packages"] = [ ]
ICCorruptedMoor["Packages"] += [ [ "corrupted_moor_zones", [ ] ] ]
ICCorruptedMoor["Packages"] += [ [ "corrupted_moor_shapes", [ ] ] ]
ICCorruptedMoor["Packages"] += [ [ "corrupted_moor_pacs", [ ] ] ]
ICCorruptedMoor["Packages"] += [ [ "corrupted_moor_maps", [ ] ] ]
# ICCorruptedMoor["Packages"] += [ [ "corrupted_moor_lightmaps", [ ] ] ]
ICCorruptedMoor["Packages"] += [ [ "corrupted_moor_ig", [ ] ] ]
ICCorruptedMoor["Refs"] = [ ]
InstallClientData += [ ICCorruptedMoor ]

ICIndoors = { }
ICIndoors["Name"] = "indoors"
ICIndoors["UnpackTo"] = None
ICIndoors["IsOptional"] = 0 # 1
ICIndoors["IsIncremental"] = 1
ICIndoors["StreamedPackages"] = False
ICIndoors["Packages"] = [ ]
ICIndoors["Packages"] += [ [ "indoors_shapes", [ ] ] ]
ICIndoors["Packages"] += [ [ "indoors_pacs", [ ] ] ]
ICIndoors["Packages"] += [ [ "indoors_lightmaps", [ ] ] ]
ICIndoors["Packages"] += [ [ "indoors_ig", [ ] ] ]
ICIndoors["Refs"] = [ ]
InstallClientData += [ ICIndoors ]

ICR2 = { }
ICR2["Name"] = "r2"
ICR2["UnpackTo"] = None
ICR2["IsOptional"] = 0 # 1
ICR2["IsIncremental"] = 1
ICR2["StreamedPackages"] = False
ICR2["Packages"] = [ ]
ICR2["Packages"] += [ [ "r2_misc", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_jungle", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_lakes", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_desert", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_roots", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_forest", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_lakes2", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_jungle2", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_forest2", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_desert2", [ ] ] ]
# ICR2["Packages"] += [ [ "r2_roots2", [ ] ] ]
ICR2["Packages"] += [ [ "r2_forest_zones", [ ] ] ]
ICR2["Packages"] += [ [ "r2_desert_zones", [ ] ] ]
ICR2["Packages"] += [ [ "r2_roots_zones", [ ] ] ]
ICR2["Packages"] += [ [ "r2_lakes_zones", [ ] ] ]
ICR2["Packages"] += [ [ "r2_jungle_zones", [ ] ] ]
ICR2["Packages"] += [ [ "r2_forest_ig", [ ] ] ]
ICR2["Packages"] += [ [ "r2_desert_ig", [ ] ] ]
ICR2["Packages"] += [ [ "r2_roots_ig", [ ] ] ]
ICR2["Packages"] += [ [ "r2_lakes_ig", [ ] ] ]
ICR2["Packages"] += [ [ "r2_jungle_ig", [ ] ] ]
ICR2["Packages"] += [ [ "r2_forest_pacs", [ ] ] ]
ICR2["Packages"] += [ [ "r2_desert_pacs", [ ] ] ]
ICR2["Packages"] += [ [ "r2_roots_pacs", [ ] ] ]
ICR2["Packages"] += [ [ "r2_lakes_pacs", [ ] ] ]
ICR2["Packages"] += [ [ "r2_jungle_pacs", [ ] ] ]
ICR2["Packages"] += [ [ "r2_forest_maps", [ ] ] ]
ICR2["Packages"] += [ [ "r2_desert_maps", [ ] ] ]
ICR2["Packages"] += [ [ "r2_roots_maps", [ ] ] ]
ICR2["Packages"] += [ [ "r2_lakes_maps", [ ] ] ]
ICR2["Packages"] += [ [ "r2_jungle_maps", [ ] ] ]
ICR2["Packages"] += [ [ "r2_roots_pz", [ ] ] ]
ICR2["Packages"] += [ [ "r2_lakes_pz", [ ] ] ]
ICR2["Packages"] += [ [ "r2_jungle_pz", [ ] ] ]
ICR2["Packages"] += [ [ "r2_forest_pz", [ ] ] ]
ICR2["Packages"] += [ [ "r2_desert_pz", [ ] ] ]
ICR2["Packages"] += [ [ "r2_roots_shapes", [ ] ] ]
ICR2["Packages"] += [ [ "r2_lakes_shapes", [ ] ] ]
ICR2["Packages"] += [ [ "r2_jungle_shapes", [ ] ] ]
ICR2["Packages"] += [ [ "r2_forest_shapes", [ ] ] ]
ICR2["Packages"] += [ [ "r2_desert_shapes", [ ] ] ]
ICR2["Refs"] = [ ]
InstallClientData += [ ICR2 ]


if NeLConfigDir:
	configWorkspaceDir = os.path.join(NeLConfigDir, "workspace")
	sys.path.append(configWorkspaceDir)
	if os.path.isfile(os.path.join(configWorkspaceDir, "projects_exedll.py")):
		from projects_exedll import *


# end of file
