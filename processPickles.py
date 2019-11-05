import numpy as np 
import os
import pickle 
from pickle2labelled import pickle2labelled


PICKLE_DATA_PATH = '/pickleData/'
WRITE_PATH = '/labelledData/'
CWD = os.getcwd()

subjects = ['subject_1','subject_2','subject_3','subject_4','subject_5']
paradigms = ['training','onoff','frequency','phase']

for subject in subjects:
    writePathSubject = CWD+WRITE_PATH+subject+'/'
    if not os.path.isdir(writePathSubject):
        os.mkdir(writePathSubject) 
    
    for paradigm in paradigms:
        readPath = CWD + PICKLE_DATA_PATH +subject+'/'+paradigm+'.pickle'
        writePathFull = writePathSubject+paradigm+'.pickle'
        print('working on ....')
        print(readPath)
        print(writePathFull)
        dataObj = pickle2labelled(readPath,paradigm)
        
        outFile = open(writePathFull,'wb')
        pickle.dump(dataObj,outFile)
        outFile.close()