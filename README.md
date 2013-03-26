Phantom
=========

* This project is still in development so there may be bugs*

Phantom is a client server application for hardware testing. It is designed to be as smart as possible interrogating the client on connection and creating the UI dynamically.

Dependencies
------------

Phantom depends on a couple of python modules to do its job. Those are listed in requirements.txt and can be
installed using `pip`:

    pip install -r requirements.txt

Phantom makes use of the following projects:

* [Pyro4][pyro]
* [ConfigObj]][configobj]
* [PySerial][pyserial]

[pyro]: http://pythonhosted.org/Pyro4/
[configobj]: http://www.voidspace.org.uk/python/configobj.html
[pyserial]: http://pyserial.sourceforge.net/

-Richard Osterloh, March 2013