import argparse


SnapCLParser = argparse.ArgumentParser(prog='mimodd snap', add_help=False,
                                       conflict_handler='resolve')
pe_group = SnapCLParser.add_argument_group('optional arguments affecting paired-end reads alignment')
adv_group = SnapCLParser.add_argument_group('optional advanced arguments')
sort_group = SnapCLParser.add_mutually_exclusive_group()
cigar_group = SnapCLParser.add_mutually_exclusive_group()
# mandatories (positional arguments)
SnapCLParser.add_argument('mode', metavar = 'sequencing mode', help = 'specify "single" or "paired" to indicate the sequencing mode')
SnapCLParser.add_argument('refgenome_or_indexdir', metavar = 'reference genome or index directory', help = 'an existing index directory generated by snap_index or a fasta reference genome (will be used to create the index)')
SnapCLParser.add_argument("inputfiles", metavar = 'input file(s)', nargs = "+", help = "one or two (in 'paired' mode with 'fastq' input format) input files")
# optionals (optional arguments)
# defaulting to argparse.SUPPRESS prevents function definition defaults from being overwritten
SnapCLParser.add_argument("-o", "--ofile", metavar = 'OFILE', dest = 'outputfile', default = argparse.SUPPRESS, help = 'name of the output file (required)')
SnapCLParser.add_argument("--iformat", default = "bam", help = 'input file format; must be fastq, gz, sam or bam (default: bam)')
SnapCLParser.add_argument("--oformat", default = "bam", help = 'output file format (sam or bam; default: bam)')
SnapCLParser.add_argument('--header', default = argparse.SUPPRESS, help = 'a SAM file providing header information to be used for the output (required for input in fastq format and with unheadered SAM/BAM input, optional for headered SAM/BAM input; replaces header information found in the input file')
SnapCLParser.add_argument("-t", "--threads", type=int, default=argparse.SUPPRESS, help='number of threads to use (overrides config setting)')
SnapCLParser.add_argument("-m", "--memory", type=int, dest='maxmem', metavar='MEMORY', default=argparse.SUPPRESS, help='maximal amount of memory to be used in GB (overrides config setting),\nwill be respected during sorting only')
sort_group.add_argument('--no-sort', action='store_false', dest='sort', help='output reads in their original order, i.e., do not sort by alignment location')
SnapCLParser.add_argument('-q', '--quiet', action = 'store_true', default = False, help = 'suppress original messages from SNAP')
SnapCLParser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'verbose output (independent of SNAP)')
pe_group.add_argument('-D', '--discard-overlapping-mates', dest='discard_overlapping', nargs='*', metavar='RF|FR|FF|RR|ALL', default=argparse.SUPPRESS, help='consider overlapping mate pairs of the given orientation type(s) anomalous and discard them; default: keep all overlapping mate pairs')
pe_group.add_argument("-s", "--spacing", nargs=2, metavar=('MIN','MAX'), default=argparse.SUPPRESS, help='min and max spacing to allow between paired ends (default: 100 10000)')
adv_group.add_argument("-d", "--maxdist", metavar='EDIT DISTANCE', type=int, default=8, help='maximum edit distance allowed per read or pair (default: 8)')
adv_group.add_argument("-n", "--maxseeds", metavar='SEEDS', type=int, default=argparse.SUPPRESS, help='number of seeds to use per read (default: 25)')
adv_group.add_argument("-h", "--maxhits", metavar='HITS', type=int, default=argparse.SUPPRESS, help='maximum hits to consider per seed (default: 250)')
adv_group.add_argument("-c", "--confdiff", metavar='THRESHOLD', type=int, default=2, help='confidence threshold (default: 2)')
adv_group.add_argument("-a", "--confadapt", metavar='THRESHOLD', type=int, default=7, help='confidence adaptation threshold (default: 7)')
adv_group.add_argument("-e", "--error-rep", dest='error_rep', action='store_true', default=argparse.SUPPRESS, help='compute error rate assuming wgsim-generated reads')
adv_group.add_argument('-P', '--no-prefetch', dest='no_prefetch', action='store_true', default=False, help='disables cache prefetching in the genome; may be helpful for machines with small caches or lots of cores/cache')
adv_group.add_argument("-x", "--explore", action='store_true', default=argparse.SUPPRESS, help='explore some hits of overly popular seeds (useful for filtering)')
adv_group.add_argument("-f", '--stop-on-first', dest='stop_on_first', action='store_true', default=argparse.SUPPRESS, help='stop on first match within edit distance limit (filtering mode)')
adv_group.add_argument("-F", "--filter-output", dest='filter_output', metavar='FILTER', default=argparse.SUPPRESS, help='retain only certain read classes in output (a=aligned only, s=single hit only, u=unaligned only)')
adv_group.add_argument("-I", "--ignore", action='store_true', default=argparse.SUPPRESS, help='ignore non-matching IDs in the paired-end aligner')
adv_group.add_argument("-S", "--selectivity", type=int, default=argparse.SUPPRESS, help='selectivity; randomly choose 1/selectivity of the reads to score')
adv_group.add_argument("-C", "--clipping", metavar='++|+x|x+|xx', default='++', help='specify a combination of two + or x symbols to indicate whether to clip low-quality bases from the front and back of reads respectively; default: clip from front and back (-C ++)')
adv_group.add_argument("-G", "--gap-penalty", dest='gap_penalty', metavar='PENALTY', type=int, default=argparse.SUPPRESS, help='specify a gap penalty to use when generating CIGAR strings')
adv_group.add_argument("-b", "--bind-threads", dest='bind_threads', action='store_true', default=argparse.SUPPRESS, help='bind each thread to its processor (off by default)')
cigar_group.add_argument("-X", dest='mmatch_notation', action='store_false', help='CIGAR strings in the output should use = and X to indicate matches/mismatches rather than M (alignment match);\nUSE OF THIS OPTION IS DISCOURAGED as =/X CIGAR strings are still not fully supported by useful third-party tools like IGV')
cigar_group.add_argument("-M", "--mmatch-notation", dest='mmatch_notation', action='store_true', default=True, help='legacy option retained for backwards compatibility;\nindicates that CIGAR strings in the output should use M (alignment match) rather than = and X (sequence (mis-)match);\n-M is implied by default, use -X to turn off')
sort_group.add_argument('--sort', '--so', action='store_true', default=True, help='legacy option retained for backwards compatibility;\nsort output file by alignment location; implied by default, use --no-sort to turn off')
idx_group = SnapCLParser.add_argument_group('optional arguments affecting indexing')
idx_group.add_argument("--idx-seedsize", dest = 'idx_seedsize', metavar = 'SEED SIZE', type = int, default = argparse.SUPPRESS, help = 'Seed size used in building the index (default: 20)')
idx_group.add_argument("--idx-slack", dest = 'idx_slack', metavar = 'SLACK', type = float, default = argparse.SUPPRESS, help = 'Hash table slack for indexing (default: 0.3)')
idx_group.add_argument('--idx-overflow', dest ='idx_ofactor', metavar = 'FACTOR', type = int, default = argparse.SUPPRESS, help = 'factor (between 1 and 1000) to set the size of the index build overflow space (default: 40)')
idx_group.add_argument('--idx-out', metavar = 'INDEX DIR', dest = 'idx_out', default = argparse.SUPPRESS, help = 'name of the index directory to be created; if given, the index directory will be permanent, otherwise a temporary directory will be used')
