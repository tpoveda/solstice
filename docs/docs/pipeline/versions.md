# **Versions**

**All files** in {{ project.name }} Short Film (Maya files, textures, etc) are versioned by Artella. This is helpful because allow us
to keep an history of each file used in the short film.

When a new version of a file is published the old version is not deleted from the server, that version is stored but 
is not visible by the user. The good thing, is that we can do a roll-back (recover an old version) at any moment. 

!!! info "What is a version roll-back?"
    When we do a version roll-back we are basically telling to Artella:
    
    *Hi Artella, I want to recover an old version, and make that version the latest available version for the team*
    
    This implies that when we do a roll-back we basically retrieve a specific old version and a new version is created
    with that file
    
    > {{ project.name }} Roolback
    ![{{ project.name }} Roolback](../img/{{ project.name }}_rollback.png?style=centerme)

***

## **Version Info**
A version stores different type of info inside it:

* **File Data**: This is the file itself (texture, Maya file, etc)
* **Version Number**: Unique number of the current version starting from **1**
* **User Name**: Name of the user who created the version
* **User Image**: Image of the user who created the version
* **Date/Hour**: Date and hour of creationg of the version
* **Comment**: Comment written by the user that describes the changes done in the new version

> This is how Artella shows a new version
![{{ project.name }} Version](../img/{{ project.name }}_version.png?style=centerme)

***

## **Version Types**

Artella (and {{ project.name }} Pipeline) works with 2 kind of versions:

* **Working** version
* **Published** version

***

### **Working Versions**
A working version is the version that artists uses while they are working on a non-production ready file. Those versions:

* Can contain any kind of data
* Are not ready for production (they need to be published for that)
* The artist have a complete freedom to create/remove working version of files


### **Published Versions**
A published version is a version that is ready for production. Those versions:

* All the data inside those file have been validated properly by {{ project.name }} Tools (specifically {{ project.name }} Publisher)
* Are ready for production
* The management of those versions can only be handle by **Leads** or **TDs**

***

## **Creating New Versions**

To create new versions you need to use <a href="https://tpoveda.github.io/{{ project.name }}/{{ project.name }}pipeline/{{ project.name }}tools/pipelinizer/tool/" target="_blank" rel="noopener">{{ project.name }} Pipeline</a> tool

> Button to Create Working Versions in {{ project.name }} Pipelinizer
![{{ project.name }} Working Button](../img/{{ project.name }}_publish_working_btn.png?style=centerme)

For more info about how to create new versions follow this link: **<a href="https://tpoveda.github.io/{{ project.name }}/{{ project.name }}pipeline/faq/workingversion/" target="_blank" rel="noopener">How to create new versions of an asset?</a>**

***


## **Publishing New Versions**

To publsh new versions you need to use <a href="https://tpoveda.github.io/{{ project.name }}/{{ project.name }}pipeline/{{ project.name }}tools/pipelinizer/tool/" target="_blank" rel="noopener">{{ project.name }} Pipeline</a> tool

> Button to Publish Version in {{ project.name }} Pipelinizer
![{{ project.name }} Working Button](../img/{{ project.name }}_publish_working_btn_1.png?style=centerme)

When publishing assets, depending of tye type of asset your're working on you need to follow different steps:

**<a href="https://tpoveda.github.io/{{ project.name }}/{{ project.name }}pipeline/faq/publish/shading" target="_blank" rel="noopener">How to publish shading files?</a>**

**<a href="https://tpoveda.github.io/{{ project.name }}/{{ project.name }}pipeline/faq/publish/textures" target="_blank" rel="noopener">How to publish texture files?</a>**

**<a href="https://tpoveda.github.io/{{ project.name }}/{{ project.name }}pipeline/faq/publish/model" target="_blank" rel="noopener">How to publish model/rig files?</a>**
