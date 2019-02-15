# **How to publish shaders?**

## **Introduction**

Each time you modify a material of an asset, you need to publish the materials of that asset. 

In Solstice, to have better control over new versions of shaders, we have decided to use a data driven approach when 
working with shaders. This give us flexibility for:

* Shaders are stored in Artella in JSON file, so Lighting TDs can modify them using a text editor without necessity of 
opening them in Maya
* We can manager shaders versions very easily

When you publish a new shading file of an asset into Artella, the following steps are followed:

1. Check if textures of the asset have been puslibshed
    1. If not, the publication of the shading file is skipped
    2. If yes, the textures path of the shading file are updated if necessary to the paths of the published textures
3. All the shaders of the asset are exported in JSON file to the Solstice Shading Library
4. A JSON info file is created/modified on the shading folder for the asset. This file stores the mapping of between 
each mesh of the asset and the shader that mesh uses
5. The new shading file is published and uplaoded to Artella server as a new version
6. The exported shaders are uploaded to Artella server as a new version
7 .The export shading info file is uploaded to Artella server as a new version

***

## **Prerequisites**

* Textures for the assets MUST be published before publishing a shading files
* Shading file must follow proper nomenclature:
    * Each asset model in the shading file must be grouped in a group called {asset_name}_grp
    * Inside that grup are loacted all the meshes with proper materials applied to them
    
***

## **Workflow**

To publish new shaders we need to use Solstice Pipelinizer Tool

Open Solstice Pipelinizer Tool located in Solstice Tools Maya shelf and select the asset you want to publish.

Press **Publish New Version** button located at the bottom of the asset panel

After pressing this button, Maya will connect with Artella to get the current version of the published files. Wait 
until it finishes (it can take between 10 seconds and 2 minutes) and Solstice Publisher window will popup.

In Solstice Publisher, you will need:

1. Check only the shading checkbox
2. Write a descriptive message for the new version of the published shading file
3. Press Publish button

And that's all!