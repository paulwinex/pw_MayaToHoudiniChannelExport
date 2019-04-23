pw_MayaToHoudiniChannelExport
=============================

![alt tag](http://www.paulwinex.ru/wp-content/uploads/2014/07/mthce_image.jpg)

This script is designed to export animation channels from Maya to Houdini CHOP files.  A format that Houdini understands as CHOP channels. You do not require any additional plug-ins or scripts to read the data in Houdini.

Supports any number of attributes from channelBox. You only need to select an attribute and add it to the list

- One file can have any number of channels. Very convenient for transferring character animation or mocap

- Automatic determination of clip length from minimum and maximum values ​​of animation curves

- Saving export settings in Maya scene or to a disk file

- Batch-mode to export several FBX files with animation

### Installation:

Copy the folder to pw_MayaToHoudiniChannelExport  the library for Python-modules. For example at:

         MAYA_INSTALL \ Python \ Lib \ site-packages

or at:

         ~ \ maya \ 2018 \ scripts

Open Script Editor and run the code

<pre><code>import pw_MayaToHoudiniChannelExport
pw_MayaToHoudiniChannelExport.show ()</code></pre>

If your Maya version is lower than 2014, you need to install [PyQt](http://www.paulwinex.ru/installpyqteng/)