print '='*100
print '| Solstice Tools | > Loading Solstice Tools'
from solstice_config import solstice_initializer
from maya import cmds
cmds.evalDeferred('solstice_initializer.init()')
print '| Solstice Tools | > LOADED SUCCESFULLY!'
print '='*100