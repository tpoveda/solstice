# **Publishing a new version for model/rig files**

!!! error
    Before publishing a model/rig file, a shading version of the file needs to be already published. If you want more 
    info about this restriction please visit this **link** (ADD LINK)
    
1. Open **Maya 2017** using **Solstice Launcher**

    ![Solstice Working Button](../../../img/model_publish_0.png?style=centerme)

    ***

2. Launch **Solstice Pipelinizer** tool

    > Solstice Pipelinizer Button in Solstice Shelf
    ![Solstice Working Button](../../../img/model_publish_1.png?style=centerme)

    ***

3. Open **Model File** you want to create new version for

    ![Solstice Working Button](../../../img/model_publish_2.png?style=centerme)
    
    !!! info
        You can publish new versions without opening the file, but is **recommended** to make sure that the file
        you are going to publish is correct
    
    ***

4. Make sure that the **nomenclature** of the asset **main group** is valid.
    
    It should have the same name as the Maya scene file, which should already follows a proper Solstice nomenclature
    
    In the leaf example, its name is **S_PRP_03_dryLeaf**
    
    !!! info
        If you have to know more about Solstice Nomenclature follow this **link** (ADD LINK)
    
    > Main Asset Group has the same name as the Maya scene
    ![Solstice Working Button](../../../img/model_publish_3.png?style=centerme)
    
    ***
    
6. Make sure that model and shading files has same names on asset meshes
    
    !!! error "VERY IMPORTANT"
        Due to pipeline restrictions we need to make sure that asset **meshes located in model file and shading file
        share the same names**. If you try to publish and asset without taking into account this point, Solstice Publisher
        will **stop** the publish process during validation.
        
        ![Solstice Working Button](../../../img/shading_publish_4.png?style=centerme)
    
7. If the file has **no rig** yet, you need to create a **temporal one** :smile: (no joking) Fortunately, **Solstice Shelf** 
has available a collection of scripts to make your life easier. This rig will give layout/animation team the ability 
to translate/rotate/scale assets in Solstice world!

    !!! important
        If asset has already a rig created, you can skip this step go directly to **step 5**
    
    Launch **Solstice Rig ToolBox** tool located in **Solstice Rig Shelf**
    
    ![Solstice Working Button](../../../img/model_publish_4.png?style=centerme)
    
    ***
    
    Go to the **Props** category using arrow buttons located in bottom bar of **Solstice Rig Toolbox**
    
    ![Solstice Working Button](../../../img/model_publish_5.png?style=centerme)
    
    ***
    
    Select **main group** of the asset and press **Create Basic Rig** button
    
    ![Solstice Working Button](../../../img/model_publish_6.png?style=centerme)
    
    !!! info
        **Proxy Reduction** spinner controls the amount of geometry reduction for the proxy mesh
        
    !!! info
        Create Basic Rig functionality has support for **Undo** (by pressing Ctrl+Z), so if after creating the rig
        you are not happy with the result (maybe you want a proxy with lower geometry) you can undo and repeat the 
        operation without problems.
    
    ***
    
    ![Solstice Working Button](../../../img/model_publish_7.png?style=centerme)
    
    ***
    
8. **Remove** all custom shaders from model file

    Model file only can have standard Maya shaders stored in it. Remove all nodes to make sure that the model.
    
    > Our model file has a custom blinn1 node. We need to remove it
    ![Solstice Working Button](../../../img/model_publish_8.png?style=centerme)
    
    ***
    
    > Our model file only has default Maya shader nodes :smile:
    ![Solstice Working Button](../../../img/model_publish_9.png?style=centerme)
    
    ***

9. **Save** your changes

    !!! info
        If you do not have lock the file Maya will pop up a message telling you if you want to **lock** the 
        file. Press **Yes**, this will ensure you that no other artists in the project updates that file while
        you are working on it
    
    ***
 
10. Open **Solstice Publisher** by pressing **>PUBLISH NEW VERSION<** button located in the bottom right corner of  **Solstice Pipelinizer**
    
    ![Solstice Working Button](../../../img/shading_publish_7.png?style=centerme)
    
    !!! warning
        When **Solstice Publisher** is launched, it checks for the latest version by connecting to **Artella server**
        This **can take time**, so be **patient**. You will see the following dialog in the center of your Maya viewport.
        
        ![Solstice Working Button](../../../img/solstice_publisher_wait.png?style=centerme)
    
    ***
    
11. Uncheck **TEXTURES** & **SHADING** checkboxes in Solstice Publisher. Make sure you only have checked **MODEL**.
Also you need to write a **descriptive comment** of the changes you have done in the version you are creating.

    Then press **Publish** button.
    
    !!! info
        Solstice Publisher will give you information about the current version of the file and the new version
        that will be created
        
    ![Solstice Working Button](../../../img/model_publish_10.png?style=centerme)
    
    ***
 
12. Solstice Publisher **Validation Tool** window will appear. Wait while the process finishes.

    This tool basically validates the status of your current model by doing the following checks:
                
    - [x] Check that model file path is valid (is located in a valid Solstice Project folder)
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
    
13. Once the validation is completed, a popup window will appear telling you that the validation was correct. Press
**Yes** button to continue with the creating of a new version process or **No** to cancel the operation.

    ![Solstice Working Button](../../../img/model_working_8.png?style=centerme)
    
14. Wait until the new version is created. Once the version is finished, Solstice Publisher will automatically sync
that version in your computer locally. Wait until the following sync screen is gone:
    
    ![Solstice Working Button](../../../img/model_working_9.png?style=centerme)
    
    ***

15. If everything is fine you will a lot of green color in your screen :smile: and you have published a new version of
the file.

    ![Solstice Working Button](../../../img/model_working_10.png?style=centerme)
    
    ***
    
    > The new version created in Artella :smile:
    ![Solstice Working Button](../../../img/model_working_11.png?style=centerme)
    
***

!!! warning
    If something is wrong during the process, please check the log of the tool. If you are not sure what's happening, 
    please send log image to Solstice TDs, so we can check what is wrong with your file.


