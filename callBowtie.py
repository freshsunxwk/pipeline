#!/usr/bin/python
#given a fastq location, create a .sh script to run mapping through generation of sorted bam


#===================================================================
#========================MODULES AND DEPENDENCIES===================
#===================================================================

import string

import random


#===================================================================
#==========================GLOBAL PARAMETERS========================
#===================================================================

#command arguments
bowtieString = '/usr/local/bowtie-0.12.8/bowtie'
samtoolsString = 'samtools'
#tempParentFolder = '/ifs/labs/bradner/BOWTIE_TEMP/'

tempParentFolder = '/mnt/d0-0/share/bradnerlab/projects/anna/BOWTIE_TEMP/'

#===================================================================
#=============================FUNCTIONS=============================
#===================================================================


def stripExtension(fileName):

    '''
    tries to strip the extension of a filename
    can strip .tar.gz, .txt, .fastq,.gz,.zip
    '''
    extensionList = ['.tar.gz','.txt','.fastq','.fasta','.gz','.zip']

    for extension in extensionList:
        fileName = fileName.replace(extension,'')

    return fileName
    

#print stripExtension('CGATGT-s_8_1_sequence.txt')


def makeFileNameDict(fastqFile,genome,tempString,tempParentFolder,finalFolder,uniqueID=''):

    '''
    creates a dictionary w/ all filenames
    '''


    fileNameDict = {}

    fileNameDict['fastqFile'] = fastqFile

    if uniqueID == '':
        fastqName = fastqFile.split('/')[-1]
        fastqName = stripExtension(fastqName)

    else:
        fastqName = uniqueID

    fileNameDict['fastqName'] = fastqName

    #make the temp Folder
    tempFolder = tempParentFolder + 'bwt_' + fastqName + tempString + '/'    
    fileNameDict['tempFolder'] = tempFolder

    tempFastqFile = tempFolder + fastqName + '.rawFastq'
    fileNameDict['tempFastqFile'] = tempFastqFile

    tempSamFile = tempFolder + fastqName + '.sam'
    fileNameDict['tempSamFile'] = tempSamFile

    tempBamFile = tempFolder + fastqName + '.bam'
    fileNameDict['tempBamFile'] = tempBamFile

    tempSortedBamFile = tempFolder + fastqName + '.%s.bwt.sorted' % (genome)
    fileNameDict['tempSortedBamFile'] = tempSortedBamFile

    groupHeader = tempFolder + fastqName + '.%s.bwt' % (genome)
    fileNameDict['groupHeader'] = groupHeader

    fileNameDict['finalFolder'] = finalFolder
    return fileNameDict




def extractFastqCmd(fileNameDict):

    '''
    creates a command to extract/copy the fastq to a temp location
    '''
    
    fastqFile = fileNameDict['fastqFile']
    tempFastqFile = fileNameDict['tempFastqFile']

    #there are 3 possibilities, a gzipped, tarballed, or naked fastq
    if string.lower(fastqFile).count('tar') == 1:
        cmd = "tar --strip-components 5 --to-stdout -xzvf %s > %s" % (fastqFile,tempFastqFile)
    elif string.lower(fastqFile.split('.')[-1]) == 'gz':
        print('ay')
        cmd = 'cp %s %s.gz\n' % (fastqFile,tempFastqFile)
        cmd+= 'gunzip %s.gz' % (tempFastqFile)
    else:
        cmd = 'cp %s %s' % (fastqFile,tempFastqFile)

    return cmd
    

def bowtieCmd(bowtieString,seedLength,bowtieIndex,fileNameDict):

    '''
    creates the bowtie command call
    '''

    
    #calling bowtie
    tempFastqFile = fileNameDict['tempFastqFile']
    tempSamFile = fileNameDict['tempSamFile']
    
    cmd = "%s -e 70 -k 1 -m1 -n 2 -p 4 -l %s --best --sam %s %s > %s" % (bowtieString,seedLength,bowtieIndex,tempFastqFile,tempSamFile)
    return cmd


def removeTempFastqCmd(fileNameDict):

    '''
    removes the temp fastq
    '''
    tempFastqFile = fileNameDict['tempFastqFile']    
    cmd = '/bin/rm -f %s' % (tempFastqFile)
    return cmd

#generate a bam file

def generateTempBamCmd(samtoolsString,fileNameDict):

    '''
    uses samtools to conver the sam to a bam
    '''
    tempSamFile = fileNameDict['tempSamFile']
    tempBamFile = fileNameDict['tempBamFile']

    cmd = "%s view -bS '%s' > '%s'" % (samtoolsString,tempSamFile,tempBamFile)
    
    return cmd

#sort
def sortBamCmd(samtoolsString,fileNameDict):

    '''
    uses smatools to sort the bam
    '''
    tempBamFile = fileNameDict['tempBamFile']
    tempSortedBamFile = fileNameDict['tempSortedBamFile']

    cmd = "%s sort '%s' '%s'" % (samtoolsString,tempBamFile,tempSortedBamFile)
    return cmd


#index
def indexBamCmd(samtoolsString,fileNameDict):

    '''
    uses samtools to index the bam
    '''

    tempSortedBamFile=fileNameDict['tempSortedBamFile']
    cmd = "%s index '%s'" % (samtoolsString,tempSortedBamFile)

    return cmd

def rmSamCmd(fileNameDict):

    '''
    remove the sam
    '''
    tempSamFile = fileNameDict['tempSamFile']
    cmd = "/bin/rm -f '%s'" % (tempSamFile)
    return cmd

def mvBamCmd(fileNameDict):

    '''
    moves and renames the bam w/o the temp string
    '''
    groupHeader = fileNameDict['groupHeader']
    finalFolder = fileNameDict['finalFolder']

    cmd = "mv '%s*' '%s'" % (groupHeader,finalFolder)
    
    return cmd

def rmTempFiles(fileNameDict):

    '''
    removes everything left in the temp folder
    '''
    groupHeader = fileNameDict['groupHeader']
    cmd = "/bin/rm -f '%s'*" % (groupHeader)
    return cmd

#===================================================================
#=============================MAIN==================================
#===================================================================

def main():

    '''
    main run function
    '''

    from optparse import OptionParser

    usage = "usage: %prog [options] -f [FASTQFILE] -l [SEEDLENGTH] -g [GENOME] -u [UNIQUEID] -o [OUTPUTFOLDER]"
    parser = OptionParser(usage = usage)
    #required flags
    parser.add_option("-f","--fastq", dest="fastq",nargs = 1, default=None,
                      help = "Enter the full path of a fastq file to be mapped")
    parser.add_option("-l","--length", dest="seedLength",nargs = 1, default=None,
                      help = "Enter an integer seed length")
    parser.add_option("-g","--genome",dest="genome",nargs =1, default = None,
                      help = "specify a genome, options are hg18 or mm9 right now")
    parser.add_option("-u","--unique",dest="unique",nargs =1, default = None,
                      help = "specify a uniqueID")
    parser.add_option("-o","--output",dest="output",nargs =1, default = None,
                      help = "Specify an output folder")
    

    (options,args) = parser.parse_args()

    if not options.fastq or not options.seedLength or not options.genome or not options.unique or not options.output:
        parser.print_help()
        exit()


    #retrive the arguments
    fastqFile = options.fastq
    seedLength = options.seedLength
    genome = options.genome
    uniqueID = options.unique
    outputFolder = options.output

    #get the bowtie index
    bowtieDict = {

        'hg18':'/mnt/d0-0/share/bradnerlab/genomes/human_gp_mar_06_no_random/bowtie/hg18'
        }

    bowtieIndex = bowtieDict[string.lower(genome)]

    #get the temp string
    tempString = '_%s' % str(random.randint(1,10000))
    
    fileNameDict = makeFileNameDict(fastqFile,genome,tempString,tempParentFolder,outputFolder,uniqueID)


    #open the bashfile to write to
    bashFileName = "%s%s_bwt.sh" % (outputFolder,uniqueID)
    bashFile = open(bashFileName,'w')

    #make temp directory
    cmd = 'mkdir %s' % (fileNameDict['tempFolder'])
    bashFile.write(cmd+'\n')

    #extract fastq
    cmd = extractFastqCmd(fileNameDict)
    bashFile.write(cmd+'\n')

    #call bowtie
    cmd = bowtieCmd(bowtieString,seedLength,bowtieIndex,fileNameDict)
    bashFile.write(cmd+'\n')

    #remove temp fastq
    cmd = removeTempFastqCmd(fileNameDict)
    bashFile.write(cmd+'\n')

    #generate a bam
    cmd = generateTempBamCmd(samtoolsString,fileNameDict)
    bashFile.write(cmd+'\n')

    #sort the bam
    cmd = sortBamCmd(samtoolsString,fileNameDict)
    bashFile.write(cmd+'\n')

    #index
    cmd = indexBamCmd(samtoolsString,fileNameDict)
    bashFile.write(cmd+'\n')

    #remove sam
    cmd = rmSamCmd(fileNameDict)
    bashFile.write(cmd+'\n')

    #mv bams
    cmd = mvBamCmd(fileNameDict)
    bashFile.write(cmd+'\n')

    #cleanup
    cmd = rmTempFiles(fileNameDict)
    bashFile.write(cmd+'\n')


    bashFile.close()
    
if __name__ == "__main__":
    main()

