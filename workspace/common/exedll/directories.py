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


# *** COMMON NAMES AND PATHS ***
CommonName = "exedll"
CommonPath = "common/" + CommonName


# *** DIRECT SOURCE DIRECTORIES ***

# Copy dir directories
CopyDirectSourceDirectories = [ ]
CopyDirectSourceFiles = [ ]


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


# *** SPECIAL SOURCES ***

# Sign files
ExeDllFiles = [ ]

ExeDllFiles += [ "nel_drv_direct3d_win_r.dll" ]
ExeDllFiles += [ "nel_drv_dsound_win_r.dll" ]
ExeDllFiles += [ "nel_drv_fmod_win_r.dll" ]
ExeDllFiles += [ "nel_drv_openal_win_r.dll" ]
ExeDllFiles += [ "nel_drv_opengl_win_r.dll" ]
ExeDllFiles += [ "nel_drv_opengl3_win_r.dll" ]
ExeDllFiles += [ "nel_drv_xaudio2_win_r.dll" ]

ExeDllFiles += [ "ryzom_client_r.exe" ]
ExeDllFiles += [ "ryzom_client_patcher.exe" ]
ExeDllFiles += [ "ryzom_configuration_qt_r.exe" ]
ExeDllFiles += [ "crash_report.exe" ]


# Copy dir directories
CopyExeDllCfgSourceFiles = [ ]

CopyExeDllCfgSourceFiles += [ "client_default.cfg" ]


# *** EXPORT DIRECTORIES ***

# Sign
UnsignedExeDllDirectory = CommonPath + "/unsigned_exe_dll"


# *** BUILD DIRECTORIES ***

# Sign
SignedExeDllDirectory = CommonPath + "/signed_exe_dll"


# *** INSTALL DIRECTORIES IN THE CLIENT DATA ***

# Copy
CopyInstallDirectory = CommonName

# Lib
# LibInstallDirectory = CommonName + "_lib"
LibInstallDirectory = CommonName

# Sign
SignInstallDirectory = CommonName
