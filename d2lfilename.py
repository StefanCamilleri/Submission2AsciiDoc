from os import listdir
from os.path import isfile, join
import re

def getstudent(entryName, classList):
    ''' Determines the student that a file or folder belongs to.
        e.g 1691733-13758497 - Bob Smith- Sep 11, 2017 541 PM - Newspaper
    '''
    #for studentNumber, studentName in classList.iteritems():
    for studentNumber, studentName in classList.items():
        # Also find hyphens in case one name is a substring of another.
        nameIndex = entryName.find(" - " + studentName + "- ")
        if nameIndex >= 0:
            return studentNumber, studentName

    return None, None


def getoriginalname(entryName):
    ''' Determines the original file or folder name
        e.g. 1691733-13758497 - Bob Smith- Sep 11, 2017 541 PM - Newspaper
    '''
    #e.g. - Sep 18, 2017 238 PM -
    date = "- \S{3} \d{1,2}, \d{4} \d{3,4} \S{2} - "

    #https://pymotw.com/2/re/
    for match in re.finditer(date, entryName):
        return entryName[match.end():]

''' Determine the name of the dropbox from the folder containing
    the submissions
'''
def getoriginaldropboxname(folderName):
    #e.g. 4.8 Algorithm - Finding Duplicates Download Nov 27, 2017 604 PM
    return folderName[:folderName.rfind(" Download")]

''' Returns true if a filename starts with a key '''
'''
def haskey(filename):
    key = "\d{7}-\d{8} - "
    return re.search(key, filename)
'''

def determineClassList(studentEntryPath, classLists):
    for c in classLists:
        studentName, studentNumber = getstudent(studentEntryPath, c)
        if studentName != None:
            return c

def getD2lClassLists(filenames):
    '''
    Creates a list of multiple class lists. Each of which is a dictionary of student names and numbers
    :param filenames: a list of comma-separated files in the format: Firstname Lastname,123456
    :return: a list of dictionaries with student numbers as keys and names as data
    '''

    classLists = []

    for f in filenames:
        classListFile = open(f, "r")
        classList = dict()

        for line in classListFile:
            line=line.strip()
            record = line.split(",")
            classList[record[1]] = record[0]

        classLists += [classList]

    return classLists
