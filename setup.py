from distutils.core import setup
setup(
  name = 'TikTok-Api',         # How you named your package folder (MyLib)
  packages = ['TikTok-Api'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'The Unoffical TikTOK API Wrapper in Python 3.',   # Give a short description about your library
  author = 'David Teather',                   # Type in your name
  author_email = 'dteather0@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/davidteather/tiktok-api',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['tiktok', 'python3', 'api', 'unofficial', 'tiktok-api'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests',
          'selenium',
          'browsermob-proxy',
          'psutil'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.7'
  ],
)