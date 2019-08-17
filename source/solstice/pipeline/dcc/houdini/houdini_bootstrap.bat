echo on
rem Solstice Houdini Bootstrap

set houdini_exec=%1
set h_path=%2
set scripts_path=%3

rem set Houdini paths
set "HOUDINI_PATH=%h_path%;&"

%houdini_exec% waitforui %scripts_path%