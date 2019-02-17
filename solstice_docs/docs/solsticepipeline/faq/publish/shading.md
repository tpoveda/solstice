# **Publishing a new version for shading files**

1. Open **Maya 2017** using **Solstice Launcher**

    ![Solstice Launcher](../../../img/shading_publish_0.png?style=centerme)

    ***

2. Launch **Solstice Pipelinizer** tool

    > Solstice Pipelinizer Button in Solstice Shelf
    ![Solstice Pipelinizer](../../../img/shading_publish_1.png?style=centerme)

    ***

3. Open **Shading File** you want to create new version for

    ![Shading File](../../../img/shading_publish_2.png?style=centerme)
    
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
    ![Solstice Working Button](../../../img/shading_publish_3.png?style=centerme)
    
    ***
    
5. Make sure that model and shading files has same names on model meshes
    
    !!! error "VERY IMPORTANT"
        Due to pipeline restrictions we need to make sure that asset **meshes located in model file and shading file
        share the same names**. If you try to publish and asset without taking into account this point, Solstice Publisher
        will **stop** the publish process during validation.
        
        ![Solstice Working Button](../../../img/shading_publish_4.png?style=centerme)
        
        
6. Open **Hypershade Editor** and make sure that shaders are rename following a proper nomenclature
    
    !!! important
        If you asset has more than one shader you will need to **repeat this process for each of the shaders** of the asset
    
    Shaders don't follow a specific nomenclature and we are not forcing to do that (just because this was not defined at
    the beginning of the project and also our tools don't depend on shader names to work properly).
    
    On the other hand, we **MUST** check that Arnold Shader Node (aiStandardSurface) and and the **shadingEngine** that is
    connected to are **renamed properly**
    
    ***
    
    > Invalid Shader Nomenclature
    ![Arnold shader node](../../../img/shading_publish_5.png?style=centerme)
    
    ***
    
    You need to check the following points:
    
    1. **Arnold Shader Node** must follow this nomenclature: **{ASSET_NAME}_{SHADER_NAME}**
        
        In our example:
        
        * **{ASSET_NAME}** is **S_PRP_03_DRYLEAF**
        * **{SHADER_NAME}** is **branches_green_high**
        
        So the name of the **Arnold Shader Node** is **S_PRP_03_dryLeaf_branches_green_high**
            
        !!! tip
            You can retrieve **{ASSET_NAME}** from different places:
            
            1. The name of the Maya asset scene
            2. In Solstice Pipelinizer all the assets showed in the Asset Viewer are named with the asset name
            
    2. **shaderEngine node** has the **same name** of the Arnold node followed by and **SG** prefix
        
        In our example:
        
        **S_PRP_03_dryLeaf_branches_green_highSG**
    
    3. **Save** your changes
    
    !!! info
        If you do not have lock the file Maya will pop up a message telling you if you want to **lock** the 
        file. Press **Yes**, this will ensure you that no other artists in the project updates that file while
        you are working on it
    
    ***
    
    > Valid Shader Nomenclature
    ![Arnold shader node](../../../img/shading_publish_6.png?style=centerme)
    
    !!! warning
        If you asset shaders does not follow those rules and you try to publish and asset without taking into account 
        this point, Solstice Publisher will **stop** the publish process during validation.
   
    ***
    
    !!! tip
        Is also recommmended to remove **unused shader nodes** from shader scene file to avoid having useless nodes
        in scenes. Also, take into account that only shaders applied to asset meshes will be published and used.
        
        ![Solstice Working Button](../../../img/delete_unused_shaders.png?style=centerme)
        
    ***
    
7. Open **Solstice Publisher** by pressing **>PUBLISH NEW VERSION<** button located in the bottom right corner of  **Solstice Pipelinizer**
    
    ![Solstice Working Button](../../../img/shading_publish_7.png?style=centerme)
    
    !!! warning
        When **Solstice Publisher** is launched, it checks for the latest version by connecting to **Artella server**
        This **can take time**, so be **patient**. You will see the following dialog in the center of your Maya viewport.
        
        ![Solstice Working Button](../../../img/solstice_publisher_wait.png?style=centerme)
    
    ***
    
8. Uncheck **TEXTURES** checkboxes in Solstice Publisher and write a descriptive comment with the changes of this version.
Press **Publish** button.

    !!! info "IMPORTANT"
        You will notice that when you check **SHADING** checkbox, **MODEL** checkbox is automatically selected. This
        is complete normal. This means that each time you publish a shading file a new model file will be published.
        
        This is happening because when a shader file is published, Solstice Publisher generates some data related with 
        shaders is stored in the model file (in the form of MetaData). This data is very important because thanks to 
        this data later we can **reconstruct all the asset shaders on the fly!**
        
    ![Solstice Working Button](../../../img/shading_publish_8.png?style=centerme)
    
    ***
    
9. Solstice Publisher **Validation Tool** window will appear. Wait while the process finishes.
    
    !!! warning "Saving File"
        During the validation process some save operations are done. If you use a Student License
        Maya version, a pop up will appear each time Maya tries to saves the file, so pay attention
        to the process and press **Yes** button each time this popup appears
    
    This tool automatically validates the status of your current shading and model fiels by doing the following checks:
    
    - [x] Check that model file path and shading file path are valid (are located in a valid Solstice Project folder)
    - [x] Check if model file and shading files are locked by other user
    - [x] Check that main group asset nomenclature are valid in both model and shading files (follow Solstice nomenclature rules)
    - [x] Synchronizes the last version of the textures files
    - [x] Creates a backup file of the shading file (this is done in case the shading validation process fails and your can recover your original work)
    - [x] Checks that model file has valid hires and proxy meshes groups
    - [x] Auto locks shading file if you have not already done it
    - [x] Automatically updates shader textures path to make sure that latest published textures are being used by the shaders
    - [x] After changing textures, the file size of the new shading file is checked and checks that the size difference is not very big between this one and the original
    - [x] Clean old plugins/unknwown plugins from the shading file
    - [x] Check that shaders have a valid nomenclature
    - [x] Generates shader JSON file and submits that file to Artella
    - [x] Submit a new working version of model and shading files into Artella server
    - [x] Publish a new version of model and shading files into Artella server
    - [x] Unlocks shading and model files after the publish process is completed
    
    !!! warning "IMPORTANT"
        If something went wrong during validation, can happen that validation process have added some info into 
        the shading file that you don't want.
         
        In that case, you can recover your **original** shading file without problems.
        You will find a file called with the same name of the shading Maya file but with a prefix **_BACKUP**. Just
        rename the file with its original name and replace the invalid shading file that has been modified by the 
        validation process.
   
    ***
       
    ![Solstice Working Button](../../../img/shading_publish_9.png?style=centerme)
    
    ***
    
    ![Solstice Working Button](../../../img/shading_publish_10.png?style=centerme)
    
    ***
    
    !!! error
        If something is wrong during the process, please check the log of the tool. If you are not sure what's happening, 
        please send log image to Solstice TDs, so we can check what is wrong with your file.
        
        In this example the name of the shaders were not valid

        ![Solstice Working Button](../../../img/shading_publish_11.png?style=centerme)
        
    ***        
    
    !!! note "Student License"
        If you are working with a Maya Student License version press please Yes to the popup that appears.
        This popup appears because Solstice Publisher will automatically try to save you current file
        before creating the new file version.
        
        Do not worry because the tool also cleans the student license before submitting the scene.
        ![Solstice Working Button](../../../img/model_working_7.png?style=centerme)
    
    ***             
        
10. Once the validation is completed, a popup window will appear telling you that the validation was correct. Press
**Yes** button to continue with the creating of a new version process or **No** to cancel the operation.

    ![Solstice Working Button](../../../img/shading_publish_12.png?style=centerme)
    
    ***

11. Wait until the new version is created. Once the version is finished, Solstice Publisher will automatically sync
that version in your computer locally. Wait until the following sync screen is gone:
    
    ![Solstice Working Button](../../../img/model_working_9.png?style=centerme)
    
    ***
    
12. If everything is fine you will a lot of green color in your screen :smile: and you have published a new version of
the file.

    ![Solstice Working Button](../../../img/shading_publish_13.png?style=centerme)
    
    ***

13. Last step is to generate and Publish JSON shader files using **Solstice Shader Library Tool**. You can open 
**Solstice Shader Library Tool** using proper button located in Solstice TD Shelf
    
    > Solstice Shader Library Tool is located in TD shelf
    ![Solstice Working Button](../../../img/shading_publish_14.png?style=centerme)
    
    ***
    
    > Solstice Shader Library Tool UI
    ![Solstice Working Button](../../../img/shading_publish_17.png?style=centerme)
    
    ***
    
14. In the Asset Viewer left panel, select the prop you want to publish shaders of and wait until 
**Solstice Shaders Publisher** window appears
    
    ![Solstice Working Button](../../../img/shading_publish_18.png?style=centerme)
    
    > Solstice Shaders Publisher UI
    ![Solstice Working Button](../../../img/shading_publish_19.png?style=centerme)
    
    ***
    
15. In this **Solstice Shaders Publisher** window you will see a list of shaders the current asset meshes have applied. 
Check the ones you want to publish and press **Export and Publish** button

    !!! warning "IMPORTANT"
        Take into account that if the shader file has unused nodes (nodes that are not applied into any mesh)
        Those shaders won't be published. **If you need those shaders to be published, plesase contact Solstice TD team!**
    
    ***
    
    > Wait until all shaders are exported and published
    ![Solstice Working Button](../../../img/shading_publish_20.png?style=centerme)

    ***

16. Once export and publish process is finished you will be able to see new shaders in the Shaders Viewer Panel

    ![Solstice Working Button](../../../img/shading_publish_21.png?style=centerme)
    
    ***
    
17. To test that everything worked fine you can follow the steps describe in the following **link** **(ADD LINK)**
