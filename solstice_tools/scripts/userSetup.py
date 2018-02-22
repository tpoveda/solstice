print '='*100
print '| Solstice Tools | > Loading Solstice Tools'
from solstice_tools.scripts.solstice_config import solstice_initializer
from maya import cmds
cmds.evalDeferred('from solstice_tools.scripts.solstice_config import solstice_initializer; solstice_initializer.init()')
print '| Solstice Tools | > LOADED SUCCESFULLY!'
print '='*100