'''
Created on 28 sept. 2014

@author: coissac
'''

import orgasm.samples

from orgasm import getIndex, getSeeds, getAdapters
from orgasm.tango import matchtoseed, cutLowCoverage, cutSNPs,\
    estimateDeadBrancheLength, coverageEstimate, estimateFragmentLength,\
    genesincontig, scaffold, fillGaps, dumpGraph, restoreGraph

from orgasm.assembler import Assembler,tango
import sys


__title__="Build the initial assembling graph"


default_config = {   'minread'       : None,
                     'coverage'      : None,
                     'minratio'      : None,
                     'mincov'        : 1,
                     'minoverlap'    : 50,
                     'smallbranches' : None,
                     'lowcomplexity' : False,
                     'snp'           : False,
                     'assmax'        : 500000,
                     'testrun'       : 15000
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the orgasmi command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='output', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    
    
    parser.add_argument('--minread',          dest='buildgraph:minread', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the minimum count of read to consider [default: <estimated>]')
    
    parser.add_argument('--coverage',         dest='buildgraph:coverage', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the expected sequencing coverage [default: <estimated>]')
    
    parser.add_argument('--minratio',         dest='buildgraph:minratio', 
                                              type=float, action='store', 
                                              default=None, 
                        help='minimum ratio between occurrences of an extension'
                             ' and the occurrences of the most frequent extension '
                             'to keep it. [default: <estimated>]')
    
    parser.add_argument('--mincov',           dest='buildgraph:mincov', 
                                              type=int, 
                                              action='store', 
                                              default=1, 
                        help='minimum occurrences of an extension to '
                             'keep it. [default: %(default)d]')
    
    parser.add_argument('--assmax',           dest='buildgraph:assmax', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='maximum base pair assembled')
    
    parser.add_argument('--minoverlap',       dest='buildgraph:minoverlap', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='minimum length of the overlap between '
                             'the sequence and reads to participate in '
                             'the extension. [default: <estimated>]')
    
    parser.add_argument('--smallbranches',    dest='buildgraph:smallbranches', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='maximum length of the branches to cut during '
                             'the cleaning process [default: <estimated>]')
    
    parser.add_argument('--lowcomplexity',    dest='buildgraph:lowcomplexity', 
                                              action='store_true', 
                                              default=False, 
                        help='Use also low complexity probes')
    
    parser.add_argument('--back',             dest='orgasm:back', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')
    
    parser.add_argument('--snp',              dest='buildgraph:snp', 
                                              action='store_true', 
                                              default=False, 
                        help='activate the SNP clearing mode')
    
    parser.add_argument('--adapt5',           dest ='orgasm:adapt5', 
                                              metavar='adapt5', 
                                              default='adapt5ILLUMINA', 
                                              type=str, 
                                              required=False,
                        help='adapter sequences used to filter reads beginning by such sequences'
                             '; either a fasta file containing '
                             'adapter sequences or internal set of adapter sequences '
                             'among %s' % (str(list(filter(lambda s: s.startswith('adapt5'),dir(orgasm.samples)))),) +' [default: %(default)s]' )

    parser.add_argument('--adapt3',           dest ='orgasm:adapt3', 
                                              metavar='adapt3', 
                                              default='adapt3ILLUMINA', 
                                              type=str, 
                                              required=False,
                        help='adapter sequences used to filter reads ending by such sequences'
                             '; either a fasta file containing '
                             'adapter sequences or internal set of adapter sequences '
                             'among %s' % (str(list(filter(lambda s: s.startswith('adapt3'),dir(orgasm.samples)))),) +' [default: %(default)s]' )

    parser.add_argument('--seeds',            dest ='orgasm:seeds', 
                                              metavar='seeds', 
                                              action='append',
                                              default=[], 
                                              type=str, 
                        help='protein or nucleic seeds; either a fasta file containing '
                        'seed sequences or the name of one of the internal set of seeds '
                        'among %s' % str(list(filter(lambda s: s.startswith('prot') or 
                                                s.startswith('nuc'),dir(orgasm.samples)))))

    parser.add_argument('--kup',              dest='orgasm:kup', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='The word size used to identify the seed reads '
                             '[default: protein=4, DNA=12]')

    parser.add_argument('--identity',         dest='orgasm:identity', 
                                              type=float, 
                                              action='store', 
                                              default=0.5, 
                        help='The fraction of word'
                             '[default: 0.5]')


def estimateMinRead(index,minoverlap,coverage):
    MINREAD=10
    MINREADCOR=3
    MINOVERLAP=50
    minread =  (index.getReadSize() - minoverlap) * coverage / index.getReadSize()  / MINREADCOR
    if minread < MINREAD:
        minoverlap = index.getReadSize() - (MINREAD * MINREADCOR * index.getReadSize() / coverage)
        minread = MINREAD
    if  minoverlap< MINOVERLAP:
        minread =  MINREAD
        minoverlap = MINOVERLAP
    return minread,minoverlap


def run(config):
    
    logger=config['orgasm']['logger']
    progress = config['orgasm']['progress']
    output = config['orgasm']['outputfilename'] 
    lowfilter=not config['buildgraph']['lowcomplexity']
    coverageset=config['buildgraph']['coverage'] is not None
    snp=config['buildgraph']['snp']
    assmax = config['buildgraph']['assmax']*2

    logger.info("Building De Bruijn Graph")


    minoverlap = config['buildgraph']['minoverlap']
    logger.info('Minimum overlap between read: %d' % minoverlap)

    r = getIndex(config)
    adapterSeq3, adapterSeq5 = getAdapters(config)
    ecoverage,x = getSeeds(r,config)   

    logger.info('Coverage estimated from probe matches at : %d' % ecoverage)
    
    # Force the coverage to the specified value
    
    if coverageset:
        coverage = config['buildgraph']['coverage']
        logger.info('Coverage forced by user at : %d' % coverage)
    else:
        coverage = ecoverage
    
    # according to the minread option estimate it from coverage or use the specified value
   
    if config['buildgraph']['minread'] is None:
        minread,minoverlap = estimateMinRead(r,
                                             minoverlap,
                                             coverage)
        logger.info('Minimum read estimated from coverage (%dx)  ar: %d' % (coverage,minread))

    else:
        minread = config['buildgraph']['minread']
        logger.info('Minimum read forced by user at : %d' % minread)
                
    # Convert matches in sedd list    
    s = matchtoseed(x,r)
    
    # Create the assembler object
    asm = Assembler(r)

    ##########################
    #
    # If minread is not specified we initiate the assembling
    # based on the coverage estimated from protein match
    # to obtain a better coverage estimation
    #
    ##########################
    if config['buildgraph']['minread'] is None and not coverageset:

        logger.info('Assembling of %d pb for estimating actual coverage' % config['buildgraph']['testrun'])
        
        # Run the first assembling pass
        a = tango(asm,s,mincov=minread,       # @UnusedVariable
                        minread=minread,
                        minoverlap=minoverlap,
                        lowfilter=lowfilter,
                        adapters3=adapterSeq3,
                        adapters5=adapterSeq5,
                        maxjump=0, 
                        cycle=1,
                        nodeLimit=config['buildgraph']['testrun'] * 2,
                        progress=progress,
                        logger=logger)
    
        # Clean small unsuccessful extensions
        asm.cleanDeadBranches(maxlength=10)
        
        # and too low covered assembling
        if coverageset:
            cutLowCoverage(asm,int(coverage),terminal=True)
        else:
            cutLowCoverage(asm,int(coverage/4),terminal=True)
            
    
        if snp:
            cutSNPs(asm)
        
        if config['buildgraph']['smallbranches'] is not None:
            smallbranches = config['buildgraph']['smallbranches']
        else:
            smallbranches = estimateDeadBrancheLength(asm)
            logger.info("Dead branch length setup to : %d bp" % smallbranches)
        
        asm.cleanDeadBranches(maxlength=smallbranches)
        
        if len(asm) > 0:
            score,length,ecoverage = coverageEstimate(asm,x,r)  # @UnusedVariable
            if not coverageset:
                coverage = ecoverage    
            minread,minoverlap = estimateMinRead(r,config['buildgraph']['minoverlap'],coverage) 
            logger.info("coverage estimated : %dx based on %d bp (minread: %d)" %(coverage,length/2,minread))
        
            
        # Reinitiate the assembling for running with the estimated parameters
        # Convert matches in sedd list    
        s = matchtoseed(x,r)
    
        # Create the assembler object
        asm = Assembler(r)
    
    #############################################
    #
    # We now run the main assembling process
    #
    #############################################

    logger.info('Starting the assembling')
    
    # Run the first assembling pass
    a = tango(asm,s,mincov=coverage/4,       #@UnusedVariable
                    minread=minread,
                    minoverlap=minoverlap,
                    lowfilter=lowfilter,
                    adapters3=adapterSeq3,
                    adapters5=adapterSeq5,
                    maxjump=0, 
                    cycle=1,
                    nodeLimit=assmax,
                    progress=progress,
                    logger=logger)

    # Clean small unsuccessful extensions
    asm.cleanDeadBranches(maxlength=10)
        
    # and too low covered assembling
    if coverageset:
        cutLowCoverage(asm,int(coverage),terminal=True)
    else:
        cutLowCoverage(asm,int(coverage/4),terminal=True)
        
    
    # cleanup snp bubble in the graph    
    if snp:
        cutSNPs(asm)
    
    if config['buildgraph']['smallbranches'] is not None:
        smallbranches = config['buildgraph']['smallbranches']
    else:
        smallbranches = estimateDeadBrancheLength(asm)
        logger.info("     Dead branch length setup to : %d bp" % smallbranches)

    asm.cleanDeadBranches(maxlength=smallbranches)


    # reestimate coverage
    
    if len(asm) == 0:
        logger.error('The assembling is empty - Stop the assembling process')
        sys.exit(1)

    score,length,ecoverage = coverageEstimate(asm,x,r)  # @UnusedVariable
    
    if not coverageset:
        coverage = ecoverage  
    
#     if coverage < 30:
#         sys.exit()

    if config['buildgraph']['minread'] is None:
        minread,minoverlap = estimateMinRead(r,config['buildgraph']['minoverlap'],coverage)
        minread/=4
        if minread<5:
            minread=5

    logger.info("coverage estimated : %d based on %d bp (minread: %d)" %(coverage,length/2,minread))
        
    meanlength,sdlength = estimateFragmentLength(asm)
    
    if config['orgasm']['back'] is not None:
        back = config['orgasm']['back']
    elif config['orgasm']['back'] is None and meanlength is not None:
        back = int(meanlength + 4 * sdlength)
        if back > 500:
            back=500
    else:
        back = 300
        
    if meanlength is not None:
        logger.info("Fragment length estimated : %f pb (sd: %f)" % (meanlength,sdlength))

    cg = asm.compactAssembling(verbose=False)
    genesincontig(cg,r,x)
    scaffold(asm,cg,minlink=5,back=back,addConnectedLink=False)
    with open(output+'.intermediate.gml','w') as gmlfile:
        print(cg.gml(),file=gmlfile)
    
    ###################################################
    #
    # We now fill the gaps between the contigs
    #
    ###################################################
    
    delta = 1
       
    # Run the fill gap procedure    
    while  delta > 0 or delta < -100 :
                   
        # intermediate graph are saved before each gap filling step
        dumpGraph(output+'.intermediate.oax',asm)
        
        delta = fillGaps(asm,back=back,
                       minread=minread,
                       maxjump=0,
                       minoverlap=minoverlap,
                       cmincov=2,
                       emincov=int(coverage/4),
                       gmincov=int(coverage/4),
                       lowfilter=lowfilter,
                       adapters5 = adapterSeq5,
                       adapters3 = adapterSeq3,
                       snp=snp,
                       nodeLimit=assmax)

        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print('==================================================================',file=sys.stderr)
        print('',file=sys.stderr)
        
        cg = asm.compactAssembling(verbose=False)
        genesincontig(cg,r,x)
        scaffold(asm,cg,minlink=5,back=back,addConnectedLink=False)
        with open(output+'.intermediate.gml','w') as gmlfile:
            print(cg.gml(),file=gmlfile)
        
        if meanlength is None:
            meanlength,sdlength = estimateFragmentLength(asm)
            if config['orgasm']['back'] is None and meanlength is not None:
                logger.info("Fragment length estimated : %f pb (sd: %f)" % (meanlength,sdlength))
                back = int(meanlength + 4 * sdlength)  
                if back > 500:
                    back=500
                         
        print('',file=sys.stderr)
        print('==================================================================',file=sys.stderr)
        print('',file=sys.stderr)
        
    ###################################################
    #
    # Finishing of the assembling
    #
    ###################################################

    if snp:
        logger.info("Clean polymorphisms")
        cutSNPs(asm)
        
    asi = len(asm)+1
    
    logger.info("Clean dead branches")
    while (asi>len(asm)):
        asi=len(asm)
        smallbranches = estimateDeadBrancheLength(asm)
        logger.info("     Dead branch length setup to : %d bp" % smallbranches)
        asm.cleanDeadBranches(maxlength=smallbranches)
        
    cg = asm.compactAssembling(verbose=False)
    
    
    if len(asm) == 0:
        logger.error('The assembling is empty - Stop the assembling process')
        sys.exit(1)

    score,length,ecoverage = coverageEstimate(asm,x,r)  # @UnusedVariable
    if not coverageset:
        coverage=ecoverage

    if snp:
        logger.info("Clean polymorphisms phase 2")
        cutSNPs(asm)
        
    logger.info("Clean low coverage terminal branches")
    if coverageset:
        cutLowCoverage(asm,int(coverage),terminal=False)
    else:
        cutLowCoverage(asm,int(coverage/2),terminal=True)
        logger.info("Clean low coverage internal branches")
        cutLowCoverage(asm,int(coverage/3),terminal=False)
        
    dumpGraph(output+'.oax',asm)
    asm = restoreGraph(output+'.oax',r,x)
        
    cg = asm.compactAssembling(verbose=False)     
        
    logger.info("Scaffold the assembly")
    scaffold(asm,cg,minlink=5,back=int(back),addConnectedLink=False)
    genesincontig(cg,r,x)
    with open(output+'.gml','w') as gmlfile:
        print(cg.gml(),file=gmlfile)
