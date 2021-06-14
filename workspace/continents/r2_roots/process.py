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
#ProcessToComplete += [ "map" ]
#ProcessToComplete += [ "shape" ]
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

EcosystemName = "primes_racines"
EcosystemPath = "ecosystems/" + EcosystemName
ContinentName = "r2_roots"
ContinentPath = "continents/" + ContinentName
CommonName = ContinentName
CommonPath = ContinentPath


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
ZoneRegions += [ [ "131_hl" ] + [ "193_jv" ] ]

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
RbankZoneUl = "131_HL"
RbankZoneDr = "193_JV"

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
AiWmapStartPoints += [ ContinentName + " 31194 -21080" ]
AiWmapStartPoints += [ ContinentName + " 31729 -21179" ]
AiWmapStartPoints += [ ContinentName + " 32376 -21135" ]
AiWmapStartPoints += [ ContinentName + " 33217 -21234" ]
AiWmapStartPoints += [ ContinentName + " 34055 -21280" ]
AiWmapStartPoints += [ ContinentName + " 34706 -21115" ]
AiWmapStartPoints += [ ContinentName + " 35445 -21172" ]
AiWmapStartPoints += [ ContinentName + " 36191 -21131" ]
AiWmapStartPoints += [ ContinentName + " 37069 -21142" ]
AiWmapStartPoints += [ ContinentName + " 37956 -21300" ]
AiWmapStartPoints += [ ContinentName + " 38638 -21205" ]
AiWmapStartPoints += [ ContinentName + " 39548 -21238" ]
AiWmapStartPoints += [ ContinentName + " 40255 -21395" ]
AiWmapStartPoints += [ ContinentName + " 31245 -21942" ]
AiWmapStartPoints += [ ContinentName + " 32072 -21995" ]
AiWmapStartPoints += [ ContinentName + " 32868 -21979" ]
AiWmapStartPoints += [ ContinentName + " 33550 -22010" ]
AiWmapStartPoints += [ ContinentName + " 34197 -22105" ]
AiWmapStartPoints += [ ContinentName + " 35020 -22160" ]
AiWmapStartPoints += [ ContinentName + " 35878 -22063" ]
AiWmapStartPoints += [ ContinentName + " 36714 -21986" ]
AiWmapStartPoints += [ ContinentName + " 37418 -22039" ]
AiWmapStartPoints += [ ContinentName + " 38329 -22050" ]
AiWmapStartPoints += [ ContinentName + " 38962 -21990" ]
AiWmapStartPoints += [ ContinentName + " 39818 -22059" ]
AiWmapStartPoints += [ ContinentName + " 40463 -22063" ]
AiWmapStartPoints += [ ContinentName + " 31312 -22688" ]
AiWmapStartPoints += [ ContinentName + " 32021 -22835" ]
AiWmapStartPoints += [ ContinentName + " 33004 -22930" ]
AiWmapStartPoints += [ ContinentName + " 33655 -22798" ]

# *** PZ OPTIONS ***
PackedZoneCWMap = ContinentName + "_0.cwmap2"

# *** CARTOGRAPHER OPTIONS ***
CartographerContinent = ContinentName
IslandsXmlFile = ContinentName + "_islands.xml"
CartographerSeasonSuffixes = [ "_sp" ]
