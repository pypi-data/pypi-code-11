#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'PyBuilder',
        version = '0.11.6',
        description = '''An extensible, easy to use continuous build tool for Python''',
        long_description = '''PyBuilder is a build automation tool for python.

PyBuilder is a software build tool written in pure Python which mainly targets Python applications.
It is based on the concept of dependency based programming but also comes along with powerful plugin mechanism that
allows the construction of build life cycles similar to those known from other famous build tools like Apache Maven.
''',
        author = "Alexander Metzner, Maximilien Riehl, Michael Gruber, Udo Juettner, Marcel Wolf, Arcadiy Ivanov, Valentin Haenel",
        author_email = "alexander.metzner@gmail.com, max@riehl.io, aelgru@gmail.com, udo.juettner@gmail.com, marcel.wolf@me.com, arcadiy@ivanov.biz, valentin@haenel.co",
        license = 'Apache License',
        url = 'http://pybuilder.github.io',
        scripts = ['scripts/pyb'],
        packages = [
            'pybuilder',
            'pybuilder.pluginhelper',
            'pybuilder.plugins',
            'pybuilder.plugins.python'
        ],
        py_modules = [],
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing'
        ],
        entry_points = {
            'console_scripts': ['pyb_ = pybuilder.cli:main']
        },
        data_files = [],
        package_data = {},
        install_requires = [
            'pip>=7.0',
            'tblib',
            'wheel'
        ],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )
