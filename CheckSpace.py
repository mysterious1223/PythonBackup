
import os
import psutil

#Source = "/mnt/ZSFSSD1/Programming Projects/Current Working Projects/py/BackupScriptPY/test/ToBackup"
Source = "/mnt/ZSFSSD1/"
#Dest = "/mnt/ZSFSSD1/Programming Projects/Current Working Projects/py/BackupScriptPY/test/"
Dest = "/media/mysterious/SuperDrive2/"


def getAvailableSpaceOfDriveWithPath ( _path):
      
        size = psutil.disk_usage (_path)
        
        return size.free
def getUsedSpaceOfDriveWithPath ( _path):
      
        size = psutil.disk_usage (_path)
        
        return size.used
def getDirSizeNew ( dest):
    total_size = 0
     # To get size of current directory
    for path, dirs, files in os.walk(dest):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
                #print ("so far " + entry.path, end = "\r", flush = False)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total


def getSizeofDir (_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

        print ("so far " + str(total_size), end = "\r", flush = True)

    return total_size
def getSizeofFile ( _path):
    return os.path.getsize(_path)


def checkifEnoughSpace( _despath, _srcpath):
        #check if we have enough space in path
        print ("checking space requirements")

        sizeFreeOnDrive = getAvailableSpaceOfDriveWithPath(_despath)
        
        print ("free " + str(sizeFreeOnDrive))

        sizeOfBackStuff = getUsedSpaceOfDriveWithPath (_srcpath)# getSizeofDir(_srcpath)

        print ("backup size " + str(sizeOfBackStuff))
        

        print("Size available in drive : " + str(sizeFreeOnDrive) + ", estimated back up size : " + str(sizeOfBackStuff))

        SizeThatWillBeUsed = sizeOfBackStuff 


        

        if SizeThatWillBeUsed >= sizeFreeOnDrive:
            if sizeOfBackStuff < sizeFreeOnDrive:

                print("!!! Padding limit reached!")
            return False

        return True


print (str(checkifEnoughSpace(Dest, Source)))