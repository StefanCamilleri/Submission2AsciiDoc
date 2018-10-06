from config import CONFIG
import sys
import os
import subprocess
import logging
from d2lfilename import *

'''
Holds the source files submitted by one student. Source files are stored in a dictionary with the relative path to each
used as the key. The path is relative to the root of the submission.
'''
class Submission:
    def __init__(self, studentNumber):
        self.studentNumber = studentNumber
        self.sourceFiles = dict()

    def addSourceFile(self, relativePath, contents):
        if (self.sourceFiles.has_key(relativePath)):
            raise Exception("Duplicate source file found. Manually delete all duplicates before running this script.")

        self.sourceFiles[relativePath] = contents

    def isEmpty(self):
        return self.sourceFiles.items().count() == 0

'''Collects source files in a folder that was extracted from a zip archive'''
'''
def getArchivedSubmission(studentSubmission, projectTitle, submissionEntryPath, fileExtension, language):
    logging.debug('getArchivedSubmission(): projectTitle=%s, submissionEntry=%s, language=%s, fileExtension=%s', projectTitle, submissionEntryPath, language, fileExtension)

    # studentName, studentNumber = getstudent(submissionEntryPath, classList)
    if studentName == None:
        return None
    # print("Processing " + studentName + "...")
    logging.debug('processing %s %s', studentName, studentNumber)

    originalFolderName = getoriginalname(submissionEntryPath)
    logging.debug('originalFolderName=%s', originalFolderName)

    #asciidocSource = getheader(studentName, studentNumber, projectTitle)
    # logging.debug('asciidocSource= %s', asciidocSource)

    # Path is a folder
    if os.path.isdir(submissionEntryPath):
        for dirpath, dirs, files in os.walk(submissionEntryPath):
            # print("dirs=", dirs)
            for file in files:
                if file.endswith(fileExtension):
                    absolutePath = os.path.join(dirpath, file)
                    relativePath = os.path.relpath(absolutePath, submissionEntryPath)
                    studentSubmission[relativePath] = getSourceCode(absolutePath, relativePath, language)

    # Path is a file
    else:
        if submissionEntryPath.endswith(fileExtension):
            # TODO: Deal with unarchived submissions here
            pass

    # Create .adoc file
    adocFileName = studentNumber + ' ' + studentName + ' ' + projectTitle + ".adoc"
    adocPathname = os.path.join(projectTitle, adocFileName)
    #adocFile = open(adocFileName, 'w')
    adocFile = open(adocPathname, 'w')
    adocFile.write(asciidocSource)
    adocFile.close()

    # Create .pdf file
    error = subprocess.call(['asciidoctor-pdf', adocPathname], shell=True)
    if error != 0:
        print("asciidoctor-pdf returned error ", error)
        return

    return studentName
'''


def getSubmission(submission, submissionPath, originalRelativeSourcePath):
    '''Adds one source file to a submission
    submission -- an object representing the entire submission for one student
    submissionPath -- an absolute path to a valid source file
    originalRelativeSourcePath -- a relative path for the purposes of titling the document
    '''
    logging.debug('dropBoxPath=%s, submissionPath=%s', dropBoxPath, submissionPath)

    sourceCodeFile = open(submissionPath, 'r')
    sourceCode = sourceCodeFile.read()
    sourceCodeFile.close()

    submission.sourceFiles[originalRelativeSourcePath] = sourceCode


def getAsciidocSource(studentSubmission, studentName, studentNumber, projectTitle):
    asciidocSource = getheader(studentName, studentNumber, projectTitle)

    for relativePath, sourceFile in studentSubmission:
        asciidocSource += sourceFile

    return asciidocSource

'''Returns the asciidoc source for the header of one students submission'''
def getheader(studentName, studentNumber, projectTitle):
    asciidocSource = (
            ':doctype: book\n\n'
            ':pdf-page-size: letter\n\n'
            ':source-highlighter: coderay\n\n'
            ':notitle:\n\n'
            '= ' + studentName + ' (' + studentNumber + ') ' + projectTitle + '\n\n'
                                                                              '== ' + projectTitle + '\n' + studentName + '\n\n'
    )
    return asciidocSource


''' Returns the asciidoc source for one source code file of a student's submission
    absolutepath The absolute path to the source file
    relativepath The relative path for the purposes of the heading in the asciidoc
    language The language argument for coderay
'''
def getSourceCode(absolutePath, relativeFilePath, language):
    sourceCodeFile = open(absolutePath, 'r')
    sourceCode = sourceCodeFile.read()
    sourceCodeFile.close()

    asciiDocSource = (
            '.' + relativeFilePath + '\n'
                                     '[source,' + language + ']\n----\n' +
            sourceCode +
            '\n----\n'
    )
    return asciiDocSource

'''
if len(sys.argv) != 5:
    print(
        "Usage: python converttoasciidoc.py <class list path> <dropbox path> <language> <file extension>\n" +
        "\t class list path: a path to a CSV file containing student names as seen in D2L in the format Full Name,######\n" +
        "\t dropbox path: a path to a folder containing the extracted contents of a dropbox folder, where archives are extracted to their own folder\n" +
        "\t language: e.g. python, java\n" +
        "\t file extension: the file extension of the source files to include")
    sys.exit()

d2lClassListFileName = sys.argv[1]
logging.debug('d2lclasslistfilename= %s', d2lClassListFileName)

dropBoxPath = sys.argv[2]
logging.debug('dropboxpath= %s', dropBoxPath)

assert os.path.isabs(dropBoxPath)

language = sys.argv[3]
logging.debug('language= %s', language)

extension = sys.argv[4]
logging.debug('extension= %s', extension)
'''

logging.basicConfig(filename='converttoasciidoc.log', filemode='w', level=logging.DEBUG)

dropBoxPath = sys.argv[1]
assert os.path.isabs(dropBoxPath)

assessmentTitle = getoriginaldropboxname(os.path.basename(dropBoxPath))
logging.debug('assessmentTitle= %s', assessmentTitle)

studentEntries = os.listdir(dropBoxPath)

# DEBUG
logging.debug('studententries:')
for studentEntry in studentEntries:
    logging.debug('%s', studentEntry)

# TODO: Detect which class this dropbox is from

classLists = getD2lClassLists(CONFIG['class lists'])
classList = determineClassList(studentEntries[0], classLists)

extensions = CONFIG['extensions']

submissions = dict()
processedStudents = []

# Group the source files by student
for entry in studentEntries:
    submissionPath = os.path.join(dropBoxPath, entry)

    studentNumber, studentName = getstudent(submissionPath, classList)
    if studentNumber == None:
        continue

    if not submissions.has_key(studentNumber):
        submissions[studentNumber] = Submission(studentNumber)

    logging.debug('Processing entry for %s %s', studentName, studentNumber)
    submission = submissions[studentNumber]

    originalRelativePath = getoriginalname(submissionPath)
    logging.debug('entry=%s originalFolderName=%s', entry, originalRelativePath)
    if os.path.isdir(submissionPath):
        for root, dirs, files in os.walk(submissionPath):
            for file in files:
                filename, fileExt = os.path.splitext(file)
                #if file.endswith(extension):
                if fileExt in extensions:
                    absolutePath = os.path.join(root, file)
                    relativePath = os.path.relpath(absolutePath, submissionPath)

                    logging.debug('file=%s relativePath=%s', file, relativePath)
                    getSubmission(submission, absolutePath, relativePath)
    else:
        filename, fileExt = os.path.splitext(submissionPath)
        #if submissionPath.endswith(extension):
        if fileExt in extensions:
            getSubmission(submission, submissionPath, originalRelativePath)

    processedStudents.append(studentNumber)

# Create one PDF for each student
os.mkdir(assessmentTitle)
for studentNumber, submission in submissions.iteritems():
    studentName = classList[studentNumber]
    asciidocSource = (
            ':doctype: book\n\n'
            ':pdf-page-size: letter\n\n'
            ':source-highlighter: coderay\n\n'
            ':notitle:\n\n'
            '= ' + studentName + ' (' + studentNumber + ') ' + '\n\n'
            '== ' + assessmentTitle + '\n' + studentName + '\n\n'
    )

    for relativeFilePath, sourceCode in submission.sourceFiles.iteritems():
        filename, fileExt = os.path.splitext(relativeFilePath)
        if fileExt in extensions:
            language = extensions[fileExt]
        else:
            language = 'plain'

        asciidocSource += (
                '=== ' + relativeFilePath + '\n'
                '[source,' + language + ']\n----\n' + sourceCode +
                '\n----\n'
        )
    # Create .adoc file
    adocFileName = studentName + ' - ' + studentNumber + ' - ' + assessmentTitle + ".adoc"
    adocPathname = os.path.join(assessmentTitle, adocFileName)
    adocFile = open(adocPathname, 'w')
    adocFile.write(asciidocSource)
    adocFile.close()

    # Create .pdf file
    error = subprocess.call(['asciidoctor-pdf', adocPathname], shell=True)
    if error != 0:
        print("asciidoctor-pdf returned error ", error)

print("\nUnprocessed students")
for studentNumber in classList:
    if studentNumber not in classList.keys():
        print(studentNumber, classList[studentNumber])