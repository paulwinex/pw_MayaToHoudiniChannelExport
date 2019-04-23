import maya.cmds as cmds

fpsList = {'game':15,
           'film': 24,
           'pal': 25,
           'ntsc': 30,
           'show': 48,
           'palf': 50,
           'ntscf': 60}


def readChannelsData(channels, frameRange, progress, options):

    channelsValue = {x:[] for x in channels}
    for i in range(frameRange[0], frameRange[1]+1):
        cmds.currentTime(i)
        prcnt = (i * 100.0) / (frameRange[1]-frameRange[0]+1)
        progress.setValue(int(prcnt))
        for ch in channels:
            value = cmds.getAttr(ch)
            if ch.split('.')[-1] in ['tx','ty','tz']:
                value = value * options['scale']
            channelsValue[ch].append(value)
    return channelsValue


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

def export(channels, outFile, frange, progres, options):
    dataChannels = readChannelsData(channels, frange, progres, options)
    text = exporter(dataChannels, frange)
    with open(outFile,'w') as f:
        f.write(text)

