from distutils.core import setup
import os.path

try:
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, "README.md"), encoding="utf-8").read()
    with open(os.path.join(here, "requirements/base.txt"), encoding="utf-8") as f:
        required = [l.strip("\n") for l in f if l.strip("\n") and not l.startswith("#")]
except IOError:
    required = []
    README = ""

setup(
  name = 'TikTokApi',         
  packages = ['TikTokApi'],   
  version = '2.1.4',      
  license='MIT',        
  description = 'The Unoffical TikTok API Wrapper in Python 3.',   
  author = 'David Teather',                   
  author_email = 'contact.davidteather@gmail.com',     
  url = 'https://github.com/davidteather/tiktok-api',
  long_description=README,
  long_description_content_type="text/markdown",  
  download_url = 'https://github.com/davidteather/TikTok-Api/tarball/master', 
  keywords = ['tiktok', 'python3', 'api', 'unofficial', 'tiktok-api'], 
  install_requires=[
          'requests',
          'selenium',
          'browsermob-proxy',
          'psutil'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3.7'
  ],
)