# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 17:37:22 2017

@author: Simon
"""

#import wfdb  # this package is used to download the EDFx database
import os
import sleeploader
import csv
import numpy as np
import tools
import re
from tqdm import tqdm
from pyedflib import highlevel
from urllib.request import urlretrieve, urlopen
import xml.etree.ElementTree as ET


datadir='edfx'



def download_edfx(datadir):

    response = urlopen('https://physionet.org/physiobank/database/sleep-edfx/sleep-cassette/')
    html = str(response.read())    
    edfxfiles = re.findall(r'(?<=<a href=")[^"]*', html)[1:]

    print ('Downloading EDFx. This will take some time (~1.8 GB).\nDownloading the files manually might be faster.')
    try:os.mkdir(datadir)
    except Exception as e: print('') if type(e) is FileExistsError else print(e)
    received = 0 
    progressloop  = tqdm(edfxfiles, desc='Downloading')
    for record in progressloop:
        if os.path.isfile(os.path.join(datadir,record)):
            progressloop.set_postfix_str('File {} already exists.'.format(record))
            continue
        urlretrieve('https://physionet.org/physiobank/database/sleep-edfx/sleep-cassette/' + record, os.path.join(datadir, record))
        received += os.path.getsize(os.path.join(datadir, record))
        progressloop.set_postfix_str('{:.0f}/{:.0f}MB'.format(received//1024/1024, 1868))
    
    
    
def convert_hypnograms(datadir, attrib='SleepStage'):
    """
    This function is quite a hack to read the edf hypnogram as a byte array. 
    I found no working reader for the hypnogram edfs.
    """
    print('Converting hypnograms')
    files = [x for x in os.listdir(datadir) if x.endswith('.edf.XML')]
    for file in tqdm(files):
        file = os.path.join(datadir,file)
        
        hypnogram = []

        #print('Reading XML label: {}'.format(file))
        xmltree = ET.parse(file)
        for stage in xmltree.iter(attrib):
            hypnogram.extend(stage.text)

        csv_file = file.replace('.XML','.csv')
        with open(csv_file, "w") as f:
            writer = csv.writer(f, lineterminator='\r')
            writer.writerows(hypnogram)
        #print('Saved: {}'.format(csv_file))
            
    

def truncate_eeg(sleepdataset):
    """
    Loads the previously saved EDFx database and truncates the eeg to remove the excessive non-bed time
    This is a lazy substitute for truncating with the lights-off markers.
    """
    sleep = sleepdataset

    data = sleep.data
    hypno = sleep.hypno
    new_data = []
    new_hypno = []


    for d, h in tqdm(zip(data,hypno), total=len(data)):
        if d.shape[0]%3000!=0: d = d[:len(d)-d.shape[0]%3000]
        d = d.reshape([-1,3000,3])

        #print(d.shape)

        if 9 in h:
            delete = np.where(h==9)[0]
            #print(delete.shape)
            d = np.delete(d, delete, 0)
            #print(d.shape)
            h = np.delete(h, delete, 0)
            #print(h.shape)

        #begin = np.where(h-np.roll(h,1)!=0)[0][0]
        #end = np.where(h-np.roll(h,1)!=0)[0][-1]

        #d = d[begin:end]
        #h = h[begin:end]

        d = d.ravel()
        new_hypno.append(h)
        new_data.append(d*1000000)

    sleep.data = new_data
    sleep.hypno = new_hypno
    sleep.save_object()
            
def prepare(datadir = 'edfx'):
    """
    Download, prepare and save the EDF database
    """
    
    download_edfx(datadir)
    convert_hypnograms(datadir)
    
    sleep = sleeploader.SleepDataset(datadir)
    sleep.load()
    truncate_eeg(sleep)
    return sleep


    
