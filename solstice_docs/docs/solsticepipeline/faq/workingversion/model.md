# **Creating a new working version for model/rig files**

!!! error
    Before submitting a model/rig file, a shading version of the file needs to be already submitted. If you want more 
    info about this restriction please visit this **link** (ADD LINK)


1. Open **Maya 2017** using **Solstice Launcher**

    ![Solstice Working Button](../../../img/model_working_0.png?style=centerme)

    ***

2. Launch **Solstice Pipelinizer** tool

    > Solstice Pipelinizer Button in Solstice Shelf
    ![Solstice Working Button](../../../img/model_working_1.png?style=centerme)

    ***

3. Open **Model File** you want to create new version for

    ![Solstice Working Button](../../../img/model_working_2.png?style=centerme)
    
    !!! info
        You can create new versions without opening the file, but is **recommended** to make sure that the file
        you are woing to version is correct
    
    ***
    
4. Open **Solstice Publisher** by pressing **> PUBLISH NEW VERSION <** button located in the bottom right corner of  ** Solstice Pipelinizer**

    ![Solstice Working Button](../../../img/model_working_3.png?style=centerme)
    
    !!! warning
        When **Solstice Publisher** is launched, it checks for the latest version by connecting to **Artella server**
        This **can take time**, so be **patient**. You will see the following dialog in the center of your Maya viewport.
        
        ![Solstice Working Button](../../img/solstice_publisher_wait.png?style=centerme)

    ***

5. Uncheck **TEXTURES** & **SHADING** checkboxes in Solstice Pipelinizer. Make sure you only have checked **MODEL**.
Also you need to write a **descriptive comment** of the changes you have done in the version you are creating.

    Then press **Publish** button.
    
    !!! info
        Solstice Publisher will give you information about the current version of the file and the new version
        that will be created
        
    ![Solstice Working Button](../../../img/model_working_4.png?style=centerme)
    
    ***
    
    !!! info
        As an example, here is the version history before creating a new version of the asset
        
        ![Solstice Working Button](../../img/model_working_5.png?style=centerme)
        
    ***
    
6. Solstice Publisher **Validation Tool** window will appear. Wait while the process finishes.

    This tool basically validates the status of your current model by doing the following checks:
                
    - [x] Check that model file path is valid (is loated in a valid Solstice Project folder)
    - [x] Check if model file is locked by other user
    - [x] Auto locks file if you have not already done it
    - [x] Open model Maya file is the model file is not already opened
    - [x] Clean old plugins/unknwown plugins from the scene
    - [x] Check that main group asset nomenclature is valid (follow Solstice nomenclature rules)
    - [x] Check that model file has no shaders stored in it
    - [x] Check that model file has valid proxy and hires groups
    - [x] Check that model groups store proper mesh info
    - [x] Automatically creates a Solstice Tag node and fills it with proper information
    - [x] Check that the asset has valid shading file published
    - [x] Check that shading file and model file has same meshes stored on them
    - [x] Updates Tag data info with info about the shaders stored in the shading file
    - [x] Stores the changes done by the validator in the model file
    - [x] Unlock the file before creatng a new version
    - [x] Submit a new version into Artella server
    
    ***             

    ![Solstice Working Button](../../../img/model_working_6.png?style=centerme)
    
    !!! note "Student License"
        If you are working with a Maya Student License version press please Yes to the popup that appears.
        This popup appears because Solstice Publisher will automatically try to save you current file
        before creating the new file version.
        
        Do not worry because the tool also cleans the student license before submitting the scene.
        ![Solstice Working Button](../../../img/model_working_7.png?style=centerme)
        
    !!! bug
        You will see in some parts that you are publishing instead of creating a new version. Don't worry
        because under the hood you're creating a new version of the file not publishing it. 
        
        We use the same tool for create working version and for publihsing asset files so at this moment there 
        are some inconsistences that will be fixed in a future

    ***
    
7. Once the validation is completed, a popup window will appear telling you that the validation was correct. Press
**Yes** button to continue with the creating of a new version process or **No** to cancel the operation.

    ![Solstice Working Button](../../../img/model_working_8.png?style=centerme)
    
8. Wait until the new version is created. Once the version is finished, Solstice Publisher will automatically sync
that version in your computer locally. Wait until the following sync screen is gone:
    
    ![Solstice Working Button](../../../img/model_working_9.png?style=centerme)
    
    ***

9. If everything is fine you will a lot of green color in your screen :smile: and you have published a new version of
the file.

    ![Solstice Working Button](../../../img/model_working_10.png?style=centerme)
    
    ***
    
    > The new version created in Artella :smile:
    ![Solstice Working Button](../../../img/model_working_11.png?style=centerme)
    
***

!!! warning
    If something is wrong during the process, please check the log of the tool. If you are not sure what's happening, 
    please send log image to Solstice TDs, so we can check what is wrong with your file.