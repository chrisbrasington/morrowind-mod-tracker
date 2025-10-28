# MODLIST for [OPENMW](https://openmw.org/) 0.50

## Getting Started

If you're new to modding morrowind, I'd recommend starting with the [I Heart Vanilla](https://modding-openmw.com/lists/i-heart-vanilla/) guide and modlist. It adds bugfixes, quality of life improvements, some higher quality textures/meshes and things like graphic herbalism (seeing the plants you pick).

Beyond that - this is my personal extended list as it has grown over time. Things that I felt enhanced the experience without deviating too far from the core experience, such as volumetric fog, dynamic actors (the game not pausing when you talk to NPCs), and some immersive shaders/lighting. 

[Tamriel Rebuilt](https://www.tamriel-rebuilt.org/) is the real gold to be found here - but that can be added after playing the main game. 

[See screenshots of modded morrowind here.](https://steamcommunity.com/id/raylinth/screenshots/?appid=22320&sort=newestfirst&browsefilter=myfiles&view=imagewall)

## OpenMW Settings

| Category / Subcategory   | Setting / Description                                                                            | Notes / Additional Info                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **Visuals / Animations** | Weapon/Shield Sheathing<br>Smooth Movement<br>Smooth Animations                                  | See animation mods                                                                                                                               |
| **Visuals / Terrain**    | Viewing Distance: 10–12 Cells                                                                    | I use [Zesterer's Volumetric Cloud & Mist Mod](https://github.com/zesterer/openmw-volumetric-clouds) to obscure distant lands |
| **Visuals / Shadows**    | Terrain Shadows<br>Indoor Shadows<br>                                           | (more if desired, kept minimal to be less demanding)                                                                                                                             |
| **Interface**            | GUI Scale Factor: 1.5 (optional)<br>Can Zoom on Maps                                             | Zoom on maps is fantastic                                                                                                                             |
| **Shaders**               | 1. DIVE<br>2. HBAO<br>3. VAIO<br>4. godrays<br>5. wetworld<br>6. tonemap<br>7. SMAA<br>8. clouds | In-game: press F2. For clouds shader: no skybox used                                                                         |

## Mod Path Details

If you need details on the file paths I have for the various mods, see [MODLIST_DETAILS.md](https://github.com/chrisbrasington/morrowind-mod-tracker/blob/main/MODLIST_DETAILS.md)

# Essentials

| Type | Name | Description |
|------|------|------|
| Patches | [PatchforPurists](https://www.nexusmods.com/morrowind/mods/45096) | Over 9000+ bugs still present in the game have been fixed. |
| Patches | [UnofficialMorrowindOfficialPluginsPatched](https://www.nexusmods.com/morrowind/mods/43931) | An attempt to fix the many issues present in Bethesda's original Official Plugins. Includes fixes for all of the Official Plugins, and offers merged and compatibility options as well. |
| Patches | [ExpansionDelay](https://www.nexusmods.com/morrowind/mods/47588) | Delays the Dark Brotherhood attacks (for Tribunal) |
| Animation | [Reanimation](https://www.nexusmods.com/morrowind/mods/52596) | An immersive reimagining of (some) of the TES3: Morrowind 1st-person animations. Developed for OpenMW engine. |
| Animation | [Impact Effects](https://www.nexusmods.com/morrowind/mods/55508) | Sounds and VFX when your weapon hits surfaces. |
| NPCs | [DynamicActors](https://www.nexusmods.com/morrowind/mods/54782) | Play idle animations when talking to NPCs. |
| NPCs | [FamiliarFacesbyCaleb](https://www.nexusmods.com/morrowind/mods/50093) | An in-depth yet completely vanilla friendly touch up of every head and almost every hair (a few looked okay) in the game. |
| NPCs | [Facelift](https://www.nexusmods.com/morrowind/mods/47617) | Some people have desired a simple enhancement of vanilla faces and hairs, so here you go. |
| Gameplay | [GraphicHerbalismMWSEandOpenMWEdition](https://www.nexusmods.com/morrowind/mods/46599) | Pick plants |
| NPCs | [QuestGreetings](https://www.nexusmods.com/morrowind/mods/52273) | ElevenAI generated voices for quest-giving NPCs in Morrowind. Currently adds over 1800 original lines of voiced dialogue using the original actors voices. |
| Weapons | [WeaponSheathing](https://www.nexusmods.com/morrowind/mods/46069) | Makes unreadied weapons appear on the character's hip or back. |

# Land masses

| Type | Name | Description |
|------|------|------|
| Landmasses | [Tamriel Rebuilt](https://www.tamriel-rebuilt.org/) | Tamriel Rebuilt is a modding project that adds Morrowind's mainland to The Elder Scrolls III: Morrowind for you to explore. |
| ModdingResources | [TamrielData](https://www.nexusmods.com/morrowind/mods/44537) | Tamriel_Data contains a data unified file structure spearheaded by Project Tamriel and Tamriel Rebuilt as the first adopter. |
| Landmasses | [Cyrodill](https://www.nexusmods.com/morrowind/mods/44922) | Project Cyrodiil is a new lands mod from the Project Tamriel team that adds part of Cyrodiil, the Imperial Province, to the world of TESIII: Morrowind. |
| Landmasses | [Skyrim](https://www.nexusmods.com/morrowind/mods/44921) | 100+ quests, including new regional questlines for the Imperial Guilds, bounty hunting, and miscellaneous quests; 290+ exterior cells of hand-crafted landscape; 330+ interior cells, including the massive cities of Karthwasten and Dragonstar, towns, camps, and dozens of locations for you to loot in classic TES fashion. |

# Quality of Life / UI

| Type | Name | Description |
|------|------|------|
| Cheat | [No Arrow Weight](https://www.nexusmods.com/morrowind/mods/42570) | Tired of arrows encumbering you? Well, no more! |
| Fixes | [JammingsOff](https://www.nexusmods.com/morrowind/mods/44523) | Changing Bounding Box size for all NPC and Player. |
| Fixes | [DistantFixesLuaEdition](https://modding-openmw.gitlab.io/distant-fixes-lua-edition/) | A Lua framework for handling updates to distant objects that can support any content via YAML-based data. |
| UserInterface | [Better Dialogue Font](https://www.nexusmods.com/morrowind/mods/36873) | A high resolution replacer for Morrowind's Magic Cards font, used in most of the UI - menus, dialogue and the journal. |
| Fonts | [AlternativeTrueTypeFonts](https://modding-openmw.com/mods/alternative-truetype-fonts/) | Fonts to replace the default fonts used by OpenMW: Pelagiad by Isak Larborn and Ayembedt by Georg Duffner. |
| HUD | [voshondsQuickSelect](https://www.nexusmods.com/morrowind/mods/56494) | Adds hotbars/actionsbars to the game for convinient access to up to 30 user defined items/spells/weapons |

# Graphics Essential

| Type | Name | Description |
|------|------|------|
| Fog | [openmw-volumetric-clouds-main](https://github.com/zesterer/openmw-volumetric-clouds) | Zesterer's Volumetric Cloud & Mist Mod for OpenMW |
| Shaders | [VtastekLightShaders](https://modding-openmw.com/mods/vtasteks-light-shaders/) | A highly advanced shader replacement that also revamps all lighting in the game. |
| UserInterface | [InterfaceReimaigned](https://www.nexusmods.com/morrowind/mods/54985) | Modernized Dialogue and Decluttering of the UI |

# Graphics Extra

| Type | Name | Description |
|------|------|------|
| Architecture | [Nordsshutyourwindows](https://www.nexusmods.com/morrowind/mods/50087) | Nord's windows have a wooden shutter, open in the day and closed at night. |
| Architecture | [MorrowindInteriorsProject](https://www.nexusmods.com/morrowind/mods/52237) | Adds exteriors to all interior cells with windows. So far, Molag Mar, Caldera, Pelagiad, and Gnisis. |
| Books | [Textures](https://www.nexusmods.com/morrowind/mods/43100) | Replaces all the books, bookpages and scrolls. |
| Combat | [Mercy Combat AI Overhaul](https://www.nexusmods.com/morrowind/mods/55064) | An immersive overhaul of in-combat NPC behavior for OpenMW 0.49. With new voice lines and animations. |
| Extra | [LuaMultiMark](https://www.nexusmods.com/morrowind/mods/53260) | Allows the player to have multiple marked locations. |
| Groundcover | [AesthesiaGroundcovergrassmod](https://www.nexusmods.com/morrowind/mods/46377) | Grass for Morrowind - vanilla and Tamriel Rebuilt support. Made for every region. Includes Mesh Generator files. |
| Lighting | [GlowingFlames](https://www.nexusmods.com/morrowind/mods/46124) | Flames are now glow mapped and/or properly illuminated. |
| Lighting | [Enhanced Shadows for OpenMW](https://www.nexusmods.com/morrowind/mods/53667) | Optimized postprocess shader pack for OpenMW, making it look better than ever before while still being very Vanilla-friendly |
| Lighting | [Enhanced Water for OpenMW](https://www.nexusmods.com/morrowind/mods/56186) | OpenMW Water Shaders with dynamic caustics, water foam, volumetric light rays, and realistic fog effects. |
| ModdingResources | [OAAB](https://www.nexusmods.com/morrowind/mods/49042) | Asset repository |
| ModdingResources | [Behaviour Tree Lua 2nd Edition](https://www.nexusmods.com/morrowind/mods/55062) | Scripting resource |
| ObjectsClutter | [OpenMWContainersAnimated](https://www.nexusmods.com/morrowind/mods/46232) | This mod adds open/close animation and sounds to all containers that should have animation. |
| Performance | [MorrowindOptimizationPatch](https://www.nexusmods.com/morrowind/mods/45384) | Greatly improves performance and fixes tons of mesh errors. |
| Performance | [ProjectAtlas](https://www.nexusmods.com/morrowind/mods/45399) | The goal of Project Atlas is to identify the most performance heavy areas of vanilla Morrowind and some popular mods and target high usage/strain meshes in those areas for atlasing. This effort involves reworking the UVs for those meshes and creating texture atlases to cover various sets. |
| Physics | [Lua physics](https://www.nexusmods.com/morrowind/mods/56589) | Object physics |
| TexturePacks | [MorrowindEnhancedTextures](https://www.nexusmods.com/morrowind/mods/46221) | Upscales every in-game texture with the help of machine learning. 100% vanilla-friendly. |
| TexturePacks | [RealSignposts](https://www.nexusmods.com/morrowind/mods/3879) | The RealSignposts Plugin replaces the signposts in Morrowind by signposts showing the real names of the locations. |
| TexturePacks | [Landscape Retexture](https://www.nexusmods.com/morrowind/mods/42575) | Landscape retexturing |
| UserInterface | [CantonsontheGlobalMap](https://www.nexusmods.com/morrowind/mods/50534) | Vivec and Molag Mar no longer look like empty water on the global map. |
| UserInterface | [PerfectPlacement](https://www.nexusmods.com/morrowind/mods/46562) | Adds interactive placement, rotation and wall mounting of items. Arrange gear, books and anything else you can pick up. |
| UserInterface | [Small Skyrim Crosshair](https://www.nexusmods.com/morrowind/mods/46351) | Adds small skyrim-a-like crosshair with ownership mod compatibility |
| UserInterface | [Canvas Map Splash Screens](https://www.nexusmods.com/morrowind/mods/56025) | Canvas map loading screens |
| Voice | [LuaHelper](https://www.nexusmods.com/morrowind/mods/54629) | Tamriel Rebuilt voiced dialogue ESP to support TR release 25.05.09 hotfix. Support mod for use by other OpenMW lua Mods. Requires OpenMW 0.49. |
| Water | [DistantSeafloorforOpenMW](https://www.nexusmods.com/morrowind/mods/50796) | Extends the seafloor around Vvardenfell to hide the edge of the world in OpenMW. Compatible with everything. |
| Water | [Better Waterfalls](https://www.nexusmods.com/morrowind/mods/45424) | Better waterfalls |
| Weather | [KirelsInteriorWeather](https://www.nexusmods.com/morrowind/mods/49278) | Plays weather sound effects in interior cells, but not in places like caves, ruins, etc and places you wouldn't expect to hear them - all with little or no FPS hit. |
| HUD | [HUD](https://www.nexusmods.com/morrowind/mods/53038?tab=files) | Simple HUD |
| Lighting | [GlowintheDahrk](https://modding-openmw.com/mods/glow-in-the-dahrk/) | This is a modern, pluginless replacement of the old Windows Glow mods |
| Tools | [waza lightfixes](https://modding-openmw.com/mods/waza_lightfixes/) | This is a tool which generates a plugin which fixes lights. |
| UserInterface | [BigIcons](https://modding-openmw.com/mods/big-icons/) | Replaces the small 16x16 spell effect icons with your choice of larger icons. Works with your choice of MWSE or OpenMW |
| Tools | [wazalightfixes](https://github.com/glassmancody/waza_lightfixes/releases) | This is a tool which generates a plugin which fixes lights. |

# Voice/Audio

| Type | Name | Description |
|------|------|------|
| Audiobooks | [Audiobooks](https://www.nexusmods.com/morrowind/mods/52458) | Turn the books in Morrowind into listenable audiobooks! |
| Voice | [VoicesOfVvardenfell PatchForOpenMW](https://www.nexusmods.com/morrowind/mods/54137') | Kezyma's Voices of Vvardenfell, all dialogue now playable. OpenMW 0.49+ |
| Voice | [VoicesOfVvardenfell](https://www.nexusmods.com/morrowind/mods/52279) | Kezyma's Voices of Vvardenfell - A project to fully voice Morrowind using ElevenAI and MWSE. Comes with an optional 'greetings-only' mode and is easily extensible to add compatibility with other mods with no knowledge of scripting or the CS and no additional esp. |
| Voice | [LuaHelper](https://www.nexusmods.com/morrowind/mods/54629) | Tamriel Rebuilt voiced dialogue ESP to support TR release 25.05.09 hotfix. Support mod for use by other OpenMW lua Mods. Requires OpenMW 0.49. |

# Other Mods

| Type | Name | Description |
|------|------|------|
| Camping | [Easy Camping](https://www.nexusmods.com/morrowind/mods/42919) | An extremely simple, balanced and practical camping mod that seems to actually work! |
| Clothing | [Westly Presents Fine Clothiers of Tamriel](https://www.nexusmods.com/morrowind/mods/52331) | Adds a clothing store in Suran carrying imports from all over Tamriel. |
| Cities | [The Waters of His Glory](https://www.nexusmods.com/morrowind/mods/56621) | Grand Aqueducts near Vivec City. |
| Landmasses | [TamrielRebuilt](https://www.nexusmods.com/morrowind/mods/42145) | Tamriel Rebuilt is a modding project that adds Morrowind's mainland to The Elder Scrolls III: Morrowind for you to explore. |

