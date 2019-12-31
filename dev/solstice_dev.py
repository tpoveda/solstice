# ==================================================================
# SOLSTICE - DEV
# ==================================================================

import os
import sys
import maya.cmds as cmds

dev_path = 'D:/dev/solstice/solstice_dev/Lib/site-packages'
paths_to_add = [dev_path]
for f in os.listdir(dev_path):
    if f.endswith('.egg-link'): 
        file_path = os.path.join(dev_path, f)
        with open(file_path) as f:
            new_path = f.readline().rstrip()
            if os.path.isdir(new_path):
                paths_to_add.append(new_path)

for p in paths_to_add:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.append(p)
        
# =============================================================

import artellapipe
import solstice.loader
solstice.loader.init(True, dev=True)

# =============================================================

# deps = artellapipe.DepsMgr().get_current_scene_dependencies()
# for file_path, files in deps.items():
#     print('\n-------------------------------------------------')
#     print(file_path)
#     for f in files:
#         print('\t{}'.format(f))
    

# import artellapipe
# from artellapipe.core import asset
# manager = asset.ArtellaAssetsManager()
# tracker = artellapipe.Tracker()
# print(tracker.all_project_assets())


# =============================================================

# import artellapipe

# artellapipe.ShadersMgr().load_scene_shaders()
# artellapipe.ShadersMgr().unload_shaders()


# shader_name = 'S_PRP_34_whiChair_WinterHouseFabricChair_default_high'
# export_path = r'C:\Users\Tomi\Desktop\export_shaders'
# artellapipe.ShadersMgr().export_shader(shader_name, export_path=export_path)

# artellapipe.ShadersMgr().load_shader(
#     shader_name='S_PRP_34_whiChair_WinterHouseFabricChair_default_high',
#     shader_path=r'C:\Users\Tomi\Desktop\export_shaders')
    
    
# from artellapipe.core import defines
# assets = artellapipe.AssetsMgr().find_all_assets()
# asset = assets[15]
# f = asset.get_file('shader', defines.ArtellaFileStatus.PUBLISHED)

# =============================================================

# from solstice.assets import prop
# prop.SolsticeProp.ASSET_TYPE

# TOOLS MANAGER
# from artellapipe import loader
# loader.run_toolbox(project=artellapipe.solstice)

# TOOLBOX
# tool.ToolsManager().run_tool(artellapipe.solstice, 'toolbox', do_reload=True)

# =============================================================

# WELCOME
# os.environ['ARTELLAPIPE.TOOLS.WELCOME_DEV'] = 'true'
# tool.ToolsManager().run_tool(artellapipe.solstice, 'welcome', do_reload=True)

# # CHANGELOG
# tool.ToolsManager().run_tool(artellapipe.solstice, 'changelog', do_reload=True)

# # BUG TRACKER
# tool.ToolsManager().run_tool(artellapipe.solstice, 'bugtracker', do_reload=True, debug=False)

# ALEMBIC MANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'alembicmanager', do_reload=True, debug=False)

# ARTELLA MANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'artellamanager', do_reload=True, debug=False, extra_args={'mode': 'all'})

# # ARTELLA UPLOADER
# tool.ToolsManager().run_tool(artellapipe.solstice, 'artellauploader', do_reload=True, debug=False)

# ASSETS LIBRARY
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'assetslibrary', do_reload=True, debug=False)

# ASSETS MANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'assetsmanager', do_reload=True, debug=False)

# LIGHT RIGS MANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'lightrigsmanager', do_reload=True, debug=False)

# NAME MANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'namemanager', do_reload=True, debug=False)

# OUTLINERa
# *tool.ToolsManager().run_tool(artellapipe.solstice, 'outliner', do_reload=True, debug=False)

# TAGGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'tagger', do_reload=True, debug=False)

# SHADERSMANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'shadersmanager', do_reload=True, debug=False)

# PLAYBLAST MANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'playblastmanager', do_reload=True, debug=False)

# SNOW GENERATOR
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'snowgenerator', do_reload=True, debug=False)

# XGENMANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'xgenmanager', do_reload=True, debug=False)

# MODEL CHECKER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'modelchecker', do_reload=True, debug=False)

# ASSETS PUBLISHER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'assetspublisher', do_reload=True, debug=False)

# DEPENDENCIES MANAGER
# artellapipe.ToolsMgr().run_tool(artellapipe.solstice, 'dependenciesmanager', do_reload=True, debug=False)



# # CHANGELOG
# os.environ['ARTELLAPIPE.TOOLS.CHANGELOG_DEV'] = 'true'
# from artellapipe.tools import changelog
# changelog.run(artellapipe.solstice, do_reload=True)



# from artellapipe.libs.naming.core import naminglib
# naming = naminglib.ArtellaNameLib()
# template = naming.templates[0]
# template.name
# template.pattern
# template.parse('Assets/Props/A/__working__/model/A.ma')
# template.format({'asset_name': 'A', 'version_folder': '__working__'})


# import ffmpeg
# from tpPyUtils import osplatform
# from artellapipe.libs import ffmpeg as ffmpeg_lib
# reload(ffmpeg_lib)
# ffmpeg_exe = ffmpeg_lib.get_ffmpeg_executable()


# video = ffmpeg.input(r"D:\dev\tests_ffmpeg\bigbuck_test.mp4")
# overlay = ffmpeg.input(r"D:\dev\tests_ffmpeg\solstice_logo.png")
# stream = ffmpeg.overlay(video, overlay)
# stream = ffmpeg.output(stream, r"D:\dev\tests_ffmpeg\bigbuck_test_out2.mp4")
# ffmpeg.run(stream, cmd=ffmpeg_exe)


# 1) Crop of the image (top and bottom black bands)
# video = ffmpeg.input(r"D:\dev\tests_ffmpeg\bigbuck_test.mp4")
# stream = ffmpeg.filter(video, 'crop', 1920, 1080-263, 0, 263)
# stream = ffmpeg.output(stream, r"D:\dev\tests_ffmpeg\bigbuck_crop.mp4")
# ffmpeg.run(stream, cmd=ffmpeg_exe)

# 2) Add logo
# video = ffmpeg.input(r"D:\dev\tests_ffmpeg\bigbuck_test.mp4")
# top = ffmpeg.input(r"D:\dev\tests_ffmpeg\top.png")
# font_file = r"D:\dev\tests_ffmpeg\Montserrat-Regular.ttf"
# bottom = ffmpeg.input(r"D:\dev\tests_ffmpeg\bottom.png")
# stream = ffmpeg.overlay(video, top, x=0, y=0)
# stream = ffmpeg.overlay(stream, bottom, x=0, y=1080-131)
# stream = ffmpeg.drawtext(stream, 'Department: LAYOUT', x=20, y=30, fontcolor='white', fontfile=font_file, fontsize=32)
# stream = ffmpeg.drawtext(stream, '   Version: 1', x=20, y=30+45, fontcolor='white', fontfile=font_file, fontsize=32)
# stream = ffmpeg.drawtext(stream, '    Frames: %{n}', start_number=0, x=20, y=1080-105, fontcolor='white', fontfile=font_file, fontsize=32, escape_text=False)
# stream = ffmpeg.drawtext(stream, '    Time: ', timecode="00:00:00:00", timecode_rate=30, x=20, y=1080-65, fontcolor='white', fontfile=font_file, fontsize=32, escape_text=False)
# stream = ffmpeg.drawtext(stream, 'Camera: persp', x=960-150, y=1080-105, fontcolor='white', fontfile=font_file, fontsize=32, escape_text=False)
# stream = ffmpeg.drawtext(stream, 'Length: 25mm: ', x=960-150, y=1080-65, fontcolor='white', fontfile=font_file, fontsize=32, escape_text=False)
# stream = ffmpeg.drawtext(stream, 'Artist: Tomi', x=1920-300, y=1080-105, fontcolor='white', fontfile=font_file, fontsize=32, escape_text=False)
# stream = ffmpeg.drawtext(stream, '  Shot: S_00_000', x=1920-300, y=1080-65, fontcolor='white', fontfile=font_file, fontsize=32, escape_text=False)
# stream = ffmpeg.output(stream, r"D:\dev\tests_ffmpeg\bigbuck_test_out2.mp4")
# ffmpeg.run(stream, cmd=ffmpeg_exe, overwrite_output=True, quiet=True)








