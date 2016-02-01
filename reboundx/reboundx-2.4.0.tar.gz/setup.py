try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension
from codecs import open
import os
import inspect
import sys 

import sysconfig
suffix = sysconfig.get_config_var('EXT_SUFFIX')
if suffix is None:
    suffix = ".so"

try:
    import rebound
except ImportError:
    print("You must first install REBOUND.  See http://rebound.readthedocs.org/en/latest/python_quickstart.html")
    sys.exit(1)

from distutils.version import LooseVersion
if LooseVersion(rebound.__version__) < LooseVersion("2.12.1"): # Only after 2.12.1 can you link to librebound.so 
    print("REBOUNDx requires REBOUND version > 2.12.1.  Please upgrade.  See 5.3 in http://rebound.readthedocs.org/en/latest/python_quickstart.html")
    sys.exit(1)

rebdir = os.path.dirname(inspect.getfile(rebound))

extra_link_args=[]
if sys.platform == 'darwin':
    from distutils import sysconfig
    vars = sysconfig.get_config_vars()
    vars['LDSHARED'] = vars['LDSHARED'].replace('-bundle', '-shared')
    extra_link_args=['-Wl,-install_name,@rpath/libreboundx'+suffix]
    extra_link_args.append('-Wl,-rpath,'+rebdir+'/../')

libreboundxmodule = Extension('libreboundx',
                    sources = [ 'src/reboundx.c', 'src/gr.c', 'src/modify_orbits.c', 'src/radiation_forces.c', 'src/rebxtools.c'],
                    include_dirs = ['src', rebdir],
                    library_dirs = [rebdir+'/../'],
                    runtime_library_dirs = [rebdir+'/../'],
                    libraries=['rebound'+suffix[:-3]], #take off .so from the suffix
                    define_macros=[ ('LIBREBOUNDX', None) ],
                    extra_compile_args=['-fstrict-aliasing', '-O3','-std=c99','-march=native', '-fPIC', '-Wpointer-arith'],
                    extra_link_args=extra_link_args,
                    )

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='reboundx',
    version='2.4.0',
    description='A library for including additional forces in REBOUND',
    long_description=long_description,
    url='http://github.com/dtamayo/reboundx',
    author='Daniel Tamayo',
    author_email='tamayo.daniel@gmail.com',
    license='GPL',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Scientific/Engineering :: Astronomy',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='astronomy astrophysics nbody integrator',
    packages=['reboundx'],
    #install_requires=['rebound>=2.12.0'],
    tests_require=["numpy","matplotlib"],
    test_suite="reboundx.test",
    ext_modules = [libreboundxmodule],
    zip_safe=False)
