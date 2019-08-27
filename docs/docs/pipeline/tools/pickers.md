# **{{ project.name }} Pickers**

!!! tip
    In Windows, remember to launch Maya using {{ project.name }} Launcher
    
## **Launch**

To launch {{ project.name }} Pickers Tool, open Maya and click on {{ project.name }} Pipelinizer Tool icon located in **ANIM** {{ project.name }} Shelf

> {{ project.name }} Pickers Icon
![{{ project.name }} Pickers Icon](../../../img/tools/pickers/{{ project.name }}_pickers_icon.png?style=centerme)

***

## **Main Features**

* **Interactive UI** based on the rig state (IK/FK, etc)
* Control **hierarchy selection** by double clicking a child control
* **Body** and **Facial** picker in separated windows or fullscreen window
* **Studio Library** incorporated inside the picker
* Option to **reset** control states to its default
* Option to **flip/mirror** controls
* Option to select complete **rig modules** (arm, head, leg, etc)
* **Namespace** are detected automatically when the tool is opened

***

> {{ project.name }} Pickers Tool UI
![{{ project.name }} Pickers Tool UI](../../../img/tools/pickers/{{ project.name }}_pickers_ui.png?style=centerme)

1. Character **Pickers** Buttons
2. Alternative picker based on AnimSchool pickers. Blue folder button will open the folder where **AnimSchool pickers are stored**
3. Open **AnimSchool picker** tool
4. Open **StudioLibrary** Tool ([https://www.studiolibrary.com/](https://www.studiolibrary.com/))
5. Direct link to **{{ project.name }} Documentation**

***

## **Picker Rig Commands**

To launch Picker Rig Commands after opening a character rig you have 2 options:

1. Open **{{ project.name }} Pickers Tool** and the scripts will be loaded automatically
2. Execute **Load Picker Scripts** script located in **ANIM** {{ project.name }} Shelf to load scripts manually

> {{ project.name }} Load Pickers Scripts Button
![Load Pickers Scripts](../../../img/tools/pickers/refresh_picker_commands.png?style=centerme)

***

!!! tip
    You can use Picker Rig Commands along with {{ project.name }} Pickers to interact with the rig
    
All {{ project.name }} rigs incorporate a collection of scripts to interact with the rig.To access that menu you need to press: 
**Shift + Alt** key combination on top of a rig control.

The contextual menu changes its options depending of what type of control you have the cursor over.

> {{ project.name }} Pickers Commands
![{{ project.name }} Pickers Commands](../../../img/tools/pickers/pickers_command.png?style=centerme)

***

## **{{ project.name }} Picker**

!!! warning
    Before opening a picker, make sure that in your scene there is, at least one character referenced/imported

After pressing a character button the Character Picker will popup on the right side of the Maya UI

> Summer Picker
![Summer Picker](../../../img/tools/pickers/summer_picker.png?style=centerme)

***

### **How to use**

**WIP**

***

## **AnimSchool Pickers**

!!! warning
    They should be only used if {{ project.name }} Pickers are not working properly and you are waiting for a new version or 
    a bug fix.
    
We have also added an alternative option to {{ project.name }} Pickers with the basic functionality based on AnimSchool picker 
tool. To use this picker follow this steps:

1. Open {{ project.name }} Picker Tool
2. Press AnimSchool button located at the bottom of the {{ project.name }} Picker UI

> AnimSchool Picker Window
![AnimSchool Picker Window](../../../img/tools/pickers/animschool_picker_0.png?style=centerme)

3. In AnimSchoolPicker press **File - Open** and select one of the AnimSchool Pickers 

!!! tip
    You can open multiple pickers at the same time inside AnimSchool picker
    
> AnimSchool Picker
![AnimSchool Picker](../../../img/tools/pickers/animschool_picker_1.png?style=centerme)