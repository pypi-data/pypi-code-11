import platform
import sys
from distutils.core import setup

import os.path

root_dir = os.path.abspath(os.path.join(__file__, os.pardir))
if root_dir not in sys.path:
    sys.path.insert(0, str(root_dir))
import version


setup(name='run-exe',
      version=version.getVersion(),
      description='Run executable file, with option to try as admin on error '
      'on Windows.',
      keywords='process windows administrator launch',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/cfobel/run-exe',
      license='GPL',
      long_description='\n%s\n' % open('README.md', 'rt').read(),
      packages=['run_exe'])
