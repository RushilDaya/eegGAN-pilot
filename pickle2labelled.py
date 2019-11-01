import json
import pickle
import numpy as np
from scipy.signal import butter,lfilter
import matplotlib.pyplot as plt

def _trimContinguous(A):
    # returns only the first element per contigous batch in a larger list A
    
    return A

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

    print(markerLocations11)
    print(markerLocations13)
    print(markerLocations15)

    return True

if __name__ == '__main__':
    exitCode = pickle2labelled('pickleData/subject_1/onoff.pickle','onoff')
    print(exitCode)
