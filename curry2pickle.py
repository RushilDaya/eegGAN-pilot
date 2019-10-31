import struct as struct
import numpy as np
import matplotlib.pyplot as plt
import pickle


def curry2pickle(fileGroupName,save=False,writePath=None):

    fileNameCeo = fileGroupName + '.ceo'
    fileNameDap = fileGroupName + '.dap'
    fileNameRs3 = fileGroupName + '.rs3'
    fileNameDat = fileGroupName + '.dat'
    
    # read the key tokens from the .dap file
    ALL_TOKENS = ['NumSamples','NumChannels','NumTrials',
                  'SampleFreqHz','TriggerOffsetUsec','DataFormat',
                  'DataSampOrder']

    dapFile = open(fileNameDap,'r')
    dap = dapFile.read()
    dapFile.close()

    dapMap = {}
    dapList = dap.split('\n')
    for row in dapList:
        elements = row.split('=')
        if len(elements) == 2:
            possibleKey = elements[0].strip()
            if possibleKey in ALL_TOKENS:
                dapMap[possibleKey] = elements[1].strip()
    
    if len(dapMap) != len(ALL_TOKENS):
        raise Exception()

    numSamples = int(dapMap['NumSamples'])
    numChannels = int(dapMap['NumChannels'])
    numTrials = int(dapMap['NumTrials'])
    sampleFreq = int(dapMap['SampleFreqHz'])
    TriggerOffsetUsec = int(dapMap['TriggerOffsetUsec'])
    DataFormat = dapMap['DataFormat']
    DataSampleOrder = dapMap['DataSampOrder']

    # read in the channel names from the .rs3 file
    rs3File = open(fileNameRs3,'r')
    rs3 = rs3File.read()
    rs3File.close()

    subset = rs3.split('LABELS START_LIST')[1]
    subset = subset.split('LABELS END_LIST')[0]
    subset = subset.split('\n')
    subset = subset[1:-1]
    channel_names = subset

    # read the data from the .dat file
    datFile = open(fileNameDat,'rb')
    unpacked = struct.unpack('f'*numChannels*numSamples*numTrials, datFile.read(4*numChannels*numSamples*numTrials))
    datFile.close()

    dataArray = np.array(unpacked).reshape((numSamples*numTrials,numChannels))

    if save:
        saveObj = {
            'data':dataArray,
            'channel_names':channel_names,
            'sample_freq':sampleFreq
        }
        outFile = open(writePath,'wb')
        pickle.dump(saveObj,outFile)
        outFile.close()

    return True

if __name__ == '__main__':
    exitCode = curry2pickle('./rawData/subject_1/onoff')
    print(exitCode)