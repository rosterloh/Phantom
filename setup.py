# Phantom setup.py script
from distutils.core import setup

setup(
    name='Phantom',
    version='0.0.1',
    url='https://github.com/rosterloh/Phantom',
    description='Phantom is a client server application for hardware testing',
    long_description=open('README.md').read(),
    author='Richard Osterloh',
    author_email='richard.osterloh@gmail.com',
    license='LICENCE',
    packages=['phantom'],
    install_requires=['pyro', 'configobj', 'pyserial']
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        #'Development Status :: 5 - Production/Stable',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
