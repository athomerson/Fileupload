from setuptools import setup, find_packages
import os

version = '1.0'

tests_require = [
    'plone.app.testing>=4.2.4',  # we need ROBOT_TEST_LEVEL
    'mock',
    ]

setup(name='collective.widget.fileupload',
      version=version,
      description="Plone integration of the Blueimp JQuery File Upload",
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Allen Thomerson',
      author_email='athomerson@inspirednetsolutions.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.widget'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'z3c.form',
        'setuptools',
        'plone.z3cform',
        'plone.namedfile',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
