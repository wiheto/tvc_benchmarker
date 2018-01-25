from setuptools import setup,find_packages
setup(name='tvc_benchmarker',
      version='1.0',
      description='tvc_benchmarker is a package that compares different time-varying functoinal connectivity methods against eachother (neuroimaging/fmri).',
      packages = ['tvc_benchmarker'],
      package_data={'':['./tvc_benchmarker/data/']},
      include_package_data = True,
      author='William Hedley Thompson',
      url='https://www.github.com/wiheto/tvc_benchmarker',
      )
