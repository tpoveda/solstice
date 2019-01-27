???+ example "Windows"
    !!! failure
        First of all, make sure that you have installed **Maya 2017 Update 5** in your computer and **Arnold 2.0.2.1**. 
        It's very important that you have installed these exact versions of Maya and Arnold installed, otherwise 
        Yeti plugin won't load properly.
        
    ### **Download Yeti**
    
    **Download Yeti 2.2.1 for Maya 2017 (Windows):** [DOWNLOAD](https://drive.google.com/open?id=1N94Rrw89R6UqbG1PD4IjirbJcrOcC06_)
    
    After downloading it, open .zip file and you will find:
    
    1. **rlm** folder
    2. **yeti_solstice** folder
    3. **yeti_setup.bat** file
    
    > Folders inside yeti_solstice.zip fil
    ![Yeti Install 0](../../img/yeti_install_win_0.png?style=centerme)
    
    ***
    
    ### **Extract Yeti**
    
    Extract **all files** on your **C:\\** drive
    
    > Extracted Yeti files on C:
    ![Yeti Install 1](../../img/yeti_install_win_1.png?style=centerme)

    ***
    
    ### **Setup Yeti**
    
    Execute yeti_setup.bat. This file will create some environment variables in your computer, so Maya can find your 
    Yeti installation when is launched.
    
    !!! warning
        Maybe you will need to execute **yeti_setup.bat** with adminstrator privileges
        
    > yeti_setup.bat creates some environment variables in your computer
    ![Yeti Install 2](../../img/yeti_install_win_2.png?style=centerme)
    
    ***
    
    ### **Load Yeti Plugin**
    
    After setting up Yeti, you need to launch Maya and open **Maya Plug-in Manager**
    
    > Opening Maya Plug-in Manager Window
    ![Yeti Install 3](../../img/yeti_install_win_3.png?style=centerme)
    
    ***
    
    If the installation was successfull you should see pgYetiMaya.mll in the list of Maya plugins. Check Loaded and 
    Auto load cheboxes to load Yeti plugin.
    
    > Maya Plug-in Window with Yeti plugin loaded successfully
    ![Yeti Install 4](../../img/yeti_install_win_4.png?style=centerme)
    
    ***
    
    > After Yeti plugin is loaded, Yeti shelf will be created automatically
    ![Yeti Install 5](../../img/yeti_install_win_5.png?style=centerme)
    
    ***
    
    ### **Configuring Arnold**
    
    !!! warning
        For each Maya scene that uses Arnold we need to fill the procedural search path of Arnold renderer with the 
        following folder: **C:/yeti_solstice/bin**
        
    > Setting up procedural search pats for Arnold
    ![Yeti Install 6](../../img/yeti_install_win_6.png?style=centerme)
    
    ***
    
    ### **Testing Yeti**
    
    At this point, Yeti plugin should work propertly with Arnold renderer 2.0.2.1. To test if all was installed 
    propertly, download this test scene: DOWNLOAD. Open the file in Maya and click render button. 
    
    !!! info
        Make sure you are using **Arnold renderer 2.0.2.1** when rendering the scene test

    > If you render the test scene, you should see this amazing render!
    ![Yeti Install 7](../../img/yeti_install_win_7.png?style=centerme)

??? example "MacOS"
    ** Work in Progress**
