#!/usr/bin/python
# 
# \file directories.py
# \brief Directories configuration
# \date 2010-08-27 17:13GMT
# \author Jan Boon (Kaetemi)
# \date 2001-2005
# \author Nevrax
# Python port of game data build pipeline.
# Directories configuration.
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

from buildsite import *
import os

# *** COMMON NAMES AND PATHS ***
CommonName = "gamedev"
CommonPath = "common/" + CommonName


# *** DIRECT SOURCE DIRECTORIES ***

# Copy dir directories
CopyDirectSourceDirectories = [ ]
CopyDirectSourceDirectories += [ GamedevDirectory ]
CopyDirectSourceFiles = [ ]
translationFileList = os.listdir(TranslationDirectory + "/translated")
for fileName in translationFileList:
	if fileName != ".svn" and fileName != ".." and fileName != "." and fileName != "*.*":
		if fileName.endswith(".uxt") or (fileName.endswith(".txt") and (fileName.startswith("skill_") or fileName.startswith("item_") or fileName.startswith("creature_") or fileName.startswith("sbrick_") or fileName.startswith("sphrase_") or fileName.startswith("place_") or fileName.startswith("faction_") or fileName.startswith("title_") or fileName.startswith("outpost_"))):
			CopyDirectSourceFiles += [ TranslationDirectory + "/translated/" + fileName ]


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


# *** INSTALL DIRECTORIES IN THE CLIENT DATA ***

# Particule system directory
CopyInstallDirectory = CommonName
