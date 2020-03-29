#!/usr/bin/python
# 
# \file directories.py
# \brief Directories configuration
# \date 2019-11-13 6:05GMT
# \author Jan Boon (Kaetemi)
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


# *** COMMON NAMES AND PATHS ***
EcosystemName = "sound"
EcosystemPath = "common/" + EcosystemName
ContinentName = EcosystemName
ContinentPath = EcosystemPath
CommonName = ContinentName
CommonPath = ContinentPath


# *** SOURCE DIRECTORIES IN THE DATABASE ***

# Sound directories
SoundSamplebanksSourceDirectory = "samplebanks"


# *** EXPORT DIRECTORIES FOR THE BUILD PIPELINE ***

# Sound directories
SoundExportDirectory = CommonPath + "/sound_export"


# *** BUILD DIRECTORIES FOR THE BUILD PIPELINE ***

# Sound directories
SoundSamplebanksBuildDirectory = CommonPath + "/sound_samplebanks_build"
SoundSheetsBuildDirectory = CommonPath + "/sound_sheets_build"


# *** INSTALL DIRECTORIES IN THE CLIENT DATA ***

# Lightmap directory
SoundInstallDirectory = "sound"

