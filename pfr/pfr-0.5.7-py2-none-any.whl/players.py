import datetime
import re
import urlparse

import numpy as np
import pandas as pd
from pyquery import PyQuery as pq

import pfr

__all__ = [
    'Player',
]

yr = datetime.datetime.now().year

@pfr.decorators.memoized
class Player:

    def __init__(self, playerID):
        self.pID = playerID
        self.mainURL = urlparse.urljoin(
            pfr.BASE_URL, '/players/{0[0]}/{0}.htm'
        ).format(self.pID)

    def __eq__(self, other):
        return self.pID == other.pID

    def __hash__(self):
        return hash(self.pID)

    @pfr.decorators.memoized
    def getDoc(self):
        doc = pq(pfr.utils.getHTML(self.mainURL))
        return doc

    @pfr.decorators.memoized
    def name(self):
        doc = self.getDoc()
        name = doc('div#info_box h1:first').text()
        return name

    @pfr.decorators.memoized
    def age(self, year=yr, month=9, day=1):
        doc = self.getDoc()
        span = doc('div#info_box span#necro-birth')
        birthstring = span.attr('data-birth')
        dateargs = re.match(r'(\d{4})\-(\d{2})\-(\d{2})', birthstring).groups()
        dateargs = map(int, dateargs)
        birthDate = datetime.date(*dateargs)
        delta = datetime.date(year=year, month=month, day=day) - birthdate
        age = delta.days / 365.
        return age

    @pfr.decorators.memoized
    def position(self):
        doc = self.getDoc()
        rawText = (doc('div#info_box p')
                   .filter(lambda i,e: 'Position' in e.text_content())
                   .text())
        rawPos = re.search(r'Position: (\S+)', rawText, re.I).group(1)
        allPositions = rawPos.split('-')
        # right now, returning just the primary position for those with
        # multiple positions
        return allPositions[0]

    @pfr.decorators.memoized
    def height(self):
        doc = self.getDoc()
        try:
            rawText = (doc('div#info_box p')
                       .filter(
                           lambda i,e: 'height:' in e.text_content().lower()
                       ).text())
            rawHeight = (re.search(r'Height: (\d\-\d{1,2})', rawText, re.I)
                         .group(1))
        except AttributeError:
            return np.nan
        feet, inches = map(int, rawHeight.split('-'))
        return feet*12 + inches

    @pfr.decorators.memoized
    def weight(self):
        doc = self.getDoc()
        rawText = (doc('div#info_box p')
                   .filter(lambda i,e: 'Weight:' in e.text_content())
                   .text())
        rawWeight = re.search(r'Weight: (\S+)', rawText, re.I).group(1)
        return int(rawWeight)

    @pfr.decorators.memoized
    def hand(self):
        doc = self.getDoc()
        rawText = (doc('div#info_box p')
                   .filter(lambda i,e: 'Position' in e.text_content())
                   .text())
        rawHand = re.search(r'Throws: (\S+)', rawText, re.I).group(1)
        return rawHand[0] # 'L' or 'R'

    @pfr.decorators.memoized
    def pick(self):
        doc = self.getDoc()
        rawDraft = doc('div#info_box > p:first').text()
        m = re.search(r'Drafted .*? round \((\d+).*?overall\)', rawDraft, re.I)
        # if not drafted or taken in supplemental draft, return NaN
        if not m or 'Supplemental' in rawDraft:
            return np.nan
        else:
            return int(m.group(1))

    @pfr.decorators.memoized
    def draftClass(self):
        doc = self.getDoc()
        rawDraft = doc('div#info_box > p:first').text()
        m = re.search(r'Drafted.*?of the (\d{4}) NFL', rawDraft, re.I)
        if not m:
            return np.nan
        else:
            return int(m.group(1))

    @pfr.decorators.memoized
    def draftTeam(self):
        doc = self.getDoc()
        rawDraft = doc('div#info_box > p:first')
        draftStr = pfr.utils.flattenLinks(rawDraft)
        m = re.search(r'Drafted by the (\w{3})', draftStr)
        if not m:
            return np.nan
        else:
            return m.group(1)

    @pfr.decorators.memoized
    def college(self):
        doc = self.getDoc()
        rawText = doc('div#info_box > p:first')
        cleanedText = pfr.utils.flattenLinks(rawText)
        college = re.search(r'College: (\S+)', cleanedText).group(1)
        return college

    @pfr.decorators.memoized
    def highSchool(self):
        doc = self.getDoc()
        rawText = doc('div#info_box > p:first')
        cleanedText = pfr.utils.flattenLinks(rawText)
        hs = re.search(r'High School: (\S{8})', cleanedText).group(1)
        return hs

    @pfr.decorators.memoized
    def av(self, year=yr):
        doc = self.getDoc()
        tables = doc('table[id]').filter(
            lambda i,e: 'AV' in e.text_content()
        )
        # if no AV table, return NaN
        if not tables:
            return np.nan
        # otherwise, extract the AV
        table = tables.eq(0)
        df = pfr.utils.parseTable(table)
        df = df.query('year == @year')
        # if the player has an AV for that year, return it
        # TODO: does this work when player played on two teams? how?
        if not df.empty:
            return df['av'].iloc[0]
        # otherwise, return NaN
        else:
            return np.nan

    @pfr.decorators.memoized
    @pfr.decorators.kindRPB
    def gamelog(self, kind='R', year=None):
        """Gets the career gamelog of the given player.
        :kind: One of 'R', 'P', or 'B' (for regular season, playoffs, or both).
        Case-insensitive; defaults to 'R'.
        :year: The year for which the gamelog should be returned; if None,
        return entire career gamelog. Defaults to None.
        :returns: A DataFrame with the player's career gamelog.
        """
        url = urlparse.urljoin(
            pfr.BASE_URL, '/players/{0[0]}/{0}/gamelog'
        ).format(self.pID)
        doc = pq(pfr.utils.getHTML(url))
        table = doc('#stats') if kind == 'R' else doc('#stats_playoffs')
        df = pfr.utils.parseTable(table)
        if year is not None:
            df = df.query('year == @year')
        return df

    @pfr.decorators.memoized
    @pfr.decorators.kindRPB
    def passing(self, kind='R'):
        """Gets yearly passing stats for the player.

        :kind: One of 'R', 'P', or 'B'. Case-insensitive; defaults to 'R'.
        :returns: Pandas DataFrame with passing stats.
        """
        doc = self.getDoc()
        table = doc('#passing') if kind == 'R' else doc('#passing_playoffs')
        df = pfr.utils.parseTable(table)
        return df

    @pfr.decorators.memoized
    def rushing_and_receiving(self):
        doc = self.getDoc()
        table = doc('#rushing_and_receiving')
        df = pfr.utils.parseTable(table)
        return df
