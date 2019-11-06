import pickle 
import math
import numpy as np 
from scipy.signal import resample
import matplotlib.pyplot as plt

# load the data::

ELECTRODE = 'Oz'
SAMPLE_RATE = 256
SUBJECT = 'subject_1'
SECONDS_PER_RECORDING = 1 # whole seconds ensures phase alignment between recordings 
PARADIGMS = ['onoff','training','phase','frequency']
FREQ_OI = 11

def _resample(signal, old, new):

    numSamples = signal.shape[1]
    desiredSamples = math.floor((numSamples*(new/old)))
    resampled = resample(signal,desiredSamples,axis=1)
    return resampled

def _getSegments(original, srOrig,srNew,secondsPR):
    # takes a original segment of unknown length and divides it up into equal length pieces
    
    # first resample:
    resampled = _resample(original,srOrig,srNew)

    # then segment:
    samplesPerSegment = math.floor(srNew*secondsPR)
    samplesAvailable = resampled.shape[1]

    # recurssion candidate
    if samplesAvailable < samplesPerSegment:
        return []
    
    segments = []
    possibleSegments = math.floor(samplesAvailable/samplesPerSegment)
    for idx in range(possibleSegments):
        segments += [resampled[0,idx*samplesPerSegment:(idx+1)*samplesPerSegment]]

    return segments

dataset = []
for paradigm in PARADIGMS:
    dataFile = './labelledData/'+SUBJECT+'/'+paradigm+'.pickle'
    pickleFile = open(dataFile,'rb')
    dataObj = pickle.load(pickleFile)
    pickleFile.close()
    
    # get the electrode index
    electrodesAll = dataObj['electrodeLabels']
    electrodeIndex = electrodesAll.index(ELECTRODE)

    # get original sample rate
    originalSampleRate = dataObj['sampleRate']

    recordings = dataObj['data']
    recordings = recordings[FREQ_OI]
    
    for recording in recordings:
        channelRecording = recording[:,electrodeIndex]
        channelRecording = channelRecording.reshape([1,channelRecording.shape[0]])
        dataset = dataset + _getSegments(channelRecording,originalSampleRate,SAMPLE_RATE,SECONDS_PER_RECORDING)


meanView = dataset[0]*0
for item in dataset:
    meanView +=item
plt.plot(meanView)
plt.show()

saveObj = {
    'metadata':{
        'subject':SUBJECT,
        'sampleRate':SAMPLE_RATE,
        'frequency':FREQ_OI,
        'recordingLength':SECONDS_PER_RECORDING,
        'electrode':ELECTRODE
    },
    'dataset':dataset
}

outFile = open('dataset.pickle','wb')
pickle.dump(saveObj,outFile)
outFile.close()




    



