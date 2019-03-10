# **Solstice Alembic Manager**

!!! tip
    In Windows, remember to launch Maya using Solstice Launcher
    
## **Launch**

To launch Solstice Alembic Manager, open Maya and click on Alembic Manager Tool icon located in **LAYOUT** and **ANIM** Solstice Shelfs

> Solstice Alembic Manager Icon 
![Solstice Alembic Manager Icon](../../../img/alembic_0.png?style=centerme)

***

## **Alembic Groups**

To export Alembics you need to create first Alembic Groups. To create them you just need to 
follow the next steps:

1. Select all the objects you want to include into Alembic File.
2. In **Alembic Group** tab, type a name in **Group Name**
3. Press **Create** button
    
A new set will be created following this nomenclature: **{GROUP_NAME}_ABCGroup**

![Solstice Alembic Manager Icon](../../../img/alembic_1.png?style=centerme)

!!! info
    You can create as much Alembic Group as you want
    
!!! tip "Cleaning Alembic Gropus"
    After exporting an alembic, Alembic Groups can be deleted. You can clean all alembic groups
    in a scene by pressing **Clean Alembic Groups** button.

***

## **Alembic Export**

To export Alembics you need to go to **Exporter** tab

!!! important
    Any Alembic used in Solstice short film **MUST** to be exported using this tool

![Solstice Alembic Manager Icon](../../../img/alembic_2.png?style=centerme)

* **Alembic Group**: Here you define the Alembic Group you want to export
* **Alembic Name**: Here you need to write the name of the Alembic file
* **Shot Name**: If you are working on an Alembic specific for a shot you need to write the shot name here
* **Frame Range**: Frame range to export. To export an Alembic without animation both frames need to be 1.
* **Export Path**: Path where Alembic file should be exported
* **Alembic Tree**: Preview of the elements contained in the selected Alembic Group

***

## **Alembic Import**

To import Alembic files you need to go to **Importer** tab

!!! important
    Any Alembic used in Solstice short film **MUST** to be imported using this tool
    
![Solstice Alembic Manager Icon](../../../img/alembic_3.png?style=centerme)

