from distutils.core import setup
setup(
  name = 'TikTokApi',         
  packages = ['TikTokApi'],   
  version = '2.1.2.1',      
  license='MIT',        
  description = 'The Unoffical TikTok API Wrapper in Python 3.',   
  author = 'David Teather',                   
  author_email = 'contact.davidteather@gmail.com',     
  url = 'https://github.com/davidteather/tiktok-api',  
  download_url = 'https://github.com/davidteather/TikTok-Api/archive/V2.1.3.tar.gz', 
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