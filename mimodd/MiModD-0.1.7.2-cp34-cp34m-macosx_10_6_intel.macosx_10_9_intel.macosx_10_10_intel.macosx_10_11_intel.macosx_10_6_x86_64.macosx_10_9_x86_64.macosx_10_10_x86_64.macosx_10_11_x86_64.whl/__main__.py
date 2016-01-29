# this is the complete command line parser and tool dispatcher for the MiModD
# Python package

import os
import argparse
import importlib

from . import __version__, terms
from . import auxparsers
from . import MiModDError

from .encoding_base import DEFAULTENCODING, FALLBACKENCODING


if os.path.exists(
    os.path.join(
        os.path.dirname(__file__),
        '__first_run__.py')):
    print (terms)
    raise MiModDError(
"""This is a fresh installation of the package.

You MUST run the config tool once before you can start using it.""")


# argparse.Action subclasses
def str_or_None (string):
    """Convert empty strings to None.

    Used to convert empty command line arguments to None before passing them
    to underlying Python functions."""
    
    if string:
        return string
    else:
        return None


class Extend(argparse.Action):
    """Custom action similar to the 'append' action.

    Useful for optional arguments parsed with nargs='*' or nargs='+' if you do
    not want the nested lists produced by 'append'."""
    
    def __call__ (self, parser, namespace, values, option_string = None):
        setattr(namespace, self.dest,
                getattr(namespace, self.dest, []) + values)

# subclass for exclusive use by the annotate subparser
class LinkFormatter(argparse.Action):
    def __call__ (self, parser, namespace, formatter_file, option_string=None):
        with open(formatter_file, 'r', encoding=FALLBACKENCODING) as f:
            formatter_dict = {}
            keys_required = []
            lines = f.readlines()
            if FALLBACKENCODING != DEFAULTENCODING:
                try:
                    lines.encode(FALLBACKENCODING).decode(DEFAULTENCODING)
                except UnicodeDecodeError:
                    pass
            for line in lines:
                tmp = line.split(':', 1)
                if len(tmp) == 2:
                    attribute, value = tmp[0].strip(), tmp[1].strip()
                    if attribute == 'species':
                        species = value
                        if keys_required:
                            break
                        if value in formatter_dict:
                            raise KeyError('Species {0} found twice in formatter file.'.format(species))
                        formatter_dict[species] = {}
                        keys_required = ['gene', 'pos']
                    elif attribute in keys_required:
                        formatter_dict[species][attribute] = value
                        keys_required.remove(attribute)
                    elif attribute in formatter_dict[species]:
                        raise KeyError('Attribute {0} found twice in species description {1}.'.format(attribute, species))

            if keys_required:
                raise KeyError('Truncated entry {0} in file {1}: did not specify the required key(s): {2}'.format(species, formatter_file, keys_required))
            setattr(namespace, 'link_formatter', formatter_dict)
            

# COMMAND LINE PARSERS FOR MIMODD MODULES
parser = argparse.ArgumentParser(usage = argparse.SUPPRESS, formatter_class = argparse.RawDescriptionHelpFormatter,
                                 description = terms + """

general command line usage:

  %(prog)s <tool> [OPTIONS]     to run a specific tool

  %(prog)s <tool> --help        for more detailed help on a specific tool
  
""")

subparsers = parser.add_subparsers(title = 'available tools', metavar = '')

# ++++++++++ version +++++++++++
p_info = subparsers.add_parser('version')
p_info.add_argument('-q', '--quiet', help = 'print version number only', action = 'store_true', default = argparse.SUPPRESS)
p_info.set_defaults(version = True)
                      
# ++++++++++ info +++++++++++
p_info = subparsers.add_parser('info',
                               help = 'retrieve information about the samples encoded in a file for various supported formats')
p_info.add_argument('ifile', metavar = 'input file', help = 'input file (supported formats: sam, bam, vcf, bcf, fasta)')
p_info.add_argument('-o', '--ofile', help = 'redirect the output to the specified file (default: stdout)')
p_info.add_argument('-v', '--verbose', help = 'verbose output', action = 'store_true', default = argparse.SUPPRESS)
p_info.add_argument('--oformat', metavar = 'html|txt', default = argparse.SUPPRESS, help = 'format for the output (default: txt)')
p_info.set_defaults(module = 'fileinfo', func = ['fileinfo'])

# +++++++++++ header +++++++++++++
p_samheader = subparsers.add_parser('header',
                                    help = 'generate a SAM format header from an NGS run description')
rg_group = p_samheader.add_argument_group('read group description')
rg_group.add_argument('--rg-id', dest = 'rg_id', nargs = '+', action = Extend, default=[], help = 'one or more unique read group identifiers')
rg_group.add_argument('--rg-sm', dest = 'rg_sm', nargs = '+', type = str_or_None, action = Extend, default = argparse.SUPPRESS, help = 'one sample name per read group identifier')
rg_group.add_argument("--rg-cn", dest = 'rg_cn', nargs = "+", type = str_or_None, action = Extend, default = argparse.SUPPRESS, help = 'one sequencing center name per read group')
rg_group.add_argument("--rg-ds", dest = 'rg_ds', nargs = "+", type = str_or_None, action = Extend, default = argparse.SUPPRESS, help = 'one description line per read group')
rg_group.add_argument("--rg-dt", dest = 'rg_dt', nargs = "+", type = str_or_None, action = Extend, default = argparse.SUPPRESS, help = 'date runs were produced (YYYY-MM-DD); one date per read group')
rg_group.add_argument("--rg-lb", dest = 'rg_lb', nargs = "+", type = str_or_None, action = Extend, default = argparse.SUPPRESS, help = 'library identifier for each read group')
rg_group.add_argument("--rg-pl", dest = 'rg_pl', nargs = "+", type = str_or_None, action = Extend, default = argparse.SUPPRESS, help = 'sequencing platform/technology used to produce each read group')
rg_group.add_argument("--rg-pi", dest = 'rg_pi', nargs = "+", type = str_or_None, action = Extend, default = argparse.SUPPRESS, help = 'predicted median insert size for the reads of each read group')
rg_group.add_argument("--rg-pu", dest = 'rg_pu', nargs = "+", type = str_or_None, action = Extend, default = argparse.SUPPRESS, help = 'platform unit, e.g., flowcell barcode or slide identifier, for each read group')
oth_group = p_samheader.add_argument_group('other information')
oth_group.add_argument("--co", nargs = "*", metavar = 'COMMENT', dest ="comments", default = argparse.SUPPRESS, help = 'an arbitrary number of one-line comment strings')
p_samheader.add_argument("-o", "--ofile", metavar = 'OFILE', dest = 'outputfile', default = argparse.SUPPRESS, help = 'redirect the output to the specified file (default: stdout)')
p_samheader.add_argument('-x', '--relaxed', dest = 'optional_sm', action = 'store_true', default = argparse.SUPPRESS, help = 'do not enforce a sample name to be specified for every read group')
p_samheader.set_defaults(module = 'samheader', func = ['run_as_main'])

# ++++++++++ convert ++++++++++
p_convert = subparsers.add_parser('convert', conflict_handler='resolve',
                                 help = 'convert between different sequenced reads file formats')
p_convert.add_argument("input1", metavar = 'input_file(s)', nargs = '+', help = 'a list of input files (alternating r1 and r2 files for paired-end data')
p_convert.add_argument("--iformat", choices = ('fastq','fastq_pe','gz','gz_pe','sam','bam'), default = argparse.SUPPRESS, help = 'the format of the input file(s) (default: bam)')
p_convert.add_argument('-o', '--ofile', metavar = 'OFILE', dest="outputname", default = argparse.SUPPRESS, help = 'redirect the output to the specified file (default: stdout)')
p_convert.add_argument("--oformat", choices = ('sam','bam','fastq','gz'), default = argparse.SUPPRESS, help = 'the output format (default: sam)')
p_convert.add_argument('-h', "--header", default = argparse.SUPPRESS, help = 'optional SAM file, the header information of which should be used in the output (will overwrite pre-existing header information from the input file); not allowed for input in SAM/BAM format')
p_convert.add_argument('-r', "--split-on-rgs", action = 'store_true', default = argparse.SUPPRESS, help = 'if the input file has reads from different read groups, write them to separate output files (using --ofile OFILE as a file name template); implied for conversions to fastq format')
p_convert.add_argument('-t', '--threads', type = int, default = argparse.SUPPRESS, help = 'the number of threads to use (overrides config setting; ignored if not applicable to the conversion)')
p_convert.set_defaults(module = 'convert', func = ['clparse_convert'])

# ++++++++++ reheader ++++++++++++++++++++
p_reheader = subparsers.add_parser('reheader',
                                   help = 'from a BAM file generate a new file with specified header sections modified based on the header of a template SAM file')
p_reheader.add_argument('template', nargs = '?', help = 'template SAM file providing header information')
p_reheader.add_argument('inputfile', metavar = 'input_file', help = 'input BAM file to reheader')
p_reheader.add_argument('--rg', nargs = '+', metavar = ('ignore|update|replace [RG_TEMPLATE]', 'RG_MAPPING'), default = argparse.SUPPRESS,
                        help = """how to compile the read group section of the new header;
ignore: do not use template information -> keep original read groups, update: use template information to update original header content, replace: use only template read group information -> discard original
(default: replace if a general template is specified, ignore if not);
the optional RG_TEMPLATE is used instead of the general template to provide the template read group information;
by default, update mode uses template information about read-groups to add to / overwrite the original information of read-groups with the same ID,
keeps all read-groups found only in the original header and adds read-groups found only in the template;
replace overwrites all original information about a read-group if a read-group with the same ID is found in the template, discards all read-groups found only in the original header and adds read-groups found only in the template; 
to update or replace the information of a read group with that of a template read-group with a different ID, a RG_MAPPING between old and new ID values can be provided in the format old_id : new_id [old_id : new_id, ..]""")
p_reheader.add_argument('--sq', nargs = '+', metavar = ('ignore|update|replace [SQ_TEMPLATE]', 'SQ_MAPPING'), default = argparse.SUPPRESS,
                        help = """how to compile the sequence dictionary of the new header;
ignore: do not use template information -> keep original sequence dictionary, update: use template information to update original header content, replace: use only template sequence information -> discard original
(default: replace if a general template is specified, ignore if not);
the optional SQ_TEMPLATE is used instead of the general template to provide the template sequence dictionary;
by default, update mode uses template sequence information to add to / overwrite the original information of sequences with the same name (SN tag value),
keeps all sequences found only in the original header and adds sequences found only in the template;
replace overwrites all original information about a sequence if a sequence with the same name is found in the template, discards all sequences found only in the original header and adds sequences found only in the template; 
to update or replace the information about a sequence with that of a template sequence with a different name, a SQ_MAPPING between old and new sequence names (SN values) can be provided in the format old_sn : new_sn [old_sn : new_sn, ..];
to protect against file format corruption, the tool will NEVER modify the recorded LENGTH (LN tag) nor the MD5 checksum (M5 tag) of any sequence""")
p_reheader.add_argument('--co', nargs = '+', metavar = ('ignore|update|replace', 'CO_TEMPLATE'), default = argparse.SUPPRESS,
                        help = """how to compile the comments (CO lines) of the new header;
ignore: do not use template comments -> keep original comments, update: append template comment lines to original comments, replace: use only template comments -> discard original
(default: replace if a general template is specified, ignore if not);
the optional CO_TEMPLATE is used instead of the general template to provide the template comments""")
p_reheader.add_argument('--rgm', nargs = "+", dest = 'rg_mapping', default = argparse.SUPPRESS,
                        help = """optional mapping between read group ID values in the format old_id : new_id [old_id : new_id, ..];
Used to rename read groups and applied AFTER any other modifications to the read group section (i.e., every old_id must exist in the modified header)""")
p_reheader.add_argument('--sqm', nargs = "+", dest = 'sq_mapping', default = argparse.SUPPRESS,
                        help = """optional mapping between sequence names (SN field values) in the format old_sn : new_sn [old_sn : new_sn, ..];
used to rename sequences in the sequence dictionary and applied AFTER any other modifications to the sequence dictionary (i.e., every old_sn must exist in the modified header)""")
p_reheader.add_argument('-o', '--ofile', metavar = 'OFILE', dest = 'outputfile', help = 'redirect the output to the specified file (default: stdout)')
p_reheader.add_argument('-H', dest = 'header_only', action = 'store_true', default = False, help = 'output only the resulting header')
p_reheader.add_argument('-v', '--verbose', action = 'store_true', default = False)
p_reheader.set_defaults(module = 'convert', func = ['clparse_reheader'])

# ++++++++++ sort ++++++++++++
p_sort = subparsers.add_parser('sort',
                                   help='sort a SAM or BAM file by coordinates (or names) of the mapped reads')
p_sort.add_argument('ifile', metavar='input_file', help='the unsorted input file in SAM/BAM format')
p_sort.add_argument('-o', '--ofile', metavar='OFILE', default=argparse.SUPPRESS, help='redirect the output to the specified file (default: stdout)')
p_sort.add_argument('--iformat', metavar='bam|sam', default=argparse.SUPPRESS, help='the format of the input file (default: assume bam)')
p_sort.add_argument('--oformat', metavar='bam|sam', default=argparse.SUPPRESS, help='specify whether the output should be in sam or bam format (default: bam)')
p_sort.add_argument('-n', '--by-name', dest='by_read_name', action='store_true', default=argparse. SUPPRESS, help='sort by read name')
p_sort.add_argument('-l', dest='compression_level', type=int, default=argparse.SUPPRESS, help='compression level, from 0 to 9')
p_sort.add_argument('-m', '--memory', type=int, dest='maxmem', metavar='MEMORY', default=argparse.SUPPRESS, help='maximal amount of memory to be used in GB (overrides config setting)')
p_sort.add_argument('-t', '--threads', type=int, default=argparse.SUPPRESS, help='the number of threads to use (overrides config setting)')
p_sort.set_defaults(module = 'pysamtools', func = ['sort'])

# +++++++++++ snap ++++++++++++++++++
p_snap = subparsers.add_parser('snap', parents = [auxparsers.SnapCLParser], conflict_handler = 'resolve',
                               help = 'align sequence reads using the SNAP aligner')
p_snap.set_defaults(module = 'snap', func = ['snap_call'])

# +++++++++++ snap_batch ++++++++++++
p_snap_batch = subparsers.add_parser('snap-batch',
                                     help = 'run several snap jobs and pool the resulting alignments into a multi-sample SAM/BAM file')
xor = p_snap_batch.add_mutually_exclusive_group(required = True)
xor.add_argument('-s', metavar = '"COMMAND"', dest = 'commands', nargs='+', help = 'one or more completely specified command line calls to the snap tool (use "" to enclose individual lines)')
xor.add_argument('-f', metavar = 'FILE', dest = 'ifile', help = 'an input file of completely specified command line calls to the snap tool')

p_snap_batch.set_defaults(module = 'snap', func = ['snap_batch','make_snap_argdictlist'])

# +++++++++++ snap_index ++++++++++++
p_snap_index = subparsers.add_parser('snap-index', conflict_handler='resolve',
                                     help = 'index a reference genome for use with the SNAP aligner')
p_snap_index.add_argument('ref_genome', metavar = 'reference_genome', help = 'fasta reference genome to index')
p_snap_index.add_argument('index_out', metavar = 'index_directory', help = 'path specifying the index directory to be created')
p_snap_index.add_argument('-s', '--seedsize', '--idx-seedsize', type = int, default = argparse.SUPPRESS, help = 'Seed size used in building the index (default: 20)')
p_snap_index.add_argument('-h', '--slack', '--idx-slack', type = float, default = argparse.SUPPRESS, help = 'Hash table slack for indexing (default: 0.3)')
p_snap_index.add_argument('-O', '--overflow', '--idx-overflow', dest ='idx_ofactor', metavar = 'FACTOR', type = int, default = argparse.SUPPRESS, help = 'factor (between 1 and 1000) to set the size of the index build overflow space (default: 40)')
p_snap_index.add_argument("-t", "--threads", type = int, default = argparse.SUPPRESS, help = 'number of threads to use (overrides config setting)')
p_snap_index.set_defaults(module = 'snap', func = ['snap_index'])

# +++++++++++ varcall +++++++++++++
p_varcall = subparsers.add_parser('varcall',
                                  help = 'predict SNPs and indels in one or more aligned read samples and calculate the coverage of every base in the reference genome using samtools/bcftools')
p_varcall.add_argument("ref_genome", metavar = 'reference_genome', help = 'the reference genome (in fasta format)')
p_varcall.add_argument("inputfiles", metavar = 'input_file(s)', nargs = "+", help = 'one or more BAM input files of aligned reads from one or more samples (will be indexed automatically)')
p_varcall.add_argument('-d', '--depth', type=int, default=250, help='max per-BAM depth to avoid excessive memory usage (default: 250)')
p_varcall.add_argument('-i', '--group-by-id', dest = 'group_by_id', action = 'store_true', default = False, help = 'optional flag to control handling of multi-sample input; if enabled, reads from different read groups are analyzed as separate samples even if the sample names associated with the read groups are identical; otherwise, the samtools default is used (reads are grouped based on the sample names of their read groups)')
p_varcall.add_argument('-x', '--relaxed', dest = 'md5check', action = 'store_false', help = 'turn off md5 checksum comparison between sequences in the reference genome and those specified in the BAM input file header(s)')
p_varcall.add_argument('-q', '--quiet', action = 'store_true', default = False, help = 'suppress original messages from samtools mpileup and bcftools call')
p_varcall.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'verbose output independent of samtools/bcftools')
p_varcall.add_argument('-o', '--ofile', metavar = 'OFILE', dest = 'output_vcf', help = 'redirect the output (variant sites) to the specified file (default: stdout)')
p_varcall.add_argument('-t', '--threads', type = int, default = argparse.SUPPRESS, help = 'the number of threads to use (overrides config setting)')
p_varcall.set_defaults(module = 'variant_calling', func = ['varcall'])

# +++++++++++ varextract +++++++
p_varex = subparsers.add_parser('varextract',
                                  help = 'extract variant sites from BCF input as generated by varcall and report them in VCF')
p_varex.add_argument("inputfile", metavar = 'input file', help = 'BCF output from varcall')
p_varex.add_argument('-p', '--pre-vcf', metavar = 'VCF_INPUT', nargs = '+', dest = 'vcf_pre')
p_varex.add_argument('-a', '--keep-alts', action = 'store_true', default = argparse.SUPPRESS, help = 'keep all alternate allele candidates even if they do not appear in any genotype')
p_varex.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'verbose output')
p_varex.add_argument('-o', '--ofile', metavar = 'OFILE', dest = 'output_vcf', help = 'redirect the output (variant sites) to the specified file (default: stdout)')
p_varex.set_defaults(module = 'variant_calling', func = ['varextract'])

# +++++++++++ covstats +++++++++
p_stats = subparsers.add_parser('covstats',
                                help = 'summary coverage statistics for varcall output')
p_stats.add_argument("inputfile", metavar = 'input file', help = 'BCF output from varcall')
p_stats.add_argument('-o', '--ofile', metavar = 'OFILE', help = 'redirect the output to the specified file (default: stdout)')
p_stats.set_defaults(module = 'variant_calling', func = ['get_coverage_from_vcf'])

# ++++++++++ delcall ++++++++
p_delcall = subparsers.add_parser('delcall',
                                  help = 'predict deletions in one or more samples of aligned paired-end reads based on coverage of the reference genome and on insert sizes')
p_delcall.add_argument('ibams', metavar = 'BAM input file(s)', nargs = '+', help= 'one or more BAM input files of aligned reads from one or more samples')
p_delcall.add_argument('icov', metavar = 'BCF file with coverage information', help= 'coverage input file (as generated by the varcall tool)')
p_delcall.add_argument('-o', '--ofile', help = 'redirect the output to the specified file (default: stdout)')
p_delcall.add_argument('--max-cov', metavar = 'COVERAGE THRESHOLD', dest = 'max_cov', type = int, default = argparse.SUPPRESS, help = 'maximal coverage allowed at any site within an uncovered region (default: 0)')
p_delcall.add_argument('--min-size', metavar = 'SIZE THRESHOLD', dest = 'min_size', type = int, default = argparse.SUPPRESS, help = 'minimal size in nts for an uncovered region to be reported (default: 100)')
p_delcall.add_argument('-u', '--include-uncovered', dest = 'include_uncovered', action = 'store_true', default=argparse.SUPPRESS, help = 'include uncovered regions in the output that did not get called as deletions')
p_delcall.add_argument('-i', '--group-by-id', dest = 'group_by_id', action = 'store_true', default = False, help = 'optional flag to control handling of multi-sample input; if enabled, reads from different read groups will be treated strictly separate. If turned off, read groups with identical sample names are used together for identifying uncovered regions, but are still treated separately for the prediction of deletions.')
p_delcall.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'verbose output')
p_delcall.set_defaults(module = 'deletion_calling', func = ['delcall'])

# ++++++++++ vcf-filter ++++++++++++++++++
p_vcf_filter = subparsers.add_parser('vcf-filter',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     help='extract lines from a vcf variant file based on sample- and field-specific filters',
                                     epilog="""Example filters:
-s sample1 --gt 0/1,1/1
\t\tretain all entries of the vcf input file for which
\t\tsample1's genotype is 0/1 (heterozygous) or
\t\t1/1 (homozygous variant)
-s sample1 sample2 --gt 0/1,1/1 0/0
\t\tretain all entries for which sample1's genotype is 0/1 or 1/1
\t\tAND for which sample2's genotype is 0/0
-s sample1 sample2 --gt 0/1,1/1 ANY --dp 3 3
\t\tretain all entries for which sample1's genotype is 0/1 or 1/1
\t\tAND for which sample1 and sample2 show at least 3-fold coverage
\t\t(sample2's genotype doesn't matter)
"""
                                     )
p_vcf_filter.add_argument('ifile', nargs='?', metavar='input_file', help='a vcf input file (default: stdin)')
p_vcf_filter.add_argument('-o', '--ofile', metavar='OFILE', default=argparse.SUPPRESS, help='redirect the output to the specified file (default: stdout)')
p_vcf_filter.add_argument('-s', '--samples', metavar='SAMPLE_NAME', nargs='+', default=argparse.SUPPRESS, help='one or more sample names that the sample-specific filters --gt , --dp, and --gq should work on.')
p_vcf_filter.add_argument('--gt', metavar='GT_PATTERN', nargs='+', default=argparse.SUPPRESS, help='genotype patterns (one per sample, use ANY to skip the requirement for a given sample) to be included in the output; format: x/x where x = 0 and x = 1 stand for the reference and the variant allele, respectively; multiple allowed genotypes for a sample can be specified as a comma-separated list')
p_vcf_filter.add_argument('--dp', metavar='DP_THRESHOLD', nargs='+', default=argparse.SUPPRESS, type=int, help='minimal coverage (one per sample, use 0 to skip the requirement for a given sample) required to include a site in the output')
p_vcf_filter.add_argument('--gq', metavar='GQ_THRESHOLD', nargs='+', default=argparse.SUPPRESS, type=int, help='minimal genotype quality (one per sample, use 0 to skip the requirement for a given sample) required to include a site in the output')
p_vcf_filter.add_argument('--af', metavar='ALLELE#:MIN_FRACTION:MAX_FRACTION', nargs='+', default=argparse.SUPPRESS, help='the fraction of reads supporting a specific ALLELE# must be between MIN_FRACTION and MAX_FRACTION to include the site in the output')
p_vcf_filter.add_argument('-r', '--region', nargs='*', dest='region_filter', default=argparse.SUPPRESS, help='keep only variants that fall in one of the given chromsomal regions (specified in the format CHROM:START-STOP or CHROM: for a whole chromosome)')
group = p_vcf_filter.add_mutually_exclusive_group()
group.add_argument('-I', '--no-indels', dest='type_filter', action='store_const', const=1, default=0, help='skip indels in the output')
group.add_argument('-i', '--indels-only', dest='type_filter', action='store_const', const=2, default=0, help='keep only indels in the output')
p_vcf_filter.add_argument('--vfilter', dest='v_filter', nargs='+', default=argparse.SUPPRESS, help='vertical sample names filter; if given, only sample columns specified by name will be retained in the output')
p_vcf_filter.set_defaults(module='vcf_filter', func=['filter'])

# +++++++++++ annotate ++++++++++++++++        
p_annotate = subparsers.add_parser('annotate',
                                 help = 'annotate a vcf variant file with information about the affected genes')
p_annotate.add_argument("inputfile", metavar = 'input_file', help = 'a vcf input file')
# optional args
p_annotate.add_argument('--species', '--sp', default = argparse.SUPPRESS, help = 'the name of the species to be assumed when generating annotations')
p_annotate.add_argument('-o', '--ofile', default = argparse.SUPPRESS, help = 'redirect the output to the specified file (default: stdout)')
p_annotate.add_argument('-f', '--oformat', metavar = 'html|text', choices = ('html', 'text'), default = argparse.SUPPRESS, help = 'the format of the output file (default: html)')
p_annotate.add_argument('-l', '--link', metavar = 'link_formatter_file', action = LinkFormatter, default = argparse.SUPPRESS, help = 'file to read hyperlink formatting instructions from')
p_annotate.add_argument('--grouping', metavar = 'by_sample|by_genes', choices = ('by_sample', 'by_genes'), default = argparse.SUPPRESS, help = 'group variants "by_sample" or "by_genes" instead of keeping the order defined in the input file')
p_annotate.add_argument('-q', '--quiet', action = 'store_true', default = False, help = 'suppress original messages from SnpEff')
p_annotate.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'verbose output (independent of SnpEff)')
# snpeff group of arguments
snpeff_group = p_annotate.add_argument_group('optional SnpEff-specific arguments')
snpeff_group.add_argument('-c', '--config', dest = 'snpeff_path', metavar = 'PATH', default = argparse.SUPPRESS,
                        help = 'location of the SnpEff installation directory. Will override MiModD config settings if provided.')
snpeff_group.add_argument('-g', '--genome', default = argparse.SUPPRESS, help = 'the name of an installed SnpEff genome annotation file (the snpeff_genomes tool can be used to get a list of all such names')
snpeff_group.add_argument('-s', '--snpeff-out', metavar = 'OFILE', dest = 'snpeff_out', default = argparse.SUPPRESS, help = 'redirect the original vcf output of SnpEff to the specified file and keep it (default: do not generate SnpEff vcf file)')
snpeff_group.add_argument('--stats', metavar = 'SUMMARY_FILE', default = argparse.SUPPRESS, help = 'generate a results summary file of the specified name')
snpeff_group.add_argument('-m', '--memory', type=int, default=argparse.SUPPRESS, help = 'maximal memory to use in GB (overrides config setting)')
snpeff_group.add_argument('--chr', action="store_true", default=argparse.SUPPRESS, help = 'prepend "chr" to chromosome names, e.g., "chr7" instead of "7"')
snpeff_group.add_argument('--minC', metavar = 'COVERAGE_THRESHOLD', type=int, default=argparse.SUPPRESS, help = 'do not include variants with a coverage lower than this threshold (default: no filtering)')
snpeff_group.add_argument('--minQ', metavar = 'QUAL_THRESHOLD', type=int, default=argparse.SUPPRESS, help = 'do not include variants with a quality lower than this threshold (default: no filtering)')
snpeff_group.add_argument('--no-downstream', dest = 'no_downstream', action="store_true", default=argparse.SUPPRESS, help = 'do not include downstream effects in the output')
snpeff_group.add_argument('--no-upstream', dest = 'no_upstream', action="store_true", default=argparse.SUPPRESS, help = 'do not include upstream effects in the output')
snpeff_group.add_argument('--no-intron', dest = 'no_intron', action="store_true", default=argparse.SUPPRESS, help = 'do not include intron effects in the output')
snpeff_group.add_argument('--no-intergenic', dest = 'no_intergenic', action="store_true", default=argparse.SUPPRESS, help = 'do not include intergenic effects in the output')
snpeff_group.add_argument('--no-utr', dest = 'no_utr', action="store_true", default=argparse.SUPPRESS, help = 'do not include UTR effects in the output')
snpeff_group.add_argument('--ud', metavar = 'DISTANCE', type=int, default=argparse.SUPPRESS, help = 'specify the upstream/downstream interval length, i.e., variants more than DISTANCE nts from the next annotated gene are considered to be intergenic')
p_annotate.set_defaults(module = 'variant_annotation', func = ['annotate'])

# ++++++++++++ snpeff_genomes ++++++++++++
p_snpeff_genomes = subparsers.add_parser('snpeff-genomes',
                                         help = 'list installed SnpEff genomes')
p_snpeff_genomes.add_argument('-c', '--config', dest = 'snpeff_path', metavar = 'PATH', default = argparse.SUPPRESS,
                        help = 'location of the SnpEff installation directory. Will override MiModD config settings if provided.')
p_snpeff_genomes.add_argument('-o', '--ofile', metavar = 'OFILE', dest = 'output', default = argparse.SUPPRESS,
                        help = 'redirect the output to the specified file (default: stdout)')
p_snpeff_genomes.set_defaults(module = 'variant_annotation', func = ['get_installed_snpeff_genomes'])

# ++++++++++++ map +++++++++++++++
p_cm = subparsers.add_parser('map',
                             help='perform a linkage analysis between a selected phenotype and identified variants')
p_cm.add_argument('mode', metavar='analysis_mode', help='specify "SVD" for Simple Variant Density analysis or "VAF" for Variant Allele Frequency analysis.')
p_cm.add_argument('ifile', metavar='input_file', help='valid input files are VCF files or per-variant report files (as generated by this tool with the "-t" option or by the CloudMap Hawaiian Variant Density Mapping tool).')
p_cm.add_argument('-o', '--ofile', default=argparse.SUPPRESS, help='redirect the binned variant counts to this file (default: stdout).')
p_cm.add_argument('-q', '--quiet', action = 'store_true', default = False, help = 'suppress warning messages about plotting problems.')
ana_group = p_cm.add_argument_group('analysis control')
ana_group.add_argument('-b', '--bin-sizes', metavar='SIZE', nargs='+', default=argparse.SUPPRESS, help='list of bin sizes to be used for histogram plots and linkage reports (default: 1Mb and 500Kb)')
ana_group.add_argument('--no-normalize', dest='normalize_hist', action='store_false', help='do not normalize binned counts data (and histograms)')
vaf_group = p_cm.add_argument_group('VAF mode-specific options')
vaf_group.add_argument('-m', '--mapping-sample', metavar='sample_name', help='name of the sample (as appearing in the input vcf file) for which variants should be mapped')
vaf_group.add_argument('-r', '--related-parent', metavar='parent_name', help='name of the sample to provide related parent strain (mutagenesis strain) variants for the analysis in Variant Allele Frequency (VAF) mode.')
vaf_group.add_argument('-u', '--unrelated-parent', metavar='parent_name', help='name of the sample to provide unrelated parent strain (mapping strain) variants for the analysis in Variant Allele Frequency (VAF) mode.')
vaf_group.add_argument('-i', '--infer', '--infer-missing', dest='infer_missing_parent', action='store_true',
                  default=argparse.SUPPRESS, help='if variant data for either the related or the unrelated parent strain is not provided, the tool can try to infer the alleles present in that parent from the allele spectrum found in the mapping sample. Use with caution on carefully filtered variant lists only!')
compat_group = p_cm.add_argument_group('file format and compatibility options')
compat_group.add_argument('-t', '--text-file', default=argparse.SUPPRESS, help='generate text-based output for every variant position and save it to the specified file. This file can be used as input during later runs of the tool, which will speed up replotting.')
compat_group.add_argument('-s', '--seqdict-file', default=argparse.SUPPRESS, help='overwrite contig information (chromosome names and sizes) in the input file with that found in SEQDICT_FILE (which must be a CloudMap-style sequence dictionary file). Useful for input files without contig information, i.e., never necessary with MiModD-generated input.')
compat_group.add_argument('--cloudmap', dest='cloudmap_mode', action='store_true', default=argparse.SUPPRESS, help='generate valid input for the original CloudMap Mapping tools and save it to the text output file specified by the "-t" option.')
plot_group = p_cm.add_argument_group('general plotting options')
plot_group.add_argument('-p', '--plot-file', metavar='FILE', default=argparse.SUPPRESS, help='generate graphical output and store it in the given file (default: no graphical output)')
plot_group.add_argument('--fit-width', action='store_true', default=argparse.SUPPRESS, help = "do not autoscale x-axes to size of largest contig")
scatter_group = p_cm.add_argument_group('scatter plot parameters')
scatter_group.add_argument('--no-scatter', action='store_true', default=argparse.SUPPRESS, help='do not produce scatter plots of observed segregation rates; just plot histograms')
scatter_group.add_argument('-l', '--loess-span', metavar='FLOAT', type=float, default=argparse.SUPPRESS, help='span parameter for the Loess regression line through the linkage data (default: 0.1, specify 0 to skip calculation)')
scatter_group.add_argument('--ylim-scatter', metavar='FLOAT', type=float, default=argparse.SUPPRESS, help = 'upper limit for scatter plot y-axis (default: 1)')  
scatter_group.add_argument('-c', '--points-color', metavar='COLOR', default=argparse.SUPPRESS, help='color for scatter plot data points (default: gray27)')
scatter_group.add_argument('-k', '--loess-color', metavar='COLOR', default=argparse.SUPPRESS, help='color for regression line through scatter plot data (default: red)')
hist_group = p_cm.add_argument_group('histogram plot parameters')
hist_group.add_argument('--no-hist', action='store_true', default=argparse.SUPPRESS, help='do not produce linkage histogram plots; only generate scatter plots')
hist_group.add_argument('--ylim-hist', metavar='INT', type=int, default=argparse.SUPPRESS, help='upper limit for histogram plot y-axis (default: auto)')   
hist_group.add_argument('--hist-colors', nargs='+', metavar='COLOR', default=argparse.SUPPRESS, help='list of colors to be used for plotting histogram bars of different width (default: darkgrey and red)')
p_cm.set_defaults(module='cloudmap', func=['delegate'])


def parse (argv=None):
    args = parser.parse_args(argv)
    if not 'func' in args:
        if 'version' in args:
            if 'quiet' in args:
                print (__version__)
            else:
                print (terms)
        else:
            args = parser.parse_args(['--help'])
    elif 'module' in args:
        module = importlib.import_module('MiModD.'+args.module)

        funcs = [getattr(module, f) for f in args.func]
        del args.func, args.module
        args = vars(args)

        result = funcs[-1](**args)

        for f in funcs[-2::-1]:
            result = f(result)


if __name__ == '__main__':
    parse()
