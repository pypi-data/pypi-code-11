from gnomic.models import Mutation, Fusion, Plasmid, Feature, Organism, Accession, Type, FeatureTree
from gnomic.grammar import GnomicSemantics


class DefaultSemantics(GnomicSemantics):
    def __init__(self,
                 organisms=None,
                 types=None):
        self._organisms = {} if organisms is None else Organism.map(organisms)
        self._types = {} if types is None else Type.map(types)

    def FUSION(self, ast):
        return Fusion(*ast)

    def ORGANISM(self, name):
        try:
            return self._organisms[name]
        except KeyError:
            self._organisms[name] = organism = Organism(name)
            return organism

    def BINARY_VARIANT(self, variant):
        if variant == '+':
            return 'wild-type'
        else:
            return 'mutant'

    def insertion(self, ast):
        return Mutation(None, ast.new, marker=ast.marker)

    def replacement(self, ast):
        return Mutation(ast.old,
                        ast.new,
                        marker=ast.marker,
                        multiple=ast.op == '>>')

    def deletion(self, ast):
        return Mutation(ast.old, None, marker=ast.marker)

    def ACCESSION(self, ast):
        return Accession(ast['id'], ast['db'])

    def PLASMID(self, ast):
        return Plasmid(ast.name, ast.contents, marker=ast.marker)

    def PHENE(self, ast):
        return self.FEATURE(ast, default_type='phene')

    def FEATURE(self, ast, default_type=None):
        if ast.type or default_type:
            name = ast.type or default_type
            try:
                type = self._types[name]
            except KeyError:
                self._types[name] = type = Type(name)
        else:
            type = None

        return Feature(ast.name, type,
                       accession=ast.accession,
                       organism=ast.organism,
                       variant=', '.join(ast.variant) if isinstance(ast.variant, list) else ast.variant,
                       range=ast.range)