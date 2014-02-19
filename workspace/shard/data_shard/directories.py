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
CommonName = "data_shard"
CommonPath = "shard/" + CommonName


# *** DIRECT SOURCE DIRECTORIES ***

# Copy dir directories
CopyDirectSourceDirectories = [ ]
CopyDirectSourceDirectories += [ DataShardDirectory ]
CopyDirectSourceDirectories += [ LeveldesignDataShardDirectory ]
CopyDirectSourceFiles = [ ]

# Sheets shard directories
VisualSlotTabBuildDirectory = "common/leveldesign/visual_slot_tab"


# *** SOURCE DIRECTORIES IN LEVELDESIGN ***
CopyLeveldesignSourceDirectories = [ ]
CopyLeveldesignSourceFiles = [ ]
CopyLeveldesignWorldSourceDirectories = [ ]
CopyLeveldesignWorldSourceFiles = [ ]
CopyLeveldesignDfnSourceDirectories = [ ]
CopyLeveldesignDfnSourceFiles = [ ]


# *** SOURCE DIRECTORIES IN THE DATABASE ***

# Copy dir directories
CopyDatabaseSourceDirectories = [ ]
CopyDatabaseSourceFiles = [ ]

# Sheets shard directories
SheetsShardBuildDirectory = CommonPath + "/sheets_shard"


# *** INSTALL DIRECTORIES IN THE CLIENT DATA ***

# Common data install directory
CopyInstallDirectory = CommonName
SheetsShardInstallDirectory = CommonName
