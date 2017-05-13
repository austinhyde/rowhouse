from distutils.core import setup

VERSION = '1.0.3'

setup(
  name='rowhouse',
  packages=['rowhouse'],
  version=VERSION,
  description='A SQLAlchemy wrapper that stays out of your way',
  author='Austin Hyde',
  author_email='austin109@gmail.com',
  url='https://github.com/austinhyde/rowhouse',
  download_url='https://github.com/austinhyde/rowhouse/archive/%s.tar.gz' % VERSION,
  keywords=['database', 'sql'],
  classifiers=['Topic :: Database'],
  install_requires=['sqlalchemy~=1.1.4']
)
