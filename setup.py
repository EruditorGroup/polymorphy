from setuptools import setup

setup(name='polymorphy',
      version='0.1',
      description='Regular expressions for russian morphology',
      url='https://github.com/EruditorGroup/polymorphy',
      author='Elia Schelokov',
      author_email='thaumant@gmail.com',
      license='MIT',
      packages=['polymorphy'],
      package_data={'polymorphy': ['dsl.ebnf']},
      zip_safe=False,
      install_requires=[
          'pymorphy2',
          'lark-parser',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Text Processing :: Linguistic',
          'Natural Language :: Russian',
      ])