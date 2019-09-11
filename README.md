pw_MayaToHoudiniChannelExport
=============================

This script is designed to export animation channels from Maya to Houdini CHOP files.
A format that Houdini understands as CHOP channels (*.clip). You do not require any additional plug-ins or scripts to read the data in Houdini.

Supports any number of attributes from channelBox. You only need to select an attribute and add it to the list.

- One file can have any number of channels. Very convenient for transferring character animation or mocap

- Automatic determination of clip length from minimum and maximum values ​​of animation curves

- Saving export settings in Maya scene or to a disk file

- Batch-mode to export several FBX files with animation

### Video Tutorial

https://vimeo.com/101163979

### Installation:

1. Install maya_to_houdini_channel_exporter

Copy the folder maya_to_houdini_channel_exporter to the library for Python-modules. For example at:

    <MAYA_INSTALL>\Python\Lib\site-packages
    # or
    <DOCUMENTS>\maya\scripts

But better wai is cr copy to you custom path and update PYTHONPATH environment.

2. Run

Open Script Editor and run the code

```python
import maya_to_houdini_channel_exporter
maya_to_houdini_channel_exporter.show ()
```


### API

To use exporter without UI use module `channelExporter`

```python
from maya_to_houdini_channel_exporter import channelExporter

channelExporter.export(
    channels=['object1.tx', 'object1.ty', 'object1.tz'],
    outFile='/path/to/file.clip',
    frange=[0, 100],
    options=dict(scale=1)
    )
# using preset
channelExporter.export_from_preset('path/to/preset.ext', outFile='/path/to/file.clip')
```