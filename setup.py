from distutils.core import setup
import os.path
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name = 'TikTokApi',         
  packages = ['TikTokApi'], 
  version = '3.4.3',
  license='MIT',       
  description = 'The Unofficial TikTok API Wrapper in Python 3.',   
  author = 'David Teather',                   
  author_email = 'contact.davidteather@gmail.com',     
  url = 'https://github.com/davidteather/tiktok-api',
  long_description=long_description,
  long_description_content_type="text/markdown",  
  download_url = 'https://github.com/davidteather/TikTok-Api/tarball/master', 
  keywords = ['tiktok', 'python3', 'api', 'unofficial', 'tiktok-api', 'tiktok api'], 
  install_requires=[
          'requests',
          'selenium',
          'pyppeteer'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3.5', 
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'
  ],
)
