from setuptools import setup, find_packages

setup(
    name='digimat.lp',
    version='0.1.1',
    description='Digimat LanPacket',
    namespace_packages=['digimat'],
    author='Frederic Hess',
    author_email='fhess@splust.ch',
    license='PSF',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'setuptools'
    ],
    dependency_links=[
        ''
    ],
    zip_safe=False)
