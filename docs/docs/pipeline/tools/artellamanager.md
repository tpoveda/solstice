# **{{ project.name }} Artella Manager**

!!! help ""
    This is the main tool used to manage the different files of the {{ project.name }} project.
  
    Using this tool you can:
    
    * **Lock** & **Unlock** specific files of the project.
    * **Sychronize** multiples files at once in of files located in your local driver or in Artella server. 
    * **Synchronize** files located at specific Artelal URL.
    
***

> Sync Operation
![Sync Process](../../../img/tools/artellamanager/3.png?style=centerme)

!!! info "Sync Result"
    <center>
    
    |          |   Description    |
    | -------- |:-------------:|
    | ![Ok Message](../../img/icons/ok.png?style=centerme) | The sync operation was completed successfully. |
    | ![Warning Message](../../img/icons/warning.png?style=centerme) | The sync was not completed because a **non critical error** error happened. |
    | ![Error Message](../../img/icons/error.png?style=centerme) | The sync was not completed because a **critical error** error happened. |
    
    </center>
    
***

## **Local Artella Manager**

With this tool you can navigate through all the files of {{ project.name }} that are already synced in your computer.

![{{ project.name }} Artella Manager - Local](../../../img/tools/artellamanager/1.png?style=centerme)

In the **files tree** you can find 2 types of different tree items: **folders** and **files**

> **Syncing Local Files**
![{{ project.name }} Artella Manager - Local | Sync Queue](../../../img/tools/artellamanager/2.png?style=centerme)

To sync specific local files (get the latest version of the file from Artella server) you just need to select the item
in the tree list. The item will be added automatically to the **Sync Queue**

!!! tip
    You can select multiples files and folders simultaneously

After selecting the files and folders you just need to press **Sync** button to start the synchronization.

***

### **Contextual Menu**

#### **Folders**

<center>

|    |      Name      |   Description    |
| -------- |:-------------:| :---------:|
| ![Artella icon](../../img/icons/artella.png?style=centerme) | **Open in Artella** | Opens folder in Artella webpage. |
| ![Set Project icon](../../img/icons/eye.png?style=centerme) | **View Locally** |  Opens folder in the operative system browser |

</center>

#### **Files**

***

##### **Local Files**

!!! info
    Files that are located only in your driver (not currently being versioned in Artella)

<center>

|    |      Name      |   Description    |
| -------- |:-------------:| :---------:|
| ![Artella icon](../../img/icons/artella.png?style=centerme) | **Open in Artella** | Opens folder in Artella webpage. |
| ![View Locally icon](../../img/icons/eye.png?style=centerme) | **View Locally** |  Opens folder in the operative system browser |
| ![Add icon](../../img/icons/add.png?style=centerme) | **Local Only - Add File** |  Adds the selected file to the Artella server, and creates its first version.

</center>

***

##### **Server Files**

!!! info
    Files that are currently being versioned by Artella

<center>

|    |      Name      |   Description    |
| -------- |:-------------:| :---------:|
| ![Artella icon](../../img/icons/artella.png?style=centerme) | **Open in Artella** | Opens folder in Artella webpage. |
| ![View Locally icon](../../img/icons/eye.png?style=centerme) | **View Locally** |  Opens folder in the operative system browser |
| ![Lock icon](../../img/icons/lock.png?style=centerme) | **Lock File** |  Lock the file in Artella server. |
| ![Unlock icon](../../img/icons/unlock.png?style=centerme) | **Unlock File** |  Unlock the file in Artella server. |
| ![Upload icon](../../img/icons/upload.png?style=centerme) | **Make New Version** |  Creates a new version of the file. |



</center>

***

## **Server Artella Manager**


With this tool you can navigate through all the files of {{ project.name }} located in Artella server.

!!! important

    ![Wait](../../../img/tools/artellamanager/serverwait.png?style=centerme)

    When using this tool, each time you enter into a folder, information form Artella is retrieved and this can take
    some time. There is a wait window that wil tell current status of the loading.

![{{ project.name }} Artella Manager - Server](../../../img/tools/artellamanager/4.png?style=centerme)

!!! tip
    ![Back and Forward](../../../img/tools/artellamanager/backforward.png?style=centerme)

    After loading a folder you can use **Back** and **Forward** buttons to move between folders quicly.

In the **files tree** you can find 4 types of different tree items: 

<center>

|          |   Description    |
| -------- |:-------------:|
| ![Question icon](../../img/icons/question.png?style=centerme) | Folders that are empty. |
| ![Folder icon](../../img/icons/folder.png?style=centerme) | Folders that are located in the root folder of Artella or inside Assets. |
| ![Asset icon](../../img/icons/teapot.png?style=centerme) | Special type of folders that contains files and folders for specific assets. |
| | Files located inside folders. |

</center>

***

> **Syncing Server Files**
![{{ project.name }} Artella Manager - Server | Sync Queue](../../../img/tools/artellamanager/5.png?style=centerme)

To sync specific server files (get the latest version of the file from Artella server) you just need to select the item
in the tree list, open its conextual menu (right-click) and select **Add to Sync Queue** option. 

After this, the item will be added to the **Sync Queue**.

!!! tip
    You can add all the files of the current opened folder by selection **Add All Items to Sync Queue** button in the top bar.

After selecting the files and folders you just need to press **Sync** button to start the synchronization.


***

## **URL Artella Manager**

> **Syncing URLS**
![{{ project.name }} Artella Manager - URL](../../../img/tools/artellamanager/6.png?style=centerme)

You just need to copy a valid Artella URL in the URL field and press the **Sync** button to synchronize that file


***

## **Sync Queue**

!!! info
    If you want to sync a folder and its contents, you will need to make sure that **Sync Subfolders** checkbox is checked (by default, it is).