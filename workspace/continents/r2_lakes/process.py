#!/usr/bin/python
# 
# \file config.py
# \brief Process configuration
# \date 2010-05-24 06:30GMT
# \author Jan Boon (Kaetemi)
# \date 2001-2005
# \author Nevrax
# Python port of game data build pipeline.
# Process configuration.
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

# *** PROCESS CONFIGURATION ***


# *** PROCESS CONFIG ***
ProcessToComplete = [ ]
ProcessToComplete += [ "properties" ]
ProcessToComplete += [ "map" ]
ProcessToComplete += [ "shape" ]
ProcessToComplete += [ "ligo" ]
ProcessToComplete += [ "zone" ]
ProcessToComplete += [ "ig" ]
ProcessToComplete += [ "zone_light" ]
ProcessToComplete += [ "rbank" ]
ProcessToComplete += [ "ig_light" ]
ProcessToComplete += [ "ps" ]
ProcessToComplete += [ "ai_wmap" ]
ProcessToComplete += [ "cartographer" ]
ProcessToComplete += [ "pz" ]


# *** ECOSYSTEM AND CONTINENT NAMES ***

EcosystemName = "lacustre"
EcosystemPath = "ecosystems/" + EcosystemName
ContinentName = "r2_lakes"
ContinentPath = "continents/" + ContinentName
CommonName = ContinentName
CommonPath = ContinentPath

ParentName = "tryker"
ParentPath = "continents/" + ParentName


# *** LANDSCAPE NAME ***
LandscapeName = ContinentName

# *** CONTINENT FILE ***
ContinentSheet = ContinentName
ContinentFile = ContinentName + "/" + ContinentSheet + ".continent"



# *** SHAPE EXPORT OPTIONS ***

# Compute lightmaps ?
ShapeExportOptExportLighting = "true"

# Cast shadow in lightmap ?
ShapeExportOptShadow = "true"

# Lighting limits. 0 : normal, 1 : soft shadows
ShapeExportOptLightingLimit = 0

# Lightmap lumel size
ShapeExportOptLumelSize = "0.25"

# Oversampling value. Can be 1, 2, 4 or 8
ShapeExportOptOversampling = 1

# Does the lightmap must be generated in 8 bits format ?
ShapeExportOpt8BitsLightmap = "false"

# Does the lightmaps export must generate logs ?
ShapeExportOptLightmapLog = "true"

# Coarse mesh texture mul size
TextureMulSizeValue = "1.5"

BuildShadowSkinEnabled = False

ClodConfigFile = ""

# *** COARSE MESH TEXTURE NAME ***
CoarseMeshTextureNames = [ ]

# *** BANK EXPORT OPTIONS ***

# *** POSTFIX USED BY THE MULTIPLE TILES SYSTEM ***
MultipleTilesPostfix = [ ]
MultipleTilesPostfix += [ "_sp" ]
MultipleTilesPostfix += [ "_su" ]
MultipleTilesPostfix += [ "_au" ]
MultipleTilesPostfix += [ "_wi" ]

# Name of the tilebank to use
BankTileBankName = EcosystemName


# *** LIGO OPTIONS ***
LigoExportLand = ContinentName + ".land"
LigoExportOnePass = 0
LigoExportColormap = "colormap_" + ContinentName + ".tga"
LigoExportHeightmap1 = "big_" + ContinentName + ".tga"
LigoExportZFactor1 = "1.0"
LigoExportHeightmap2 = "noise_" + ContinentName + ".tga"
LigoExportZFactor2 = "0.5"
LigoExportExtendCoords = 1
LigoTileBankFile = "landscape/_texture_tiles/" + EcosystemName + "/" + EcosystemName + ".bank"

# *** ZONE REGIONS ( up-left, down-right ) ***
ZoneRegions = [ ] 
ZoneRegions += [ [ "6_hm" ] + [ "67_jv" ] ]

# *** RBANK OPTIONS ***

# Options
RBankVerbose = 0
RBankConsistencyCheck = 0
RbankReduceSurfaces = 1
RbankSmoothBorders = 1
RbankComputeElevation = 0
RbankComputeLevels = 1
RbankLinkElements = 1
RbankCutEdges = 1
RbankUseZoneSquare = 0

# Region to compute ( ALPHA UPPER CASE! )
RbankZoneUl = "6_HM"
RbankZoneDr = "67_JV"

# Output names
RbankRbankName = LandscapeName

# *** MAPS OPTIONS ***
ReduceBitmapFactor = 0
# list all panoply files
MapPanoplyFileList = None
# name of the .hlsbank to build.
MapHlsBankFileName = None

# *** AI WMAP OPTIONS ***
AiWmapContinentName = ContinentName
AiWmapVerbose = 0
AiWmapStartPoints = [ ]
AiWmapStartPoints += [ ContinentName + " 31330 -1280" ] # 1
AiWmapStartPoints += [ ContinentName + " 32069 -1340" ] # 2
AiWmapStartPoints += [ ContinentName + " 33000 -1000" ] # 3
AiWmapStartPoints += [ ContinentName + " 34000 -1076" ] # 4
AiWmapStartPoints += [ ContinentName + " 34850 -1100" ] # 5
AiWmapStartPoints += [ ContinentName + " 35550 -1000" ] # 6
AiWmapStartPoints += [ ContinentName + " 36271 -1105" ] # 7
AiWmapStartPoints += [ ContinentName + " 37150 -1290" ] # 8
AiWmapStartPoints += [ ContinentName + " 38000 -1215" ] # 9
AiWmapStartPoints += [ ContinentName + " 38628 -1213" ] # 10
AiWmapStartPoints += [ ContinentName + " 31341 -2077" ] # 11
AiWmapStartPoints += [ ContinentName + " 32187 -2200" ] # 12
AiWmapStartPoints += [ ContinentName + " 32983 -2200" ] # 13
AiWmapStartPoints += [ ContinentName + " 33465 -2164" ] # 14
AiWmapStartPoints += [ ContinentName + " 34300 -2000" ] # 15
AiWmapStartPoints += [ ContinentName + " 35200 -2100" ] # 16
AiWmapStartPoints += [ ContinentName + " 35900 -2000" ] # 17
AiWmapStartPoints += [ ContinentName + " 36700 -2050" ] # 18
AiWmapStartPoints += [ ContinentName + " 37500 -2050" ] # 19
AiWmapStartPoints += [ ContinentName + " 38400 -2000" ] # 20
AiWmapStartPoints += [ ContinentName + " 31200 -2800" ] # 21
AiWmapStartPoints += [ ContinentName + " 32000 -2800" ] # 22
AiWmapStartPoints += [ ContinentName + " 32700 -2800" ] # 23
AiWmapStartPoints += [ ContinentName + " 33300 -2800" ] # 24
AiWmapStartPoints += [ ContinentName + " 34000 -2800" ] # 25
AiWmapStartPoints += [ ContinentName + " 34700 -2800" ] # 26
AiWmapStartPoints += [ ContinentName + " 35100 -2800" ] # 27
AiWmapStartPoints += [ ContinentName + " 36500 -2800" ] # 28
AiWmapStartPoints += [ ContinentName + " 37400 -2800" ] # 29
AiWmapStartPoints += [ ContinentName + " 38100 -2800" ] # 30
AiWmapStartPoints += [ ContinentName + " 31400 -3800" ] # 31
AiWmapStartPoints += [ ContinentName + " 32100 -3800" ] # 32
AiWmapStartPoints += [ ContinentName + " 32550 -3800" ] # 33
AiWmapStartPoints += [ ContinentName + " 33440 -3800" ] # 34
AiWmapStartPoints += [ ContinentName + " 34250 -3800" ] # 35
AiWmapStartPoints += [ ContinentName + " 35000 -3800" ] # 36
AiWmapStartPoints += [ ContinentName + " 35800 -3800" ] # 37
AiWmapStartPoints += [ ContinentName + " 36300 -3800" ] # 38
AiWmapStartPoints += [ ContinentName + " 37530 -3820" ] # 39
AiWmapStartPoints += [ ContinentName + " 38400 -3800" ] # 40
AiWmapStartPoints += [ ContinentName + " 31200 -4600" ] # 41

# *** PZ OPTIONS ***
PackedZoneCWMap = ContinentName + "_0.cwmap2"

# *** CARTOGRAPHER OPTIONS ***
CartographerContinent = ContinentName
IslandsXmlFile = ContinentName + "_islands.xml"
CartographerSeasonSuffixes = [ "_sp" ]
