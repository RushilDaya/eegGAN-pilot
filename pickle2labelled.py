import json
import pickle
import numpy as np
from scipy.signal import butter,lfilter
import matplotlib.pyplot as plt

def _trimContinguous(A):
    # returns only the first element per contigous batch in a larger list A

    if len(A) == 0:
        return []

    trimedList = [A[0]]
    runningIndex = A[0]
    for idx in range(1,len(A)):
        if A[idx] != A[idx-1]+1:
            trimedList +=[ A[idx] ]
        
    return trimedList

def _getsegments(electrodeChannels, freqMarkers, markerTrialStarts,markerTrialEnds,eventMarkerStarts,eventMarkerEnds):
    # uses the obtained indices to split the dataset for the particular frequency markers considered
    
    allSegments = []

    for freqMarker in freqMarkers:
        trialStart = [item for item in markerTrialStarts if item > freqMarker ][0]
        trialEnd   = [item for item in markerTrialEnds if item > freqMarker ][0]


        filteredEventStarts = [item for item in eventMarkerStarts if (item > trialStart and item < trialEnd )]
        filteredEventEnds = [item for item in eventMarkerEnds if (item > trialStart and item < trialEnd )]

        if len(filteredEventEnds) != len(filteredEventEnds):
            raise Exception

        # we want the segments NOT corresponding to events
        # hence the switch around here
        segmentBeginings = [trialStart]+ filteredEventEnds
        segmentEndings = filteredEventStarts + [trialEnd]

        for idx in range(len(segmentBeginings)):
            begining = segmentBeginings[idx] 
            ending = segmentEndings[idx] 
            segment = electrodeChannels[begining:ending,:]
            allSegments += [segment]

    return allSegments


def pickle2labelled(picklePath, paradigm, reref=True, bandpass=True):
    # segments the raw data into sections labelled segments
    # the segment lengths are not consistent -- each one being as long as possible
    # will rereference to the Pz and Fz means if reref=True
    # will perform bandpass filtering if bandpass=True
    # No electrode selection or resampling

    markerFile = open('markerFile.json','rb')
    markers = json.load(markerFile)
    markerFile.close()

    pickleFile = open(picklePath,'rb')
    dataObj = pickle.load(pickleFile)
    pickleFile.close()

    electrodeList= dataObj['channel_names']
    sampleRate= dataObj['sample_freq']
    markerChannel = dataObj['data'][:,-1]
    electrodeChannels = dataObj['data'][:,:-1]
    
    # first zero mean all the signals
    channelMeans = np.mean(electrodeChannels, axis=0)
    electrodeChannels = electrodeChannels - channelMeans


    if reref:
        references = ['Cz','Fz']
        indices = []
        for ref in references:
            indices += [electrodeList.index(ref)]
        
        referenceSet = electrodeChannels[:,indices]
        refSig = np.mean(referenceSet,axis=1)
        refSig = refSig.reshape(refSig.shape[0],1)
        electrodeChannels = electrodeChannels - refSig

    if bandpass:
        lowCut = 4 # Hz
        highCut = 30 # Hz
        nyquist = 0.5*sampleRate
        lowNorm = lowCut/nyquist
        highNorm = highCut/nyquist
        b, a = butter(1,[lowNorm,highNorm],btype='band')

        for channelIdx in range(electrodeChannels.shape[1]):
            channelData = electrodeChannels[:,channelIdx]
            filtered = lfilter(b,a,channelData) # wtf 
            electrodeChannels[:,channelIdx]=filtered

    # perform the data spliting
    labelledSet = {11:[],13:[],15:[]}

    
    markerLocations11 = [i for i in range(len(markerChannel)) if markerChannel[i]==markers["trialPrior11"]]
    markerLocations13 = [i for i in range(len(markerChannel)) if markerChannel[i]==markers["trialPrior13"]]
    markerLocations15 = [i for i in range(len(markerChannel)) if markerChannel[i]==markers["trialPrior15"]]
    markerLocations11 = _trimContinguous(markerLocations11)
    markerLocations13 = _trimContinguous(markerLocations13)
    markerLocations15 = _trimContinguous(markerLocations15)

    markerTrialStarts =[i for i in range(len(markerChannel)) if markerChannel[i]==markers["trialStart"]]
    markerTrialEnds = [i for i in range(len(markerChannel)) if markerChannel[i]==markers["trialEnd"]]
    markerTrialStarts = _trimContinguous(markerTrialStarts)
    markerTrialEnds = _trimContinguous(markerTrialEnds)

    eventMarkerStarts = [i for i in range(len(markerChannel)) if markerChannel[i]==markers["eventStart"]]
    eventMarkerEnds = [i for i in range(len(markerChannel)) if markerChannel[i]==markers["eventEnd"]]
    eventMarkerStarts = _trimContinguous(eventMarkerStarts) 
    eventMarkerEnds =  _trimContinguous(eventMarkerEnds)

    labelledSet[11]= _getsegments(electrodeChannels, markerLocations11, markerTrialStarts,markerTrialEnds,eventMarkerStarts,eventMarkerEnds)
    labelledSet[13]= _getsegments(electrodeChannels, markerLocations13, markerTrialStarts,markerTrialEnds,eventMarkerStarts,eventMarkerEnds)
    labelledSet[15]= _getsegments(electrodeChannels, markerLocations15, markerTrialStarts,markerTrialEnds,eventMarkerStarts,eventMarkerEnds)
    
    return {
        'data':labelledSet,
        'sampleRate': sampleRate,
        'electrodeLabels': electrodeList
    }    

if __name__ == '__main__':
    exitCode = pickle2labelled('pickleData/subject_1/training.pickle','training')
