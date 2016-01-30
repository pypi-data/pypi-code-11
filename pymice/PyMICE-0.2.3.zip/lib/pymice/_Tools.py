#!/usr/bin/env python
# encoding: utf-8
###############################################################################
#                                                                             #
#    PyMICE library                                                           #
#                                                                             #
#    Copyright (C) 2012-2016 Jakub M. Kowalski, S. Łęski (Laboratory of       #
#    Neuroinformatics; Nencki Institute of Experimental Biology of Polish     #
#    Academy of Sciences)                                                     #
#                                                                             #
#    This software is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This software is distributed in the hope that it will be useful,         #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this software.  If not, see http://www.gnu.org/licenses/.     #
#                                                                             #
###############################################################################

import sys
import os
import shutil
from datetime import datetime
import time
import warnings
from math import modf
from operator import attrgetter

import pytz

try:
  from itertools import imap

except ImportError:
  imap = map

#from numbers import Number
#import numpy as np
#if not issubclass(np.floating, Number):
#  Number.register(np.floating)

from ._FixTimezones import LatticeOrderer


import tempfile
import zipfile
try:
 from urllib import urlretrieve

except ImportError:
  from urllib.request import urlretrieve


if sys.version_info >= (3, 0):
  basestring = str

def timeString(x, tz=None):
  return datetime.fromtimestamp(x, tz).strftime('%Y-%m-%d %H:%M:%S.%f%z')


class PmWarnings(object):
  class PmWarning(Warning):
    """
    A virtual class of PyMICE warnings always to be reported
    - a hook for U{4180-wontfix-issue <http://bugs.python.org/issue4180>}
    """
    pass
  
  class PmDeprecationWarning(DeprecationWarning, PmWarning):
    pass
  
  class PmUserWarning(UserWarning, PmWarning):
    pass

  __initialized__ = False

  def __init__(self):
    if not PmWarnings.__initialized__:
      warnings.filterwarnings('always',
                              category=PmWarnings.PmWarning)
      PmWarnings.__initialized__ = True

    self.enable()

  def disable(self):
    self.enabled = False

  def enable(self):
    self.enabled = True

  def deprecated(self, message, stacklevel=1):
    warnings.warn(message,
                  self.PmDeprecationWarning if self.enabled else DeprecationWarning,
                  stacklevel=stacklevel + 2)

  def warn(self, message, stacklevel=1):
    warnings.warn(message,
                  self.PmUserWarning if self.enabled else UserWarning,
                  stacklevel=stacklevel + 2)


warn = PmWarnings()

# def ensureFloat(x):
#   """
#   Convert x to float if possible.
#
#   Accept ',' used as a decimal mark.
#
#   Convert '' to None.
#   """
#   if isinstance(x, basestring):
#     if x == '':
#       return None
#
#     return float(x.replace(',', '.'))
#
#   if x is not None:
#     return float(x)
#
#
# def ensureInt(x):
#   """
#   Convert x to int if possible.
#
#   Convert '' to None.
#   """
#   if x == '' or x is None:
#     return None
#
#   return int(x)


def hTime(t):
  """
  Convert timestamp t to a human-readible UTC string.
  """
  dec, integer = modf(t)
  return time.strftime("%Y-%m-%d %H:%M:%S" + ('{:01.3f}'.format(dec))[1:],
                       time.gmtime(integer))

EPOCH = datetime(1970,1,1)
#UTC_OFFSET = time.mktime(EPOCH.timetuple())

EPOCH_UTC = datetime(1970, 1, 1, tzinfo=pytz.UTC)

def toTimestampUTC(x):
  return (x - EPOCH_UTC).total_seconds()

def toTimestamp(x):
  return (x - EPOCH).total_seconds()



def toDt(tmp):
  if tmp is None or isinstance(tmp, datetime):
    return tmp

  if isinstance(tmp, (tuple, list)):
    return datetime(*tmp)

  if isinstance(tmp, dict):
    return datetime(**tmp)

  tmp = datetime.fromtimestamp(float(tmp))



def convertTime(tStr, tzinfo=None):
  """
  Converts time to timestamp - no timezones assumed.

  >>> convertTime('1970-01-01 12:34:56.7')
  datetime.datetime(1970, 1, 1, 12, 34, 56, 700000)
  """
  tSplit = tStr.replace('-', ' ').replace(':', ' ').split()
  args = list(imap(int, tSplit[:5]))
  secs = int(float(tSplit[5]) * 1000000) if len(tSplit) == 6 else 0
  args.extend((secs // 1000000, secs % 1000000, tzinfo))
  return datetime(*args)

def timeToList(tStr):
  date, time = tStr.split()
  tokens = date.split('-') + time.split(':')

  if len(tokens) == 5:
    return map(int, tokens) + [0, 0]

  decimal, seconds = modf(float(tokens[5]))
  #return map(int, tokens[:5] + [seconds, round(decimal * 1000000)])
  return LatticeOrderer.Node(map(int, tokens[:5] + [seconds, round(decimal * 1000000)]))

class timeListList(list):
  def __eq__(self, x):
    return self[0] == x[0]

  def __le__(self, x):
    return self[0] <= x[0]

  def __ge__(self, x):
    return self[0] >= x[0]

  def __ne__(self, x):
    return self[0] != x[0]

  def __lt__(self, x):
    return self[0] < x[0]

  def __gt__(self, x):
    return self[0] > x[0]


class PathZipFile(object):
  """
  A class emulating zipfile.ZipFile behaviour with filesystem directories.
  """
  def __init__(self, path):
    self.__path = path

  def open(self, name, mode='r'):
    fn = os.path.join(self.__path, name)
    return open(fn, mode)


class DataDownloadStdoutReporter(object):
  class DownloadPercentReporter(object):
    def __init__(self, checkpoints):
      self.__checkpoints = iter(checkpoints)
      self.setNextCheckpoint()

    def isAtCheckpoint(self, downloaded):
      return downloaded > self.__checkpoint

    def setNextCheckpoint(self):
      try:
        self.__checkpoint = next(self.__checkpoints)

      except StopIteration:
        self.__checkpoint = float('inf')

    def reportCheckpoint(self):
      print("{:3d}% downloaded".format(self.__checkpoint))

    def reportAtCheckpoint(self, downloaded):
      if self.isAtCheckpoint(downloaded):
        self.reportCheckpoint()
        self.setNextCheckpoint()

    def __call__(self, blockcount, blocksize, totalsize):
      self.reportAtCheckpoint(blockcount * blocksize * 100 // totalsize)

  def warnUnknownDownload(self, download):
    print('Warning: unknown download requested({})'.format(download))

  def reportUnnecessaryFetch(self, dataset):
    print('{} dataset already present'.format(dataset))

  def reportNothingToFetch(self):
    print('All datasets already present.')

  def printManualDownloadInstruction(self, toDownload):
    print('In case the automatic download fails fetch the data manually.')

    for url, files in toDownload.items():
      self.printFileDownloadInstruction(url, files)
    
    print("\n")

  def printFileDownloadInstruction(self, url, files):
    print('\nDownload archive from: {}'.format(url))
    print('then extract the following files:')
    for filename in files:
      print('- {}'.format(filename))

  def reportDownloadStart(self, url):
    print('downloading data from {}'.format(url))

  def getReportHook(self):
    return self.DownloadPercentReporter([1, 25, 50, 75])

  def reportDownloadEnd(self):
    print('data downloaded')

  def reportFileExtraction(self, filename):
    print('extracting file {}'.format(filename))

  def warnFileSizeMismatch(self, filename, filesize):
    print('Warning: size of extracted file differs')


class DataDownloadDummyReporter(object):
  def __getattribute__(self, attribute):
    def dummyFunction(*args, **kwargs):
      return None

    return dummyFunction


class DataGetter(object):
  DATA = {'C57_AB': {'C57_AB/2012-08-28 13.44.51.zip': 86480,
                     'C57_AB/2012-08-28 15.33.58.zip': 494921,
                     'C57_AB/2012-08-31 11.46.31.zip': 29344,
                     'C57_AB/2012-08-31 11.58.22.zip': 3818445,
                     'C57_AB/timeline.ini': 2894,
                     'C57_AB/COPYING': 697,
                     'C57_AB/LICENSE': 19467,
                    },
          'demo': {'demo.zip': 106091,
                   'COPYING': 540,
                   'LICENSE': 19467,
                   },
         }

  def __init__(self, path, reporter):
    self.setPath(path)
    self._reporter = reporter

  def setPath(self, path):
    if path is None:
      path = os.getcwd()

    self.ensureIsDirectory(path)
    self._path = path

  def ensureIsDirectory(self, path):
    if not os.path.exists(path):
      os.makedirs(path)

    elif not os.path.isdir(path):
      raise OSError("Not a directory: '{}'".format(path))

  def necessaryDataSetsGenerator(self, fetch):
    for dataset in fetch:
      if self.isFetchPossibleAndNecessary(dataset):
        yield dataset

  def isFetchPossibleAndNecessary(self, dataset):
    try:
      files = self.DATA[dataset]

    except KeyError:
      self._reporter.warnUnknownDownload(download)
      return

    if all(self.fileSizeMatches(fn, fs) for (fn, fs) in files.items()):
      self._reporter.reportUnnecessaryFetch(dataset)
      return

    return True

  def fileSizeMatches(self, filename, size):
    path = os.path.join(self._path, filename)
    return os.path.isfile(path) and os.path.getsize(path) == size

  def fetch(self, requested):
    if requested is None:
      requested = sorted(self.DATA.keys())

    elif isinstance(requested, basestring):
      requested = (requested,)

    toFetch = list(self.necessaryDataSetsGenerator(requested))

    if not toFetch:
      self._reporter.reportNothingToFetch()
      return

    self.fetchDatasets(toFetch)

  def fetchDatasets(self, datasets):
    for dataset in datasets:
      self.fetchDataset(dataset)


class ModuleDataGetter(DataGetter):
  PATHS = {'C57_AB': ['tutorial/C57_AB',],
           'demo': ['tutorial/demo.zip',
                    'tutorial/LICENSE',
                    'tutorial/COPYING',],
           }



  def fetchDataset(self, dataset):
    for path in self.PATHS[dataset]:
      self.fetchDir(path)

  def fetchDir(self, path):
    src = os.path.join(os.path.dirname(__file__), 'data', path)
    self.copyFiles(src, self._path)

  def copyFiles(self, src, dst):
    if os.path.isdir(src):
      path = os.path.join(dst, os.path.basename(src))
      if not os.path.exists(path):
        os.mkdir(path)

      for item in os.listdir(src):
        self.copyFiles(os.path.join(src, item),
                       path)

    else:
      shutil.copy(src, dst)


class DataDownloader(DataGetter):
  URLS = {'C57_AB': 'https://www.dropbox.com/s/0o5faojp14llalm/C57_AB.zip?dl=1',
          'demo': 'https://www.dropbox.com/s/yo2fpxcuardo3ji/demo.zip?dl=1',
          }

  class TemporaryFileName(object):
    def __enter__(self):
      fh, self.__filename = tempfile.mkstemp(suffix=".zip", prefix="PyMICE_download_tmp_")
      os.close(fh)
      return self.__filename

    def __exit__(self, exc_type, exc_value, traceback):
      os.remove(self.__filename)


  def fetchDatasets(self, toFetch):
    self.printManualDownloadInstruction(toFetch)
    super(DataDownloader, self).fetchDatasets(toFetch)

  def printManualDownloadInstruction(self, downloads):
    toDownload = dict(map(self.getDownloadInfo, downloads))
    self._reporter.printManualDownloadInstruction(toDownload)

  def getDownloadInfo(self, dataset):
    return self.URLS[dataset], sorted(self.DATA[dataset])

  def fetchDataset(self, dataset):
    self.retrieveFiles(self.URLS[dataset],
                       sorted(self.DATA[dataset].items()))

  def retrieveFiles(self, url, files):
    self._reporter.reportDownloadStart(url)
    with self.TemporaryFileName() as filename:
      self.downloadArchive(url, filename)
      self.extractFiles(filename, files)

  def downloadArchive(self, url, filename):
    urlretrieve(url, filename, self._reporter.getReportHook())
    self._reporter.reportDownloadEnd()

  def extractFiles(self, archive, files):
    with zipfile.ZipFile(archive) as zf:
      for filename, filesize in files:
        self.extractFile(zf, filename, filesize)

  def extractFile(self, zipfile, filename, filesize):
    self._reporter.reportFileExtraction(filename)
    zipfile.extract(filename, self._path)
    if os.path.getsize(os.path.join(self._path, filename)) != filesize:
      self._reporter.warnFileSizeMismatch(filename, filesize)


def getTutorialData(path=None, quiet=False, fetch=None):
  """
  Download example dataset(s) used in tutorials.

  :param path: a directory where tutorial data are to be loaded into
               (defaults to working directory)
  :type path: basestring

  :param quiet: a switch disabling stdout output.
  :type quiet: bool

  :param fetch: the datasets to download
  :type fetch: collection(basestring, ...)

  SetUp

  >>> import tempfile
  >>> import os
  >>> _dirname = tempfile.mkdtemp(prefix='.tmp_ToolsDoctests')
  >>> _cwd = os.getcwd()
  >>> os.chdir(_dirname)
  
  >>> getTutorialData(fetch='C57_AB')
  >>> getTutorialData(fetch='C57_AB')
  C57_AB dataset already present
  All datasets already present.
  >>> getTutorialData(fetch='C57_AB', quiet=True)
  >>> getTutorialData()
  C57_AB dataset already present
  >>> getTutorialData()
  C57_AB dataset already present
  demo dataset already present
  All datasets already present.

  TearDown

  >>> os.remove('demo.zip')
  >>> os.remove('COPYING')
  >>> os.remove('LICENSE')
  >>> os.remove('C57_AB/2012-08-28 13.44.51.zip')
  >>> os.remove('C57_AB/2012-08-28 15.33.58.zip')
  >>> os.remove('C57_AB/2012-08-31 11.46.31.zip')
  >>> os.remove('C57_AB/2012-08-31 11.58.22.zip')
  >>> os.remove('C57_AB/timeline.ini')
  >>> os.remove('C57_AB/COPYING')
  >>> os.remove('C57_AB/LICENSE')
  >>> os.rmdir('C57_AB')
  >>> os.chdir(_cwd)
  >>> os.rmdir(_dirname)

  """
  downloader = ModuleDataGetter(path, DataDownloadDummyReporter() if quiet else DataDownloadStdoutReporter())
  downloader.fetch(fetch)








def groupBy(objects, getKey):
  """
  >>> import operator
  >>> output = groupBy([(1, 2), (3, 4), (3, 2), (1, 1), (2, 1, 8)],
  ...                  getKey=operator.itemgetter(1))
  >>> for k in sorted(output):
  ...   print("{} {}".format(k, output[k]))
  1 [(1, 1), (2, 1, 8)]
  2 [(1, 2), (3, 2)]
  4 [(3, 4)]

  >>> output = groupBy([(1, 2), (2, 1), (0, 2), (3, 0), (1, 1), (1, 1)],
  ...                  getKey=lambda x: x[0] + x[1])
  >>> for k in sorted(output):
  ...   print("{} {}".format(k, output[k]))
  2 [(0, 2), (1, 1), (1, 1)]
  3 [(1, 2), (2, 1), (3, 0)]

  >>> groupBy([], getKey=lambda x: x[0] + x[1])
  {}

  >>> output = groupBy([Pair(1, 2), Pair(1, 1), Pair(2, 1)], 'a')
  >>> for k in sorted(output):
  ...   print("{} {}".format(k, output[k]))
  1 [Pair(a=1, b=2), Pair(a=1, b=1)]
  2 [Pair(a=2, b=1)]

  >>> output = groupBy([Pair(1, 2), Pair(1, 1), Pair(2, 1)], ('a', 'b'))
  >>> for k in sorted(output):
  ...   print("{} {}".format(k, output[k]))
  (1, 1) [Pair(a=1, b=1)]
  (1, 2) [Pair(a=1, b=2)]
  (2, 1) [Pair(a=2, b=1)]
  """
  if not hasattr(getKey, '__call__'):
    getKey = attrgetter(getKey) if isinstance(getKey, basestring) else attrgetter(*getKey)

  result = {}
  for o in objects:
    key = getKey(o)
    try:
      result[key].append(o)

    except KeyError:
      result[key] = [o]

  return result

def mergeIntervalsValues(objects, getData, overlap=False, mergeWindow=None):
  if len(objects) == 0:
    return []

  if not hasattr(getData, '__call__'):
    getData = attrgetter(*getData)

  result = []
  data = sorted(map(getData, objects))
  row = data[0]
  lastStart, lastEnd = row[:2]
  assert lastStart <= lastEnd

  lastValue = row[2:]

  for row in data[1:]:
    start, end = row[:2]
    value = row[2:]
    assert overlap or lastEnd <= start
    assert start <= end
    if lastValue == value and (start - lastEnd <= mergeWindow or mergeWindow is None):
      lastEnd = max(end, lastEnd)

    else:
      result.append((lastStart, lastEnd, lastValue))
      lastStart, lastEnd, lastValue = start, end, value

  result.append((lastStart, lastEnd, lastValue))
  return result
