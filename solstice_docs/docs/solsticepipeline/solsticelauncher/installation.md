### **Instructions**

???+ example "Windows"

    !!! error
        If you experience problems during Solstice Pipeline installation please uninstall them manually first

    1. **Download the Solstice Launcher Executable**
        * Visit <a href="https://www.artella.com/" target="_blank" rel="noopener">www.artella.com</a>
        * Create a new Account **(Sign up button)** if you do not have one
        * Access Solstice Project and navigate to the **"Files"** area
        
        > Scripts Folder in Solstice Project
        ![Solstice Launcher Install 0](../../img/solstice_installer_0.png?style=centerme)
        
        * Go into **PIPELINE** folder located inside Scripts folder
    
    2. **Synced last version of Solstice Luancher**
        * Select **solstice_launcher.exe** and press **...** symbol at the top right of your screen (look image below)
        * In the menu, press **Sync Selected** to sync the file to the latest version available
    
        > Sync Selected solstice_launcher.exe
        ![Solstice Launcher Install 1](../../img/solstice_installer_1.png?style=centerme)
        
        * Wait until file is **synced**
        * The file is located in your local **Artella** folder
        
        > solstice_launcher.exe synced in your local drive
        ![Solstice Launcher Install 2](../../img/solstice_installer_2.png?style=centerme)
        
        ***
        
        > solstice_launcher.exe
        ![Solstice Launcher Install 3](../../img/solstice_installer_3.png?style=centerme)
        
        ***
        
    !!! tip
        Solstice Launcher for Windows does not need any kind of installation. At this point, you can copy
        **solstice_launcher.exe** and copy it anywhere in your computer (for example, your Desktop)
        
    ***
    
    !!! tip "Manual Installation"
    
        To install Solstice Tools manaully follow next steps:
        
        * Sync in Artella Files (in Pipeline/Scripts folder) the file called **solstice_pipeline.zip**
        
        ![Solstice Launcher Install 12](../../img/solstice_installer_12.png?style=centerme)
        
        * Open it and extract **solistce_pipeline** in **Documentos/maya/2017/scripts**
        
        ![Solstice Launcher Install 13](../../img/solstice_installer_13.png?style=centerme)

        * Open **userSetup.py** file in the samer folder (if that file does not exists create a new file with that name
        and extension). At the end of the file write:
        
                import maya.utils
                def run_solstice_tools():
                        import solstice_pipeline
                        solstice_pipeline.init()
                maya.utils.executeDeferred(run_solstice_tools)
        
        ![Solstice Launcher Install 14](../../img/solstice_installer_14.png?style=centerme)
        
        * Launch Maya with its normal shortcut
        
        ![Solstice Launcher Install 15](../../img/solstice_installer_15.png?style=centerme)

            
        
        
???+ example "MacOS"
    
    !!! error "IMPORTANT"
        **If you have already installed Solstice Tools previously**, you need to **DELETE** **modules** and 
        **solstice_pipeline** folders located in **Library/Preferences/Autodesk/maya** folder
        
        ![Solstice Launcher Install 10](../../img/solstice_installer_10.png?style=centerme)
    
    ***
        

    1. **Download the Solstice Launcher Executable**
        * Visit <a href="https://www.artella.com/" target="_blank" rel="noopener">www.artella.com</a>
        * Create a new Account **(Sign up button)** if you do not have one
        * Access Solstice Project and navigate to the **"Files"** area
        
        > Scripts Folder in Solstice Project
        ![Solstice Launcher Install 0](../../img/solstice_installer_0.png?style=centerme)
        
        * Go into **PIPELINE** folder located inside Scripts folder
        
    2. **Synced last version of Solstice Luancher**
        * Select **solstice_mac_installer.pkg** and press **...** symbol at the top right of your screen (look image below)
        * In the menu, press **Sync Selected** to sync the file to the latest version available
        
        > Sync Selected solstice_mac_installer.pkg
        ![Solstice Launcher Install 4](../../img/solstice_installer_4.png?style=centerme)
        
        * Wait until file is **synced**
        * The file is located in your local **Artella** folder
        * Double click on it to open the installer
        
        ![Solstice Launcher Install 5](../../img/solstice_installer_5.png?style=centerme)
        
        * Follow the steps (just press Continue button) in all the windows
        
        ![Solstice Launcher Install 6](../../img/solstice_installer_6.png?style=centerme)
        
        ![Solstice Launcher Install 7](../../img/solstice_installer_7.png?style=centerme)
        
        * Press **Install** button
        
        ![Solstice Launcher Install 8](../../img/solstice_installer_8.png?style=centerme)
        
        !!! warning
            During installation maybe MacOS will ask for your password. Just write to continue the installation.
        
        * Press **Close** button to close installation window
        
        ![Solstice Launcher Install 9](../../img/solstice_installer_9.png?style=centerme)
        
        * Execute Maya using its normal shortcut
        
        ![Solstice Launcher Install 11](../../img/solstice_installer_11.png?style=centerme)

        


        
        
        
        
        
        
        