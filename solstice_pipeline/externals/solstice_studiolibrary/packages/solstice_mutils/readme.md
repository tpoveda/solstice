# Welcome to solstice_mutils!

solstice_mutils is a free python module for managing poses and animation in Maya. Comments, suggestions and bug reports are welcome.

* www.solstice_studiolibrary.com


## Classes

* solstice_mutils.Pose
* solstice_mutils.Animation
* solstice_mutils.MirrorTable
* solstice_mutils.SelectionSet


# Examples


Saving animation to disk

```python
    import solstice_mutils
    import maya.cmds

    objects = maya.cmds.ls(selection=True)
    a = solstice_mutils.Animation.fromObjects(objects)
    a.save("/tmp/test.anim")
```

Loading animation from disk

``` python
    a = solstice_mutils.Animation.fromPath("/tmp/test.anim")
    a.load()
```

Loading animation to selected objects

```python
    objects = maya.cmds.ls(selection=True)
    a.load(objects=objects)
```

Loading animation to multiple namespaces

```python
    namespaces = ["character1", "character2"]
    a.load(namespaces=namespaces)
```

Loading animation to specified objects

```python
    objects = ["Character1:Hand_L", "Character1:Finger_L"]
    a.load(objects=objects)
```
