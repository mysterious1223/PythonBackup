import time
import shutil
import errno
import os
Source = "/mnt/ZSFSSD1/Programming Projects/Current Working Projects/py/BackupScriptPY/test/Tobackup"
Dest = "/mnt/ZSFSSD1/Programming Projects/Current Working Projects/py/BackupScriptPY/test/"
backupfoldername = "TestBackup"




def _logpath(path, names):

    filesToIgnore = []

    #self.printLine ("Started Copying!", False)
    print(path)
    #print (str(names))

    for n in names:
        print(path + "/" + n)
        fullFileName = os.path.join(os.path.normpath(path), n)
        #fullFileName = os.path.join(os.path.normpath(path), n)
        
        #prints the folders. We need to check if it has a pattern .*
        folder = os.path.basename(os.path.normpath(path))
        #WORKS
        if folder.startswith ("."):
            print ("Hidden "+os.path.basename(os.path.normpath(path)))
            filesToIgnore.append (n)
         




    #logging.info('Working in %s' % path)
    return filesToIgnore



def copySourceToDestination():
    try:
        shutil.copytree(Source, Dest + backupfoldername, ignore=_logpath)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(Source, Dest)

        else:
            print('!!! Directory not copied. Error: %s' % e)
            return False
    print("Done!")
    return True

copySourceToDestination()


#import os

#srcDir = os.getcwd()

#dirName = 'target_directory'

#dstDir = os.path.abspath(dirName)

# def ignore_list(path, files):

#filesToIgnore = []

# for fileName in files:

 #   fullFileName = os.path.join(os.path.normpath(path), fileName)

  #  if (not os.path.isdir(fullFileName)
   #     and not fileName.endswith('pyc')
    #    and not fileName.endswith('ui')
    #   and not fileName.endswith('txt')
    #  and not fileName == '__main__.py'
    # and not fileName == 'dcpp.bat'):

    # filesToIgnore.append(fileName)

# return filesToIgnore

# start of script

#shutil.copytree(srcDir, dstDir, ignore=ignore_list)
