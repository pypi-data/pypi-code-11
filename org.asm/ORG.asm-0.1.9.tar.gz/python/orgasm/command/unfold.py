'''
Created on 28 sept. 2014

@author: coissac
'''
from orgasm import getIndex, getSeeds
from orgasm.tango import restoreGraph, estimateFragmentLength, genesincontig,\
    pathConstraints, scaffold, selectGoodComponent, unfoldAssembling, path2fasta

__title__="Universal assembling graph unfolder"

default_config = { 'circular' : False,
                   'force'    : False
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the orgasmi command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='output', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    
    parser.add_argument('--circular',         dest='unfold:circular', 
                                              action='store_true', 
                                              default=None, 
                        help='Wish a circular unfolding')

    parser.add_argument('--force',            dest='unfold:force', 
                                              action='store_true', 
                                              default=None, 
                        help='Force circular unfolding')

    parser.add_argument('--back',             dest='orgasm:back', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')
    


def run(config):

    logger=config['orgasm']['logger']
    output = config['orgasm']['outputfilename'] 

    if config['unfold']['force']:
        config['unfold']['circular']= True
        

    r = getIndex(config)
    coverage,x = getSeeds(r,config)  
    
    asm = restoreGraph(output+'.oax',r,x)

    logger.info("Evaluate fragment length")
    
    meanlength,sdlength = estimateFragmentLength(asm)
    
    if meanlength is not None:
        logger.info("Fragment length estimated : %f pb (sd: %f)" % (meanlength,sdlength))

    if config['orgasm']['back'] is not None:
        back = config['orgasm']['back']
    elif config['orgasm']['back'] is None and meanlength is not None:
        back = int(meanlength + 4 * sdlength)
        if back > 500:
            back=500
    else:
        back = 300
        
    logger.info("Evaluate pair-end constraints")
    
    cg = asm.compactAssembling(verbose=False)
    
    genesincontig(cg,r,x)

    constraints = pathConstraints(asm,cg,back=int(back),minlink=5)
    scaffold(asm,cg,minlink=config['orgasm']['minlink'],
             back=int(back),addConnectedLink=False)
     

    fastaout = open(output+".fasta","w")
    pathout  = open(output+".path","w")
    
    
    logger.info("Select the good connected componantes")
    gcc = selectGoodComponent(cg)
    
    logger.info("Print the result as a fasta file")
    
    if config['unfold']['circular']:
        if config['unfold']['force']:
            logger.info("Force circular sequence")
        else:
            logger.info("Unfolding in circular mode")
        
    c=1
    for seeds in gcc:
        path = unfoldAssembling(asm,cg,
                                seeds=seeds,
                                constraints=constraints,
                                circular=config['unfold']['circular'],
                                force=config['unfold']['force'])
            
        path = path[-1][0]
                        
        fa = path2fasta(asm,cg,path,
             identifier="Seq_%d" % c,
             back=back,
             minlink=config['orgasm']['minlink'],
             logger=logger)
        print(fa,file=fastaout)
        print(" ".join([str(x) for x in path]),file=pathout)

        c+=1
        
    with open(output +'.path.gml','w') as gmlfile:
        print(cg.gml(),file=gmlfile)

              
