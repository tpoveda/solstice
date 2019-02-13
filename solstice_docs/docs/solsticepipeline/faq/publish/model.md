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
        you are woing to version is correct
    
    ***

4. Make sure that the nomenclature of the asset main group is valid.
    
    It should have the same name as the Maya scene file, which should already follows a proper Solstice nomenclature
    
    In the leaf example, its name is **S_PRP_03_dryLeaf**
    
    !!! info
        If you have to know more about Solstice Nomenclature follow this **link** (ADD LINK)
    
    > Main Asset Group has the same name as the Maya scene
    ![Solstice Working Button](../../../img/model_publish_3.png?style=centerme)
    
    ***
    
5. If the file has **no rig** yet, you need to create a **temporal one** :smile: (no joking) Fortunately, **Solstice Shelf** 
has available a collection of scripts to make your life easier. This rig will give layout/animation team the ability 
to translate/rotate/scale assets in Solstice world!

    !!! important
        If asset has already a rig created, you can skip this step go directly to **step 5**
    
    Launch **Solstice Rig ToolBox** tool located in **Solstice Rig Shelf**
    
    > Solstice Pipelinizer Button in Solstice Shelf
    ![Solstice Working Button](../../../img/model_publish_4.png?style=centerme)
    
    ***
    
    Go to the **Props** category using arrow buttons located in bottom bar of **Solstice Rig Toolbox**
    
    > Solstice Pipelinizer Button in Solstice Shelf
    ![Solstice Working Button](../../../img/model_publish_5.png?style=centerme)
    
    ***
    
    Select **main group** of the asset and press **Create Basic Rig** button
    
    > Solstice Pipelinizer Button in Solstice Shelf
    ![Solstice Working Button](../../../img/model_publish_6.png?style=centerme)
    
    !!! info
        **Proxy Reduction** spinner controls the amount of geometry reduction for the proxy mesh
        
    !!! info
        Create Basic Rig functionality has support for **Undo** (by pressing Ctrl+Z), so if after creating the rig
        you are not happy with the result (maybe you want a proxy with lower geometry) you can undo and repeat the 
        operation without problems.
    
    ***
    
    > Solstice Pipelinizer Button in Solstice Shelf
    ![Solstice Working Button](../../../img/model_publish_7.png?style=centerme)
    
    ***
 
 **FINISH**





