# **Assets Manager**

This is the main tool used by all artists in Solstice Short Film to:

* **Synchronize** specifics assets (get latest available version)
* Check Assets **versions**
* **Upload** to Artella server new in progress version for assets
* **Publish** assets that are ready to be used in production
* **Open** specific assets files (model scene, shading scene, textures, etc)
* **Import/Reference** specific published assets into current scene

***

## **Assets Viewer**
This is the main work area of the tool, here you can select Assets and filter them by its type. At this moment all 
short film assets are organized in 4 groups:

* **Background Elements**
* **Characters**
* **Props**
* **Sets** (not being used at this moment)

> Solstice Pipelinizer Assets Viewer
![Pipelinizer Assets Viewer](../../../../img/pipelinizer_assets_viewer.png?style=centerme)

!!! warning
    Assets Viewer only will show already synced assets, so if you cannot see any assets make sure that you have
    sync your assets using Sync Batch functionality explained above

!!! tip
    Using left buttons you can filter assets by type
    
> Assets Viewer filtering characters
![Pipelinizer Assets Viewer](../../../../img/pipelinizer_char_filter.png?style=centerme)

***

## **Solstice Pipelinizer Asset**

Each Solstice Short Film assets appears in Solstice Pipelinizer **Assets Viewer**

We support **4** types of **Assets Types**:

* **Background Elements**
* **Characters**
* **Props**
* **Sets** (not being used at this moment)

> Solstice Pipelinizer Asset
![Pipelinizer Asset](../../../../img/summer_asset2.png?style=centerme)

A Pipelinizer Asset shows:

* An **image** that represents what the asset contains
* The **name** of the assets (using proper nomenclature)

***

### Asset Properties

> Summer Asset Properties
![Summer Asset Properties](../../../../img/asset_properties.png?style=centerme)

***

### Asset Contextual Menu

> Asset Contextual Menu
![Asset Contextual Menu](../../../../img/asset_contextual_menu.png?style=centerme)


* **Synchronize**: Here you have access to options to synchronize specific asset files (working and published versions)
    * **All**: Synchronize latest version of all asset files
    * **Model**: Synchronize latest version of the asset model file
    * **Textures**: Synchronize latest version of the asset textures files
    * **Shading**: Synchronize latest version of the asset shading file
    !!! info
        Take into account that this contextual menu can vary depending of the asset type. For example, **character** 
        assets also have the option to sync **grooming** files
        
        > Asset Contextual Menu
        ![Charactrer Asset Groom Contextual Menu](../../../../img/solstice_asset_contextual_menu_groom.png?style=centerme)
        
    
* **Import to current scene ...**: **Imports** asset **last synced published version** in scene

* **Reference in current scene ...**: **Reference** asset **lsat synced published version** in scene


***

### Asset Properties

![Asset Properties](../../../../img/solstice_asset.png?style=centerme)

***

<center>

|    |      Description      | 
| -------- |:------------:|
| ![Asset Properties Red](../../../../img/color_red.png?style=centerme) | Asset basic information (Name and Image) |
| ![Asset Properties Pink](../../../../img/color_pink.png?style=centerme) | Access Quick Actions |
| ![Asset Properties Purple](../../../../img/color_purple.png?style=centerme) | Asset Files Access |
| ![Asset Properties Blue](../../../../img/color_blue.png?style=centerme) | Asset Files Working Version info |
| ![Asset Properties Green](../../../../img/color_green.png?style=centerme) | Asset Files Published Version info |
| ![Asset Properties Yellow](../../../../img/color_yellow.png?style=centerme) | Asset Description |
| ![Asset Properties Orange](../../../../img/color_orange.png?style=centerme) | Asset create new Working/Published version buttons |


</center>

***

#### **Asset Basic Info**

![Asset Basic Info](../../../../img/asset_basic_info.png?style=centerme)

In this section you can find two important asset infos:

* **Asset Name**: This is the name of the asset with proper Solstice Pipeline Nomenclature
* **Asset Image**: Descriptive preview image of the asset

***

#### **Asset Quick Actions**
        
![Asset Quick Actions](../../../../img/asset_quick_actions.png?style=centerme)

In this section you can find 3 important quick action buttons:

* **Folder**: If you press this button, the folder within your hard drive that contains the asset will be opened
automatically. **Useful to access asset folders inside Artella directory quickly**

* **Artella**: If you press this button, the Artella asset path will be opened in your default we browser.
**Useful to access asset Artella files quickly**

* **Check**: If you press this button, the asset working and published files version will be checked. This will update:
    1. Updates all file access state buttons (shows the user which files are locked by others)
    2. Updates working/published version info (shows the user which versions of the asset files are sync locally)
    
    > This dialog will appear while Check process is being executed ...
    ![Check Quick Action](../../../../img/asset_check_button.png?style=centerme)

    
    !!! warning ""
        This process can take a while to complete
        
***

#### **Asset File Access**

![Asset File Access](../../../../img/asset_file_access.png?style=centerme)

In this section you can access to all asset files. This section is divided into 2 categories:

1. **Working**: In this category you can access to all assets files that are versioned as working verions (versions that
are not ready to be used in production yet).

2. **Published**: In this category you can access to all assets files that are versioned as published versions (versions
that are ready to be used in production).

By pressing on the buttons you will open the different files

If you click in a button and the file is not opened, that means that the file does not exists in your locally (in 
your hard drive). This can be caused by:

* You have not synced the asset files (so you will need to synchronize them)
* The file has not that files created yet (this is quite usual when an asset has not published versions yet)

***

!!! info "Lock/Unlock files"
    When working with files (specially with working versions), you can lock files so other Solstice artists cannot 
    modify your file accidentally. You can lock/unlock (unlock your locked files) directly in this section (without the 
    need of going to Artella webpage) following next steps:
    
    > Press Check button, to update the lock/ulnock the status file of your files
    ![Asset File Lock 0](../../../../img/asset_lock_0.png?style=centerme)
    
    > Lock/Unlock buttons will appear under the file buttons
    ![Asset File Lock 1](../../../../img/asset_lock_1.png?style=centerme)
    
    > Lock Asset File in Artella
    ![Artella Lock Asset File](../../../../img/lock_asset_file.png?style=centerme)
    
    ***
    
    ##### Lock/Unlock States
    
    <center>
    
    | Button State   |      Description      | 
    | :--------: |:------------:|
    | ![Unlock Button](../../../../img/unlock_button.png?style=centerme) | Asset file is not locked by anyone. Click on it to lock it. |
    | ![Lock Button](../../../../img/lock_button.png?style=centerme) | Asset file is locked by you. Click on it to unlock the file |
    | ![Other user locked](../../../../img/file_lock_button.png?style=centerme) | Asset file is locked by other user. File can't be lock until the other user unlock it |
    | ![Not available](../../../../img/file_not_found_button.png?style=centerme) | Asset file does not exists in Artella server yet |
    
    </center>
        
***

#### **Asset Files Versions Info**

This section is divided into 2 parts:

1. **Working** asset files version info
2. **Published** asset files version info

Those sections shows the following info:

* **Visual guide** showing the **status** of a specific asset file
* **Current version** of the file **locally** (in your hard drive)
* **Latest version** file in Artella
* Button that shows **more info** of the asset file (textures files associated, etc)

!!! bug
    Sometimes **working** version info is not updated properly and will appear as invalid. Future version will have this 
    bug fixed.    

> Each asset file will be added to the info section
![Asset File Info](../../../../img/asset_info.png?style=centerme)

***

##### Status Icon

|   |      Description      | 
| :--------: |:------------:|
| ![Ok status](../../../../img/ok.png?style=centerme) |Asset file is valid. In **published section**, this means that asset file is ready for production |
| ![Warning status](../../../../img/warning.png?style=centerme) | Asset file has something wrong in it. **Contact TD for more info about how to solve this** |
| ![Error status](../../../../img/error.png?style=centerme) | Asset file does not exists yet |

##### File Category

Each asset file has a category:

* **MODEL**: This is the file that contains the model and rig of the asset
* **SHADING**: This is the file that contains shading version of the asset with all the asset shaders
* **TEXTURES**: Collection of textures used by asset shaders

!!! info "Custom asset files"
    Some asset type, such as characters, can have other file types such as for example:
    
    * **GROOM**: This is the file that contains groom info for the character
    
    
##### File Versions

|   |      Description      | 
| :--------: |:------------:|
| ![Local version](../../../../img/hdd.png?style=centerme) | This is the file asset version that is located locally (in your hard drive) |
| ![Artella version](../../../../img/artella.png?style=centerme) | This is the file asset version that is located in Artella server |

With this info you can have different scenarios:

* Your Local version is lower than Artella version: This means that you need to **sync** the asset file because exist a **newer** version in Artella server
* Your Local version is the **same** as Artella version: This means that you have the **latest** available version synced in your computer

##### More Info

This button will popup a new window that shows more info about the asset file

!!! bug
    This button is not used at this moment and maybe will removed in future versions of the tool

***

#### **New Version Buttons**

![Asset File Info](../../../../img/new_version_buttons.png?style=centerme)

Those buttons are used to create new **working** versions and to **publish** assets

For more info about how to create new version and publish assets please go to the following links:

* [How to upload new working versions of an asset?](https://tpoveda.github.io/solstice/solsticepipeline/faq/workingversion/)
* [How to publish an asset?](https://tpoveda.github.io/solstice/solsticepipeline/faq/publishversion/)


    
    
