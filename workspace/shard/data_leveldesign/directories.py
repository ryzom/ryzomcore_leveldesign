#!/usr/bin/python
# 
# \file directories.py
# \brief Directories configuration
# \date 2014-02-13 20:32GMT
# \author Jan Boon (Kaetemi)
# Python port of game data build pipeline.
# Directories configuration.
# 
# NeL - MMORPG Framework <http://dev.ryzom.com/projects/nel/>
# Copyright (C) 2014  by authors
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

from buildsite import *
import os

# *** COMMON NAMES AND PATHS ***
CommonName = "data_leveldesign"
CommonPath = "shard/" + CommonName


# *** DIRECT SOURCE DIRECTORIES ***

# Copy dir directories
CopyDirectSourceDirectories = [ ]
CopyDirectSourceFiles = [ WorldEditorFilesDirectory + "/world_editor_classes.xml" ]


# *** SOURCE DIRECTORIES IN LEVELDESIGN ***
CopyLeveldesignSourceDirectories = [ "game_element/emotes" ]
CopyLeveldesignSourceFiles = [ "game_elem/sheet_id.bin", "game_elem/localisation.localisation_table" ]
CopyLeveldesignWorldSourceDirectories = [ "" ]
CopyLeveldesignWorldSourceFiles = [ ]
CopyLeveldesignDfnSourceDirectories = [ "basics", "game_elem/_emote", "world" ]
CopyLeveldesignDfnSourceFiles = [ "game_elem/localisation_table.dfn", "game_elem/_localisation_table_line.dfn", "game_elem/_item/item_shield_category.typ", "game_elem/_item/item_slot.typ", "game_elem/_item/item_mp_group.typ", "_light.dfn", "_rgba.dfn", "_vector.dfn", "game_elem/weather_function.dfn", "game_elem/weather_function_modifier.dfn", "game_elem/weather_function_params.dfn", "game_elem/weather_function_visual.dfn" ]


# *** SOURCE DIRECTORIES IN THE DATABASE ***

# Copy dir directories
CopyDatabaseSourceDirectories = [ ]
CopyDatabaseSourceFiles = [ ]


# *** INSTALL DIRECTORIES IN THE CLIENT DATA ***

# Common data install directory
CopyInstallDirectory = CommonName
