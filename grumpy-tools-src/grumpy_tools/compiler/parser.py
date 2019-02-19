# coding: utf-8
"""
Grumpy uses `pythonparser` as its AST parser. This module contains an augmented
(extended) parser from it, letting us to accept special Grumpy-only syntax, like
the `import '__go__/...'` syntax for importing Go code.
"""
import logging

import pythonparser.parser
from pythonparser.parser import Parser, Seq, Loc, Opt, Tok, List, Alt, Rule, action
from pythonparser import ast

logger = logging.getLogger(__name__)

PYTHNOPARSER_PATCHED = False


def patch_pythonparser():
    global PYTHNOPARSER_PATCHED
    if PYTHNOPARSER_PATCHED:
        return False

    logger.info('Monkeypatching pythonparser.parser.Parser with Grumpy extensions')
    pythonparser.parser.Parser = GrumpyParser
    PYTHNOPARSER_PATCHED = True
    return True


class GrumpyParser(Parser):
    # From: https://github.com/google/grumpy/commit/9d80504e8d42c4a03ece9ed983b0ca160d170969#diff-c46e216e8423951b5f41dde139575b68R1038
    @action(Rule("atom_5"))
    def import_from_7(self, string):
        return (None, 0), (string.loc, string.s)

    # From: https://github.com/google/grumpy/commit/9d80504e8d42c4a03ece9ed983b0ca160d170969#diff-c46e216e8423951b5f41dde139575b68R1046
    @action(Seq(Loc("from"), Alt(Parser.import_from_3, Parser.import_from_4, import_from_7),
                Loc("import"), Alt(Parser.import_from_5,
                                   Seq(Loc("("), Rule("import_as_names"), Loc(")")),
                                   Parser.import_from_6)))
    def import_from(self, from_loc, module_name, import_loc, names):
        """
        (2.6, 2.7)
        import_from: ('from' ('.'* dotted_name | '.'+)
                    'import' ('*' | '(' import_as_names ')' | import_as_names))
        (3.0-)
        # note below: the ('.' | '...') is necessary because '...' is tokenized as ELLIPSIS
        import_from: ('from' (('.' | '...')* dotted_name | ('.' | '...')+)
                    'import' ('*' | '(' import_as_names ')' | import_as_names))
        """
        (dots_loc, dots_count), dotted_name_opt = module_name
        module_loc = module = None
        if dotted_name_opt:
            module_loc, module = dotted_name_opt
        lparen_loc, names, rparen_loc = names
        loc = from_loc.join(names[-1].loc)
        if rparen_loc:
            loc = loc.join(rparen_loc)

        if module == "__future__":
            self.add_flags([x.name for x in names])

        return ast.ImportFrom(names=names, module=module, level=dots_count,
                              keyword_loc=from_loc, dots_loc=dots_loc, module_loc=module_loc,
                              import_loc=import_loc, lparen_loc=lparen_loc, rparen_loc=rparen_loc,
                              loc=loc)

    @action(Seq(Rule("atom_5"), Opt(Seq(Loc("as"), Tok("ident")))))
    def str_as_name(self, string, as_name_opt):
        asname_name = asname_loc = as_loc = None
        loc = string.loc
        if as_name_opt:
            as_loc, asname = as_name_opt
            asname_name = asname.value
            asname_loc = asname.loc
            loc = loc.join(asname.loc)
        return ast.alias(name=string.s, asname=asname_name,
                         loc=loc, name_loc=string.loc, as_loc=as_loc, asname_loc=asname_loc)

    dotted_as_names = List(Alt(Rule("dotted_as_name"), Rule("str_as_name")), ",", trailing=False)
