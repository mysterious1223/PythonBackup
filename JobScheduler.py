#will run hold the job object and run it on a scheduled basis
from BackupJob import BackupJob
from Logger import Logger
import sys
import os
from datetime import datetime
import time

Source = ""

Dest = ""

#the false helps determin if it was ran or not
dict = [['Friday',22,False]]
timeout = 5
#if source is disk we set last param to true
k = BackupJob (dict, Source, Dest, True)
#k.updateBackupfolderName ()
#k.copySourceToDestination ()


logg = Logger (os.path.abspath(os.getcwd()), "systemlog.log")


while True:

    time.sleep (timeout)

    #if source is disk
    statusOK = k.runBackupProcess(datetime.today(), logg)

    if not statusOK:
        if logg != None:
            logg.writeLogEntry ("[!] Job Failed")
        print ("[!] Job Failed")
        break


#todo 20200430!
# add ability to maintain N back ups and delete others. [x]
# clean up the job scheduler []
# remove old folders [x]
# check space every so often []
# if a person manually removes logs or backups program should adjust []
#investigate why superdrive is out of space [x]
# add logging so we can see the output more easily [x]
#instead of [+] use [date]
#Same line out put. We can use this [x]
#while True:
    #print(6, end="\r", flush=True)

# A queue system if a backup takes to long we can create a queue with a list of jobs
# exclude hidden folders. Create a test script to experiments - the array returned from callback willbe the file to exclude [x]
# Use a text file config to list out scheduled tasks
# duration len

