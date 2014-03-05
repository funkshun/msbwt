'''
Created on Nov 1, 2013

@author: holtjma
'''

import argparse as ap
import logging
import os
import sys

import MSBWTGen
import MultiStringBWT
import util

DESC = "A multi-string BWT package for DNA and RNA."
VERSION = '0.1.0'
PKG_VERSION = '0.1.0'

def initLogger():
    '''
    This code taken from Shunping's Lapels for initializing a logger
    '''
    global logger
    logger = logging.getLogger('root')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def mainRun():
    #start up the logger
    initLogger()
    
    #attempt to parse the arguments
    p = ap.ArgumentParser(description=DESC, formatter_class=ap.RawTextHelpFormatter)
    
    #version data
    p.add_argument('-V', '--version', action='version', version='%(prog)s' + \
                   ' %s in MSBWT %s' % (VERSION, PKG_VERSION))
    
    sp = p.add_subparsers(dest='subparserID')
    p2 = sp.add_parser('cffq', help='create a MSBWT from FASTQ files (pp + cfpp)')
    p2.add_argument('-p', metavar='numProcesses', dest='numProcesses', type=int, default=1, help='number of processes to run (default: 1)')
    p2.add_argument('-u', '--uniform', dest='areUniform', action='store_true', help='the input sequences have uniform length (faster)', default=False)
    p2.add_argument('outBwtDir', type=util.newDirectory, help='the output MSBWT directory')
    p2.add_argument('inputFastqs', nargs='+', type=util.readableFastaFile, help='the input FASTQ files')
    
    p7 = sp.add_parser('pp', help='pre-process FASTQ files before BWT creation')
    p7.add_argument('-u', '--uniform', dest='areUniform', action='store_true', help='the input sequences have uniform length (faster)', default=False)
    p7.add_argument('outBwtDir', type=util.newDirectory, help='the output MSBWT directory')
    p7.add_argument('inputFastqs', nargs='+', type=util.readableFastaFile, help='the input FASTQ files')
    
    p3 = sp.add_parser('cfpp', help='create a MSBWT from pre-processed sequences and offsets')
    p3.add_argument('-p', metavar='numProcesses', dest='numProcesses', type=int, default=1, help='number of processes to run (default: 1)')
    p3.add_argument('-u', '--uniform', dest='areUniform', action='store_true', help='the input sequences have uniform length (faster)', default=False)
    p3.add_argument('bwtDir', type=util.existingDirectory, help='the MSBWT directory to process')
    
    p4 = sp.add_parser('merge', help='merge many MSBWTs into a single MSBWT')
    p4.add_argument('-p', metavar='numProcesses', dest='numProcesses', type=int, default=1, help='number of processes to run (default: 1)')
    p4.add_argument('outBwtDir', type=util.newDirectory, help='the output MSBWT directory')
    p4.add_argument('inputBwtDirs', nargs='+', type=util.existingDirectory, help='input BWT directories to merge')
    
    p5 = sp.add_parser('query', help='search for a sequence in an MSBWT, prints sequence and seqID')
    p5.add_argument('inputBwtDir', type=util.existingDirectory, help='the BWT to query')
    p5.add_argument('kmer', type=util.validKmer, help='the input k-mer to search for')
    p5.add_argument('-d', '--dump-seqs', dest='dumpSeqs', action='store_true', help='print all sequences with the given kmer (default=False)', default=False)
    
    p6 = sp.add_parser('massquery', help='search for many sequences in an MSBWT')
    p6.add_argument('inputBwtDir', type=util.existingDirectory, help='the BWT to query')
    p6.add_argument('kmerFile', help='a file with one k-mer per line')
    p6.add_argument('outputFile', help='output file with counts per line')
    p6.add_argument('-r', '--rev-comp', dest='reverseComplement', action='store_true', help='also search for each kmer\'s reverse complement', default=False)
    
    p8 = sp.add_parser('compress', help='compress a MSBWT to a smaller storage format')
    p8.add_argument('-p', metavar='numProcesses', dest='numProcesses', type=int, default=1, help='number of processes to run (default: 1)')
    p8.add_argument('srcDir', type=util.existingDirectory, help='the source directory for the BWT to compress')
    p8.add_argument('dstDir', type=util.existingDirectory, help='the destination directory (if same, old is removed)')
    
    #TODO:
    p9 = sp.add_parser('decompress', help='decompress a MSBWT for queries/merging')
    p9.add_argument('-p', metavar='numProcesses', dest='numProcesses', type=int, default=1, help='number of processes to run (default: 1)')
    p9.add_argument('srcDir', type=util.existingDirectory, help='the source directory for the BWT to compress')
    p9.add_argument('dstDir', type=util.newOrExistingDirectory, help='the destination directory (if same, old is removed)')
    
    args = p.parse_args()
    
    if args.subparserID == 'cffq':
        #TODO: memory problems
        #print 'This impl has a memory issue, instead use "pp" and "cfpp".'
        #return
        logger.info('Inputs:\t'+str(args.inputFastqs))
        logger.info('Uniform:\t'+str(args.areUniform))
        #logger.info('Output:\t'+args.outMSBWT)
        logger.info('Output:\t'+args.outBwtDir)
        logger.info('Processes:\t'+str(args.numProcesses))
        print
        #MultiStringBWT.createMSBWTFromFastq(args.inputFastqs, args.outMSBWT, args.numProcesses, logger)
        MultiStringBWT.createMSBWTFromFastq(args.inputFastqs, args.outBwtDir, args.numProcesses, args.areUniform, logger)
        
    elif args.subparserID == 'pp':
        logger.info('Inputs:\t'+str(args.inputFastqs))
        logger.info('Uniform:\t'+str(args.areUniform))
        #logger.info('Sequences:\t'+str(args.outSeqPrefix))
        #logger.info('Offsets:\t'+str(args.outOffsetFN))
        #logger.info('About:\t'+str(args.outAboutFN))
        logger.info('Output:\t'+args.outBwtDir)
        print
        seqFN = args.outBwtDir+'/seqs.npy'
        offsetFN = args.outBwtDir+'/offsets.npy'
        aboutFN = args.outBwtDir+'/about.npy'
        MultiStringBWT.preprocessFastqs(args.inputFastqs, seqFN, offsetFN, aboutFN, args.areUniform, logger)
        
    elif args.subparserID == 'cfpp':
        #logger.info('Sequences:\t'+args.inputSeqFilePrefix)
        #logger.info('Offsets:\t'+args.inputOffsetFN)
        logger.info('BWT:\t'+args.bwtDir)
        logger.info('Uniform:\t'+str(args.areUniform))
        #logger.info('Output:\t'+args.outMSBWT)
        logger.info('Processes:\t'+str(args.numProcesses))
        print
        seqFN = args.bwtDir+'/seqs.npy'
        offsetFN = args.bwtDir+'/offsets.npy'
        bwtFN = args.bwtDir+'/msbwt.npy'
        MSBWTGen.createFromSeqs(seqFN, offsetFN, bwtFN, args.numProcesses, args.areUniform, logger)
    
    elif args.subparserID == 'compress':
        #TODO: work this into the new directory format
        logger.info('Src:'+args.srcDir)
        logger.info('Dst:'+args.dstDir)
        #logger.info('BWT Directory: '+args.bwtDir)
        print
        MSBWTGen.compressBWT(args.srcDir+'/msbwt.npy', args.dstDir+'/comp_msbwt.npy', args.numProcesses, logger)
        
        #TODO: add this line, but be careful for now that we don't accidentally break something
        #os.remove(args.bwtDir+'/msbwt.npy')
    elif args.subparserID == 'decompress':
        logger.info('Src Directory: '+args.srcDir)
        logger.info('Dst Directory: '+args.dstDir)
        logger.info('Processes: '+str(args.numProcesses))
        print
        MSBWTGen.decompressBWT(args.srcDir, args.dstDir, args.numProcesses, logger)
        #TODO: remove if srcdir and dstdir are the same
        
        
    elif args.subparserID == 'merge':
        #logger.info('Inputs:\t'+args.inputBwtFN1)
        #logger.info('\t\t'+args.inputBwtFN2)
        logger.info('Inputs:\t'+str(args.inputBwtDirs))
        logger.info('Output:\t'+args.outBwtDir)
        logger.info('Processes:\t'+str(args.numProcesses))
        print
        
        #bwtFNs = [None]*len(args.inputBwtDirs)
        #for x, dirName in enumerate(args.inputBwtDirs):
        #    bwtFNs[x] = dirName+'/msbwt.npy'
        
        #MSBWTGen.mergeNewMSBWT(args.outMSBWT, args.inputBwtFN1, args.inputBwtFN2, args.numProcesses, logger)
        MSBWTGen.mergeNewMSBWT(args.outBwtDir, args.inputBwtDirs, args.numProcesses, logger)
    
    elif args.subparserID == 'query':
        #this is the easiest thing we can do, don't dump the standard info, just do it
        msbwt = MultiStringBWT.loadBWT(args.inputBwtDir, logger)
        
        #always print how many are found, users can parse it out if they want
        r = msbwt.findIndicesOfStr(args.kmer)
        print r[1]-r[0]
        
        #dump the seqs if request
        if args.dumpSeqs:
            for x in xrange(r[0], r[1]):
                dInd = msbwt.getSequenceDollarID(x)
                print msbwt.recoverString(dInd)[1:]+','+str(dInd)
    
    elif args.subparserID == 'massquery':
        logger.info('Input:\t'+str(args.inputBwtDir))
        logger.info('Queries:\t'+str(args.kmerFile))
        logger.info('Output:\t'+args.outputFile)
        logger.info('Rev-comp:\t'+str(args.reverseComplement))
        print
        #msbwt = MultiStringBWT.MultiStringBWT()
        #msbwt.loadMsbwt(args.inputBwtDir, False, logger)
        msbwt = MultiStringBWT.loadBWT(args.inputBwtDir, logger)
        
        output = open(args.outputFile, 'w+')
        output.write('k-mer,counts')
        if args.reverseComplement:
            output.write(',revCompCounts\n')
        else:
            output.write('\n')
        
        logger.info('Beginning queries...')
        for line in open(args.kmerFile, 'r'):
            kmer = line.strip('\n')
            c = msbwt.countOccurrencesOfSeq(kmer)
            if args.reverseComplement:
                rc = msbwt.countOccurrencesOfSeq(MultiStringBWT.reverseComplement(kmer))
                output.write(kmer+','+str(c)+','+str(rc)+'\n')
            else:
                output.write(kmer+','+str(c)+'\n')
        logger.info('Queries complete.')
        
    else:
        print args.subparserID+" is currently not implemented, please wait for a future release."

if __name__ == '__main__':
    mainRun()