import maya.cmds as cmds
import json

fpsList = {'game':15,
           'film': 24,
           'pal': 25,
           'ntsc': 30,
           'show': 48,
           'palf': 50,
           'ntscf': 60}


def readChannelsData(channels, frameRange, options, progress=None):

    channelsValue = {x:[] for x in channels}
    for i in range(frameRange[0], frameRange[1]+1):
        cmds.currentTime(i)
        prcnt = (i * 100.0) / (frameRange[1]-frameRange[0]+1)
        if progress:
            progress.setValue(int(prcnt))
        for ch in channels:
            value = cmds.getAttr(ch)
            if ch.split('.')[-1] in ['tx','ty','tz']:
                value = value * options.get('scale', 1)
            channelsValue[ch].append(value)
    return channelsValue

def getAutoRange():
    allCurves = cmds.ls(type='animCurve')
    if allCurves:
        maxTime = max([ x for x in [ max(cmds.keyframe(crv,q=1, tc=1)) for crv in allCurves ] ])
        minTime = min([ x for x in [ min(cmds.keyframe(crv,q=1, tc=1)) for crv in allCurves ] ])
        result = [int(minTime), int(maxTime)]
        return result
    else:
        st = int(cmds.playbackOptions(q=1, minTime=1))
        en = int(cmds.playbackOptions(q=1, maxTime=1))
        return [int(st), int(en)]

def exporter(data, frameRange):
    fps = fpsList[cmds.currentUnit(q=1, t=1)]
    startFrame = frameRange[0]-1
    length = frameRange[1]-frameRange[0] + 1
    count = len(data)
    text = '''\
{
   rate = %s
   start = %s
   tracklength = %s
   tracks = %s
''' % (fps, startFrame, length, count)
    for ch, values in data.items():
        chanText = '''\
    {
        name = %s
        data = %s
    }\n''' % (ch.replace('.',':'), ' '.join([str(x) for x in values]))
        text += chanText
    text += '}'
    return text

def export(channels, outFile, frange=None, options=None, progres=None):
    frange = frange or getAutoRange()
    options = options or {}
    dataChannels = readChannelsData(channels, frange, options, progres)
    text = exporter(dataChannels, frange)
    with open(outFile,'w') as f:
        f.write(text)
    return outFile

def export_from_preset(preset, outFile=None, frame_range=None):
    preset_data = json.load(open(preset))
    return export(preset_data['channels'], outFile or preset_data['path'],
                  frame_range or ([preset_data['start'], preset_data['end']] if not preset_data.get('auto') else None),
                  preset_data)
