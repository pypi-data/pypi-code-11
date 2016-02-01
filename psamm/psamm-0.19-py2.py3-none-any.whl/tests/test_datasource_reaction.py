#!/usr/bin/env python
# This file is part of PSAMM.
#
# PSAMM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PSAMM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PSAMM.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2015  Jon Lund Steffensen <jon_steffensen@uri.edu>

import unittest
from decimal import Decimal

from psamm.reaction import Reaction, Compound, Direction
from psamm.datasource import reaction


class TestDefaultReactionParser(unittest.TestCase):
    def test_reaction_parse(self):
        r = reaction.parse_reaction(
            '|H2O| + |PPi| => (2) |Phosphate| + (2) |H+|')
        self.assertEqual(r, Reaction(
            Direction.Forward, [(Compound('H2O'), 1), (Compound('PPi'), 1)],
            [(Compound('Phosphate'), 2), (Compound('H+'), 2)]))

    def test_reaction_parse_with_decimal(self):
        r = reaction.parse_reaction('|H2| + (0.5) |O2| => |H2O|')
        self.assertEqual(r, Reaction(
            Direction.Forward,
            [(Compound('H2'), 1), (Compound('O2'), Decimal('0.5'))],
            [(Compound('H2O'), 1)]))

    def test_reaction_parse_with_compartment(self):
        r = reaction.parse_reaction('(2) |H2| + |O2| => (2) |H2O[e]|')
        self.assertEqual(r, Reaction(
            Direction.Forward, [(Compound('H2'), 2), (Compound('O2'), 1)],
            [(Compound('H2O', compartment='e'), 2)]))

    def test_reaction_parse_with_multichar_compartment(self):
        r = reaction.parse_reaction(
            '(2) |H2[C_c]| + |O2[C_c]| => (2) |H2O[C_e]|')
        self.assertEqual(r, Reaction(
            Direction.Forward,
            [(Compound('H2', compartment='C_c'), 2),
             (Compound('O2', compartment='C_c'), 1)],
            [(Compound('H2O', compartment='C_e'), 2)]))

    def test_reaction_parse_raw_compound_id(self):
        r = reaction.parse_reaction('(2) cpd00001 => cpd00002')
        self.assertEqual(r, Reaction(
            Direction.Forward, [(Compound('cpd00001'), 2)],
            [(Compound('cpd00002'), 1)]))

    def test_reaction_parse_raw_compound_id_with_typo(self):
        r = reaction.parse_reaction('(2) cpd00001 => cdp00002')
        self.assertEqual(r, Reaction(
            Direction.Forward, [(Compound('cpd00001'), 2)],
            [(Compound('cdp00002'), 1)]))

    def test_reaction_parse_raw_compound_id_in_compartment(self):
        r = reaction.parse_reaction('(2) cpd00001 => cpd00002[e]')
        self.assertEqual(r, Reaction(
            Direction.Forward, [(Compound('cpd00001'), 2)],
            [(Compound('cpd00002', 'e'), 1)]))

    def test_reaction_parse_bidirectional(self):
        r = reaction.parse_reaction('(1) |cpd1| <=> (2) cpd2 + |cpd3|')
        self.assertEqual(r, Reaction(
            Direction.Both, [(Compound('cpd1'), 1)],
            [(Compound('cpd2'), 2), (Compound('cpd3'), 1)]))

    def test_reaction_str(self):
        r = Reaction(Direction.Reverse, [(Compound('H2O'), 2)],
                     [(Compound('H2'), 2), (Compound('O2'), 1)])
        self.assertEqual(str(r), '(2) |H2O| <= (2) |H2| + |O2|')


if __name__ == '__main__':
    unittest.main()
