# **Solstice Pipelinizer**

!!! tip
    In Windows, remember to launch Maya using Solstice Launcher
    
## **Launch**

To launch Solstice Pipelinizer Tool, open Maya and click on Solstice Pipelinizer Tool icon located in **MAIN** Solstice Shelf

> Solstice Pipelinizer Icon
![Solstice Pipelinizer Icon](../../../img/solstice_pipelinizer_icon.png?style=centerme)

***

!!! info "Save Scene"
    If you have an scene opened when launching Solstice Pipelinizer, a dialog will appear telling you if you want 
    to save your current scene before opening Solstice Pipelinizer. 
    
    ![Solstice Pipelinizer Save](../../../img/solstice_pipelinizer_save.png?style=centerme)
    
    If you press **Yes**, the scene will be saved before opening Solstice Pipelinizer tool, otherwise (**No**) Solstice 
    Pipelinizer will be opened without saving the scene.
    
    I **recommend** saving the scene to avoid the lose of data if Solstice Pipelinizer crashes at some point (that 
    can happen)

    


> Solstice Pipelinizer
![Solstice Pipelinizer](../../../img/solstice_pipelinizer.png?style=centerme)

***

## **Main UI**

> Solstice Pipelinizer UI
![Solstice Pipelinizer UI](../../../../img/pipelinizer_0.png?style=centerme)

<center>

|    |      Description      | 
| -------- |:------------:|
| ![Solstice Pipelinizer Purple](../../../../img/color_purple.png?style=centerme) | User Information (shows the name of the user, OS platform and Artella availability |
| ![Solstice Pipelinizer Blue](../../../../img/color_blue.png?style=centerme) | Solstice Pipelinizer Toolbar |
| ![Solstice Pipelinizer Yellow](../../../../img/color_yellow.png?style=centerme) | Assets Manager & Sequences Manager |


</center>

### **User Information**

> Solstice Pipelinizer User Info
![Solstice Pipelinizer User Info](../../../../img/pipelinizer_info.png?style=centerme)

!!! tip
    User Image is downloaded in an asynchronous way so can take some seconds until the image appears. During this time,
    you will an animated loading circle instead of the user info
    
    > User Info Loading
    ![Solstice Pipelinizer User Info Loading](../../../img/circle_loading.png?style=centerme)
    
***

#### **User Artella Image**
This is the image of the user that is setted up in Artella Settings


> Solstice Pipelinizer User Image
![Solstice Pipelinizer User Info](../../../../img/pipelinizer_user_image.png?style=centerme)

***

#### **User Name**
This is the name of the user

***

#### **OS Platform**
This is the OS used by the user

<center>

|    |      Description      | 
| -------- |:------------:|
| ![OS Apple](../../../../img/os_windows.png?style=centerme) | This icon appears if the user is using Windows OS |
| ![OS Windows](../../../../img/os_apple.png?style=centerme) | This icon appearas if the user is using MacOS |

</center>

***

#### **Artella availability**
This indicator shows is Artella server is available (green) or not (red)

<center>

|    |      Description      | 
| -------- |:------------:|
| ![Artella On](../../../../img/artella_on.png?style=centerme) | Artella server is available |
| ![Artella Off](../../../../img/artella_off.png?style=centerme) | Artella server is **not** available |


</center>

***

### **ToolBar**

> Solstice Pipelinizer ToolBar
![Solstice Pipelinizer User Info](../../../../img/pipelinizer_toolbar.png?style=centerme)

***

#### **Artella Project**
This button opens Solstice Artella Project in your web browser

![Artella Project](../../../../img/artella_logo.jpg?style=centerme)

!!! info
    The link that is opened is the next one: <a href="https://www.artella.com/project/2252d6c8-407d-4419-a186-cf90760c9967/files" target="_blank" rel="noopener">Solstice Artella Project</a>
    
***

#### **Local Project**
This button opens your local Solstice Artella Project in your computer

![Local Project](../../../../img/folder.png?style=centerme)

> Artella Local Folder in my computer
![Local Project Browser](../../../../img/artella_local.jpg?style=centerme)

!!! note
    Your local Artella folder can be different because this path is configured by each user during
    <a href="https://tpoveda.github.io/solstice/solsticepipeline/artella/app/" target="_blank" rel="noopener">Artella App</a> installation

***

#### **Assets Batch Synchronization**
This button allows you to sync different assets types in batch (sync all characters, all props, etc)

![Sync Batch](../../../../img/sync.png?style=centerme)

When you click on top of the Sync button a drop down appears:

> Sync Batch Dropdown Menu
![Sync Batch Menu](../../../../img/sync_menu.png?style=centerme)

***

!!! important
    The Batch Synchronization can take quite a lot time to complete, please be patient during the process. 
    If Maya crashes during the process, just start the sync again **(you won't lose already sync assets)**

***

You can batch 3 types of assets:

1. **Characters**

    > Sync Characters
    ![Sync Batch Characters](../../../../img/sync_menu_characters.png?style=centerme)
    
    * **All**: All characters assets files are synchronized in your computer from Artella
    * **Model**: Only character models files are synchronized in your computer from Artella
    * **Textures**: Only character textures files are synchronized in your computer from Artella
    * **Shading**: Only character shading files are synchronized in your computer from Artella
    * **Groom**: Only character groom files are synchronized in your computer from Artella

2. **Props**

    > Sync Props
    ![Sync Batch Props](../../../../img/sync_menu_props.png?style=centerme)
    
    * **All**: All props assets files are synchronized in your computer from Artella
    * **Model**: Only props models files are synchronized in your computer from Artella
    * **Textures**: Only props textures files are synchronized in your computer from Artella
    * **Shading**: Only props shading files are synchronized in your computer from Artella

3. **Background Elements**

    > Sync Background Elements
    ![Sync Batch Background Elements](../../../../img/sync_menu_bg.png?style=centerme)
    
    * **All**: All background assets files are synchronized in your computer from Artella
    * **Model**: Only background models files are synchronized in your computer from Artella
    * **Textures**: Only background textures files are synchronized in your computer from Artella
    * **Shading**: Only background shading files are synchronized in your computer from Artella
    
4. **All**

    > Sync All Assets
    ![Sync Batch All](../../../../img/sync_menu_all.jpg?style=centerme)
    
    All Solstice Short Film assets will be synchronized
    
    !!! warning
        Synchronizing all assets can take **LOT OF TIME** depending on your Internet connection and the state of the 
        Artella server, so be patient.
        
***

#### ** Solstice Pipelinizer Settings**
This button opens Solstice Pipelinizer settings dialog

![Solstice Pipelinizer Settings](../../../../img/settings.png?style=centerme)

> Solstice Pipelinizer Settings Dialog
![Pipelinizer Settings Dialog](../../../../img/pipelinizer_settings_dialog.png?style=centerme)

* **Auto Check Published Versions?**: If is **checked**, any time you select an Asset in Asset Viewer, Solstice Pipelinizer
will retrieve latest **published** versions of the asset files

* **Auto Check Working Versions?**:  If is **checked**, any time you select an Asset in Asset Viewer, Solstice Pipelinizer
will retrieve if the latest **working** versions of the asset files

* **Check Lock/Unlock Working Versions?**:  If is **checked**, any time you select an Asset in Asset Viewer, Solstice Pipelinizer
will check if some **working** files (model, textures, etc) of the asset are being locked (used) by other users

!!! warning
    Enabling these settings will means that any time you select an Asset in the Assets Viewer, Pipelinizer Tool will need
    to connect to Artella Server to retrieve some information, this will take some time, so be patient.
