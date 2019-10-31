from curry2pickle import curry2pickle
import os

RAW_DATA_PATH = '/rawData/'
WRITE_PATH = '/pickleData/'
CWD = os.getcwd()

# takes all the raw data files and converts them to pickle objects

subjects = ['subject_1','subject_2','subject_3','subject_4','subject_5']
paradigms = ['training','onoff','frequency','phase']

for subject in subjects:
    specificWritePath = CWD+WRITE_PATH+'/'+subject+'/'
    if not os.path.isdir(specificWritePath):
        os.mkdir(specificWritePath)
    
    for paradigm in paradigms:
        readPathFull = CWD+RAW_DATA_PATH+'/'+subject+'/'+paradigm
        writePathFull = specificWritePath+paradigm+'.pickle'
        curry2pickle(readPathFull,save=True,writePath=writePathFull)
