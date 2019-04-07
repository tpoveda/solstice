import os
import sys

print '='*100
print '| Solstice Pipeline | > Loading Solstice Tools'

try:
    import solstice_pipeline
    from maya import cmds
    cmds.evalDeferred('solstice_pipeline.init()')
    print '| Solstice Pipeline | Solstice Tools loaded successfully!'
    print '='*100
except Exception as e:
    try:
        solstice_pipeline.init()
        print '| Solstice Pipeline | Solstice Tools loaded successfully!'
        print '='*100
    except Exception as e:
        print('ERROR: Impossible to load Solstice Tools, contact TD!')
        print(str(e))
