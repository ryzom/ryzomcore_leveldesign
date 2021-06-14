#!/usr/bin/python
# 
# \file config.py
# \brief Process configuration
# \date 2010-05-24 06:30GMT
# \author Jan Boon (Kaetemi)
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

EcosystemName = "jungle"
EcosystemPath = "ecosystems/" + EcosystemName
ContinentName = "r2_forest"
ContinentPath = "continents/" + ContinentName
CommonName = ContinentName
CommonPath = ContinentPath

ParentName = "zorai"
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
ZoneRegions += [ [ "69_fb" ] + [ "130_hk" ] ]

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
RbankZoneUl = "68_FA"
RbankZoneDr = "131_HL"

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
AiWmapStartPoints += [ ContinentName + " 21600 -11200" ]
AiWmapStartPoints += [ ContinentName + " 22300 -11200" ]
AiWmapStartPoints += [ ContinentName + " 23066 -11207" ]
AiWmapStartPoints += [ ContinentName + " 24105 -11095" ]
AiWmapStartPoints += [ ContinentName + " 24800 -11200" ]
AiWmapStartPoints += [ ContinentName + " 25424 -11251" ]
AiWmapStartPoints += [ ContinentName + " 26400 -11200" ]
AiWmapStartPoints += [ ContinentName + " 27200 -11200" ]
AiWmapStartPoints += [ ContinentName + " 28000 -11200" ]
AiWmapStartPoints += [ ContinentName + " 28600 -11200" ]
AiWmapStartPoints += [ ContinentName + " 29400 -11408" ]
AiWmapStartPoints += [ ContinentName + " 29900 -11000" ]
AiWmapStartPoints += [ ContinentName + " 30500 -11200" ]
AiWmapStartPoints += [ ContinentName + " 21278 -12178" ]
AiWmapStartPoints += [ ContinentName + " 22061 -11792" ]
AiWmapStartPoints += [ ContinentName + " 22800 -12000" ]
AiWmapStartPoints += [ ContinentName + " 23554 -11853" ]
AiWmapStartPoints += [ ContinentName + " 24326 -11878" ]
AiWmapStartPoints += [ ContinentName + " 25000 -12000" ]
AiWmapStartPoints += [ ContinentName + " 26000 -12000" ]
AiWmapStartPoints += [ ContinentName + " 26548 -12026" ]
AiWmapStartPoints += [ ContinentName + " 27101 -11038" ]
AiWmapStartPoints += [ ContinentName + " 28475 -12108" ]
AiWmapStartPoints += [ ContinentName + " 28522 -12111" ]
AiWmapStartPoints += [ ContinentName + " 29365 -11968" ]
AiWmapStartPoints += [ ContinentName + " 30500 -11800" ]
AiWmapStartPoints += [ ContinentName + " 21100 -12600" ]
AiWmapStartPoints += [ ContinentName + " 21622 -12713" ]
AiWmapStartPoints += [ ContinentName + " 22306 -12674" ]
AiWmapStartPoints += [ ContinentName + " 22800 -12800" ]
AiWmapStartPoints += [ ContinentName + " 23501 -12801" ]
AiWmapStartPoints += [ ContinentName + " 24701 -12901" ]
AiWmapStartPoints += [ ContinentName + " 25301 -12901" ]
AiWmapStartPoints += [ ContinentName + " 26201 -12901" ]
AiWmapStartPoints += [ ContinentName + " 27001 -12901" ]
AiWmapStartPoints += [ ContinentName + " 27801 -12901" ]
AiWmapStartPoints += [ ContinentName + " 29001 -12901" ]
AiWmapStartPoints += [ ContinentName + " 29601 -12901" ]
AiWmapStartPoints += [ ContinentName + " 30201 -12901" ]
AiWmapStartPoints += [ ContinentName + " 21201 -13301" ] # 40
AiWmapStartPoints += [ ContinentName + " 22201 -13301" ]
AiWmapStartPoints += [ ContinentName + " 22801 -13501" ]
AiWmapStartPoints += [ ContinentName + " 24001 -13501" ]
AiWmapStartPoints += [ ContinentName + " 24701 -13501" ]
AiWmapStartPoints += [ ContinentName + " 25801 -13501" ]
AiWmapStartPoints += [ ContinentName + " 27001 -13501" ]

# *** PZ OPTIONS ***
PackedZoneCWMap = ContinentName + "_0.cwmap2"

# *** CARTOGRAPHER OPTIONS ***
CartographerContinent = ContinentName
IslandsXmlFile = ContinentName + "_islands.xml"
CartographerSeasonSuffixes = [ "_sp" ]
