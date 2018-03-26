import os
import sys

print '='*100
print '| Solstice Tools | > Loading Solstice Tools'

try:
    solstice_tools_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    if solstice_tools_path not in sys.path:
        sys.path.append(solstice_tools_path)

    from solstice_config import solstice_initializer
    from maya import cmds
    cmds.evalDeferred('solstice_initializer.init()')
    print '| Solstice Tools | > LOADED SUCCESFULLY!'
    print '='*100
except Exception as e:
    print('ERROR: Impossible to load Solstice Tools, contact TD!')
    print(str(e))
