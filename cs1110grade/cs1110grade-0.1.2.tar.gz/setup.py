from setuptools import setup, find_packages

setup(name='cs1110grade',
      version='0.1.2',
      description='Tools for automated grading of cs1110 assignments.',
      url='https://github.com/fredcallaway/grade.py',
      author='Fred Callaway',
      author_email='fredc@llaway.com',
      license='MIT',
      packages=find_packages(exclude=['grade_template*']),
      scripts=['bin/grade.py'],
      #include_package_data=True,
      zip_safe=False)