# back up job object
# it will hold our class
import tarfile
import os.path
import sys
import subprocess
import shutil
import errno
import time
from datetime import datetime
import logging
import psutil
from Logger import Logger
# todos
# add file logging (to store outputs)
# add auto run capabilities
# self aware check if diskspace - compared to the file that is about to be copied
# count of remaining files
# remove old back up and keep 2 at a time


class BackupDataObj:
    thisName = ""
    thisPath = ""
    thisSize = 0
    thisFileCount = 0
    createdDateTime = ''

    def __init__(self, name, path, size, filecount, CreatedTime):
        self.thisName = name
        self.thisPath = path
        self.thisSize = size
        self.thisFileCount = filecount
        self.createdDateTime = CreatedTime
        #print (path)

    def generateLogFile(self):
        #print ("[+] generate file")

        self.createdDateTime = str(datetime.today())
        # how to create log?
        f = open(self.thisPath + "/" + self.thisName, 'a')
        f.writelines("name:"+self.thisName+"\n")
        f.writelines("path:"+self.thisPath+"\n")
        f.writelines("size:"+str(self.thisSize)+"\n")
        f.writelines("filecount:"+str(self.thisFileCount)+"\n")
        f.writelines("CreatedDateTime:"+str(self.createdDateTime)+"\n")
        f.close()


class BackupJob:

    SourceIsDisk = False

    currLogger = None
    # hack to fix sameline bug
    sameLineCalled = False
    previousBuffSize = 0
    # number of backups to keep
    MaxBackups = 2

    # keep some space freee
    BackupSizePadding = 50

    listBackups = []

    backupfoldername = ""
    backupSource = ""
    backupDest = ""

    Days = {'Saturday': 5, 'Sunday': 6, 'Monday': 0, 'Tuesday': 1, 'Wednesday': 2,
            'Thursday': 3, 'Friday': 4}

    isRan = False

    DayTimeDataSet = []

    # dict
    def __init__(self, dayTime, source, dest, isDisk):
        # if day is null
        self.SourceIsDisk = isDisk
        self.DayTimeDataSet = dayTime
        self.backupSource = source
        self.backupDest = dest

        if not self.LoadAllPresentBackups():
            self.printLine("!!! No backups present", False)

    def CreateBackupLog(self, name, path, size, filecount):
        # create a log file with path to backup and contents
        backLog = BackupDataObj(name + ".log", path,
                                size, filecount, datetime.today())
        # create a new logfile
        backLog.generateLogFile()

        self.printLine("backup log created", False)

        return backLog

    def LoadBackupLogsIntoList(self, logfile):
        # load logs into our list
        self.printLine("log loaded into list", False)
        f = open(logfile, 'r')
        Lines = f.readlines()

        Name = ""
        Path = ""
        Size = 0
        FileCount = 0
        CreatedTime = ""
        for line in Lines:
            lineComp = line.split(":")
            if lineComp[0] == 'name':
                Name = lineComp[1].rstrip("\r\n")
            if lineComp[0] == 'path':
                Path = lineComp[1].rstrip("\r\n")
            if lineComp[0] == 'size':
                Size = lineComp[1].rstrip("\r\n")
            if lineComp[0] == 'filecount':
                FileCount = lineComp[1].rstrip("\r\n")
            if lineComp[0] == 'CreatedDateTime':
                CreatedTime = lineComp[1] + ":" + \
                    lineComp[2] + ":" + lineComp[3].rstrip("\r\n")

        self.listBackups.append(BackupDataObj(
            Name, Path, Size, FileCount, CreatedTime))

        self.printLine("Record added to our list " + logfile, False)

    def LoadAllPresentBackups(self):
        # init our backup list
        self.printLine("init backup list", False)
        backupsExist = False
        #self.CreateBackupLog('kevin.log', self.backupDest, 555,1234)

        for filename in os.listdir(self.backupDest):
            if os.path.splitext(filename)[1] == ".log":
                self.printLine(filename, False)
                self.LoadBackupLogsIntoList(self.backupDest+"/"+filename)
                backupsExist = True

        return backupsExist

    def _logpath(self, path, names):
        filesToIgnore = []

        #self.printLine ("Started Copying!", False)
        #print(path)
        #print (str(names))

        for n in names:
            self.printLine(path + "/" + n, True)
            #fullFileName = os.path.join(os.path.normpath(path), n)
            #fullFileName = os.path.join(os.path.normpath(path), n)

            # prints the folders. We need to check if it has a pattern .*
            folder = os.path.basename(os.path.normpath(path))
            # WORKS
            if folder.startswith("."):
                #print("Hidden "+os.path.basename(os.path.normpath(path)))
                filesToIgnore.append(n)
        #logging.info('Working in %s' % path)
        return filesToIgnore

    def updateBackupfolderName(self):
        self.backupfoldername = "Backup_"
        self.backupfoldername = self.backupfoldername + \
            time.strftime("%Y%m%d-%H%M%S")
        #print ("New backup name " + self.backupfoldername)

    def copySourceToDestination(self):
        try:
            shutil.copytree(self.backupSource, self.backupDest +
                            self.backupfoldername, ignore=self._logpath)
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(self.backupSource, self.backupDest)

            else:
                self.printLine(
                    '!!! Directory not copied. Error: %s' % e, False)
                return False
        self.printLine("Done!", True)
        return True

    def getAvailableSpaceOfDriveWithPath(self, _path):

        size = psutil.disk_usage(_path)

        return size.free

    def getUsedSpaceOfDriveWithPath(self, _path):

        size = psutil.disk_usage(_path)

        return size.used

    def getSizeofDir(self, _path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size

    def getSizeofFile(self, _path):
        return os.path.getsize(_path)

    def getFileCountInDir(self, _path):
        count = 0
        for f in os.walk(_path):
            #print('Found directory: %s' % dirName)
            count += len(f[2])
        return count

    def checkifEnoughSpace(self, _despath, _srcpath):
        # check if we have enough space in path
        self.printLine("checking space requirements", False)

        sizeFreeOnDrive = self.getAvailableSpaceOfDriveWithPath(_despath)

        # back up source is disk
        if self.SourceIsDisk:
            sizeOfBackStuff = self.getUsedSpaceOfDriveWithPath(_srcpath) * 2
        # back up source is a folder
        else:
            sizeOfBackStuff = self.getSizeofDir(_srcpath) * 2

        self.printLine("Size available in drive : " + str(sizeFreeOnDrive) +
                       ", estimated back up size : " + str(sizeOfBackStuff), False)

        SizeThatWillBeUsed = sizeOfBackStuff + self.BackupSizePadding

        if SizeThatWillBeUsed >= sizeFreeOnDrive:
            if sizeOfBackStuff < sizeFreeOnDrive:

                self.printLine("!!! Padding limit reached!", False)
            return False

        return True

    def removeTheOldestBackup(self, oldestBackup):
        self.printLine("> removing oldest ...", False)

        compressedFileToRemove = oldestBackup.thisName.replace(
            ".log", ".tar.gz")
        logFileToRemove = oldestBackup.thisName

        try:
            os.remove(oldestBackup.thisPath + "/" + compressedFileToRemove)
            os.remove(oldestBackup.thisPath + "/" + logFileToRemove)
            self.listBackups.remove(oldestBackup)
        except:
            self.printLine("!!! error removing backup", False)
            return False

        return True

    def ChecknumberOfBackUps(self):
        # MaxBackups
        # use the backup logs to assist us with this
        # we will need to delete the oldest back up
        # add created date to log history

        self.printLine("Checking if need to delete old backup", False)
        #print ("[+] Checking if need to delete old backup")
        if len(self.listBackups) == 0:
            self.printLine("> No backups to check", False)
            #print ("[>] No backups to check")

        if len(self.listBackups) >= self.MaxBackups:
            self.printLine(
                "> Backups are greater than or equal to "+str(self.MaxBackups), False)
            #print ("[>] Backups are greater than or equal to "+ str(self.MaxBackups))

            oldesttimeDate = None
            oldestBkup = None

            for bkup in self.listBackups:
                #print ("[>] " + bkup.thisName + " Created: " + bkup.createdDateTime)
                self.printLine("> " + bkup.thisName +
                               " Created: " + bkup.createdDateTime, False)
                # we will need to figure out the oldest back up
                timeDate = datetime.strptime(
                    bkup.createdDateTime, '%Y-%m-%d %H:%M:%S.%f')

                # we now have date time so we can filter and remove the backups we dont need
                # do we need to had tar.gz? or replace log with tar.gz
                #print ("[>] " + str(timeDate.hour))

                if oldesttimeDate == None:
                    # we need to initialize
                    oldesttimeDate = timeDate
                    oldestBkup = bkup

                if oldesttimeDate > timeDate:
                    oldesttimeDate = timeDate

                    oldestBkup = bkup

            # we will need to delete all until we have max - 1 left
            #print ("[>] the oldest back up is "+ oldestBkup.thisName + " Created: " + oldestBkup.createdDateTime)
            self.printLine("> the oldest back up is " + oldestBkup.thisName +
                           " Created: " + oldestBkup.createdDateTime, False)
            if self.removeTheOldestBackup(oldestBkup):

                self.printLine(
                    "Back up removed successfully. Rechecking...", False)
                self.printLine("> new backup count " +
                               str(len(self.listBackups)), False)
                self.ChecknumberOfBackUps()
#
        else:

            self.printLine("> " + str(len(self.listBackups)) +
                           " backups found", False)

        return True

    def printLine(self, text, sameline):

        if sameline:

            if self.previousBuffSize > 0:
                print(self.previousBuffSize*' ', end="\r", flush=True)
            print("[" + str(datetime.today()) + "] " +
                  text, end="\r", flush=True)

            self.previousBuffSize = len(text)

            self.sameLineCalled = True

        else:
            if self.sameLineCalled:
                print("\n[" + str(datetime.today()) + "] " + text)
                self.sameLineCalled = False
            else:
                print("[" + str(datetime.today()) + "] " + text)

        if self.currLogger != None:
            self.currLogger.writeLogEntry(text)

    def compressPath(self):
        self.printLine("Starting compression", False)
        #print ("Starting compression")

        # for filename in os.listdir(src):
        #print(os.path.join(src, filename))
        #print (os.path.basename(src) +"/"+ filename)

        with tarfile.open(self.backupDest + self.backupfoldername + ".tar.gz", "w:gz") as tar:
            for filename in os.listdir(self.backupDest + self.backupfoldername):
                #print("["+self.backupDest + self.backupfoldername+"]")
                #print ("/"+ filename)
                self.printLine(self.backupDest +
                               self.backupfoldername + "/" + filename, True)
                #print ()
                try:
                    tar.add(self.backupDest + self.backupfoldername + "/" + filename,
                            arcname=os.path.basename(self.backupfoldername) + "/" + filename)
                except:
                    #print ("[!] error compressing " + self.backupDest + self.backupfoldername +"/"+ filename)
                    self.printLine("!!! error compressing " + self.backupDest +
                                   self.backupfoldername + "/" + filename, False)
                    return ""
            tar.close()

        self.printLine("Done!", True)
        return self.backupDest + self.backupfoldername + ".tar.gz"

    def removeOldBackupFolder(self):

        #print ("[+] Removing old temp backup folder " + self.backupDest + self.backupfoldername)
        self.printLine("Removing old temp backup folder " +
                       self.backupDest + self.backupfoldername, False)
        try:
            shutil.rmtree(self.backupDest + self.backupfoldername)
        except:
            #print ("[!] Failed to remove old back up folder")
            self.printLine("!!! Failed to remove old back up folder", False)
            return False
        return True
    # to run everything

    def CheckandAdjustBackupList(self):
        #self.printLine ("Checking backup list", False)
        if len(self.listBackups) > 0:
            for f in self.listBackups:
                #self.printLine ("Checking " + f.thisName, False)
                if not os.path.exists(f.thisPath + "/" + f.thisName) and os.path.exists(f.thisPath + "/" + f.thisName.replace(".log", ".tar.gz")):
                    os.remove(f.thisPath + "/" +
                              f.thisName.replace(".log", ".tar.gz"))

                    if not os.path.exists(f.thisPath + "/" + f.thisName.replace(".log", ".tar.gz")) and os.path.exists(f.thisPath + "/" + f.thisName):
                        os.remove(f.thisPath + "/" + f.thisName)

                    self.printLine(
                        "Log or compressed file missing removing " + f.thisName, False)
                    # remove from list

                    self.listBackups.remove(f)

                elif not os.path.exists(f.thisPath + "/" + f.thisName) and not os.path.exists(f.thisPath + "/" + f.thisName.replace(".log", ".tar.gz")):
                    self.printLine(
                        "Both Log / compressed file missing removing " + f.thisName, False)
                    # remove from list
                    self.listBackups.remove(f)

            #self.printLine("No backups logged", False)
    def runBackupProcess(self, dateTime, logg):

        self.currLogger = logg
        # 0 mon
        #print (dateTime.weekday())
        # military
        #print (dateTime.hour)
        self.updateBackupfolderName()

        self.CheckandAdjustBackupList()

        for dt in self.DayTimeDataSet:

            if dateTime.weekday() == self.Days[dt[0]] and dateTime.hour == dt[1]:

                if dt[2] == False:
                    dt[2] = True

                    #print ("[+] Checking for issues ...")
                    self.printLine("Checking for issues ...", False)
                    if self.ChecknumberOfBackUps():
                        #print ("[+] Backups are below or equal to " + str (self.MaxBackups))
                        self.printLine(
                            "Backups are below or equal to " + str(self.MaxBackups), False)
                    # else:
                        # a crash for testing
                        # return False

                    # processback up?
                    if not self.checkifEnoughSpace(self.backupDest, self.backupSource):
                        #print ("[!] Failed not enough space, please manually configure space")

                        self.printLine(
                            "!!! Failed not enough space, please manually configure space", False)

                        return False

                    #print ("[+] Backup now processing...")
                    self.printLine("Backup now processing...", False)

                    self.printLine(
                        "source folder has " + str(self.getFileCountInDir(self.backupSource)) + " files", False)
                    #print ("[+] source folder has " + str(self.getFileCountInDir(self.backupSource)) + " files")

                    #print ("[+] Starting copying procedure")
                    self.printLine("Starting copying procedure", False)
                    # run back up stuff
                    if not self.copySourceToDestination():
                        #print ("[!] Failed to copy to destination")
                        self.printLine(
                            "!!! Failed to copy to destination", False)
                        return False

                    pathofcompressedfile = self.compressPath()

                    if len(pathofcompressedfile) < 2:
                        return False

                    #print ("[+] Compression done")
                    self.printLine("Compressing complete!", False)
                    #print ("removing temp directory")

                    #shutil.rmtree(output + backupFoldername)
                    if self.removeOldBackupFolder():
                        #print ("[+] Back up folder removed")
                        self.printLine("Backup folder removed", False)

                    self.printLine("Back up complete for : " +
                                   str(dateTime), False)
                    #print ("[+] Back up complete for : " + str(dateTime))
                    self.listBackups.append(self.CreateBackupLog(self.backupfoldername, self.backupDest, str(
                        self.getSizeofFile(pathofcompressedfile)), str(self.getFileCountInDir(self.backupSource))))
                    #print ("[+] back up log created "+self.backupDest + "/" + self.backupfoldername + ".log")
                    # print ("[+] # of backups "+ str(len(self.listBackups)))
                    self.printLine("back up log created "+self.backupDest +
                                   "/" + self.backupfoldername + ".log", False)
                    self.printLine("# of backups " +
                                   str(len(self.listBackups)), False)
                    # return the next back up
                    #print ("[+] Waiting for next scheduled backup ")
                    self.printLine("Waiting for next scheduled backup", False)

            else:
                # resets because there is another date on list
                dt[2] = False

        return True
