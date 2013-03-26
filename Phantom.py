#!/usr/bin/env python
# Author: Richard Osterloh <richard.osterloh@gmail.com>

# Check needed software dependencies to nudge users to fix their setup
import sys
if sys.version_info < (2, 5):
    print "Sorry, requires Python 2.5, 2.6 or 2.7."
    sys.exit(1)

try:
    import Cheetah
    if Cheetah.Version[0] != '2':
        raise ValueError
except ValueError:
    print "Sorry, requires Python module Cheetah 2.1.0 or newer."
    sys.exit(1)
except:
    print "The Python module Cheetah is required"
    sys.exit(1)

# We only need this for compiling an EXE and I will just always do that on 2.6+
if sys.hexversion >= 0x020600F0:
    from multiprocessing import freeze_support

import os
import threading
import time
import signal
import traceback
import getopt

import phantom

from phantom import logger
from phantom.version import PHANTOM_VERSION

import ConfigObj

signal.signal(signal.SIGINT, sickbeard.sig_handler)
signal.signal(signal.SIGTERM, sickbeard.sig_handler)


def daemonize():
    """
    Fork off as a daemon
    """

    # Make a non-session-leader child process
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))

    os.setsid()  # @UndefinedVariable - only available in UNIX

    # Make sure I can read my own files and shut out others
    prev = os.umask(0)
    os.umask(prev and int('077', 8))

    # Make the child a session-leader by detaching from the terminal
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))

    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())

    if sickbeard.CREATEPID:
        pid = str(os.getpid())
        logger.log(u"Writing PID " + pid + " to " + str(sickbeard.PIDFILE))
        file(sickbeard.PIDFILE, 'w').write("%s\n" % pid)


def main():
    
    # do some preliminary stuff
    sickbeard.MY_FULLNAME = os.path.normpath(os.path.abspath(__file__))
    sickbeard.MY_NAME = os.path.basename(sickbeard.MY_FULLNAME)
    sickbeard.PROG_DIR = os.path.dirname(sickbeard.MY_FULLNAME)
    sickbeard.DATA_DIR = sickbeard.PROG_DIR
    sickbeard.MY_ARGS = sys.argv[1:]
    sickbeard.CREATEPID = False
    sickbeard.DAEMON = False

    # Need console logging for SickBeard.py and SickBeard-console.exe
    consoleLogging = (not hasattr(sys, "frozen")) or (sickbeard.MY_NAME.lower().find('-console') > 0)

    # Rename the main thread
    threading.currentThread().name = "MAIN"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "qfdp::", ['quiet', 'forceupdate', 'port=', 'daemon', 'noresize', 'pidfile=', 'nolaunch', 'config=', 'datadir='])
    except getopt.GetoptError:
        print "Available Options: --quiet, --forceupdate, --port, --daemon, --noresize, --pidfile, --nolaunch, --config, --datadir"
        sys.exit()

    forceUpdate = False
    forcedPort = None
    noLaunch = False

    for o, a in opts:
        # For now we'll just silence the logging
        if o in ('-q', '--quiet'):
            consoleLogging = False

        # Should we update (from tvdb) all shows in the DB right away?
        if o in ('-f', '--forceupdate'):
            forceUpdate = True

        # Suppress launching web browser
        # Needed for OSes without default browser assigned
        # Prevent duplicate browser window when restarting in the app
        if o in ('--nolaunch',):
            noLaunch = True

        # Override default/configured port
        if o in ('-p', '--port'):
            forcedPort = int(a)

        # Run as a daemon
        if o in ('-d', '--daemon'):
            if sys.platform == 'win32':
                print "Daemonize not supported under Windows, starting normally"
            else:
                consoleLogging = False
                sickbeard.DAEMON = True

        # Prevent resizing of the banner/posters even if PIL is installed
        if o in ('--noresize',):
            sickbeard.NO_RESIZE = True

        # Specify folder to load the config file from
        if o in ('--config',):
            sickbeard.CONFIG_FILE = os.path.abspath(a)

        # Specify folder to use as the data dir
        if o in ('--datadir',):
            sickbeard.DATA_DIR = os.path.abspath(a)

        # Write a pidfile if requested
        if o in ('--pidfile',):
            sickbeard.PIDFILE = str(a)

            # If the pidfile already exists, sickbeard may still be running, so exit
            if os.path.exists(sickbeard.PIDFILE):
                sys.exit("PID file '" + sickbeard.PIDFILE + "' already exists. Exiting.")

            # The pidfile is only useful in daemon mode, make sure we can write the file properly
            if sickbeard.DAEMON:
                sickbeard.CREATEPID = True
                try:
                    file(sickbeard.PIDFILE, 'w').write("pid\n")
                except IOError, e:
                    raise SystemExit("Unable to write PID file: %s [%d]" % (e.strerror, e.errno))
            else:
                logger.log(u"Not running in daemon mode. PID file creation disabled.")

    # If they don't specify a config file then put it in the data dir
    if not sickbeard.CONFIG_FILE:
        sickbeard.CONFIG_FILE = os.path.join(sickbeard.DATA_DIR, "config.ini")

    # Make sure that we can create the data dir
    if not os.access(sickbeard.DATA_DIR, os.F_OK):
        try:
            os.makedirs(sickbeard.DATA_DIR, 0744)
        except os.error, e:
            raise SystemExit("Unable to create datadir '" + sickbeard.DATA_DIR + "'")

    # Make sure we can write to the data dir
    if not os.access(sickbeard.DATA_DIR, os.W_OK):
        raise SystemExit("Datadir must be writeable '" + sickbeard.DATA_DIR + "'")

    # Make sure we can write to the config file
    if not os.access(sickbeard.CONFIG_FILE, os.W_OK):
        if os.path.isfile(sickbeard.CONFIG_FILE):
            raise SystemExit("Config file '" + sickbeard.CONFIG_FILE + "' must be writeable.")
        elif not os.access(os.path.dirname(sickbeard.CONFIG_FILE), os.W_OK):
            raise SystemExit("Config file root dir '" + os.path.dirname(sickbeard.CONFIG_FILE) + "' must be writeable.")

    os.chdir(sickbeard.DATA_DIR)

    if consoleLogging:
        print "Starting up Sick Beard " + SICKBEARD_VERSION + " from " + sickbeard.CONFIG_FILE

    # Load the config and publish it to the sickbeard package
    if not os.path.isfile(sickbeard.CONFIG_FILE):
        logger.log(u"Unable to find '" + sickbeard.CONFIG_FILE + "' , all settings will be default!", logger.ERROR)

    sickbeard.CFG = ConfigObj(sickbeard.CONFIG_FILE)

    # Initialize the config and our threads
    sickbeard.initialize(consoleLogging=consoleLogging)

    sickbeard.showList = []

    if sickbeard.DAEMON:
        daemonize()

    # Use this PID for everything
    sickbeard.PID = os.getpid()

    if forcedPort:
        logger.log(u"Forcing web server to port " + str(forcedPort))
        startPort = forcedPort
    else:
        startPort = sickbeard.WEB_PORT

    if sickbeard.WEB_LOG:
        log_dir = sickbeard.LOG_DIR
    else:
        log_dir = None

    # sickbeard.WEB_HOST is available as a configuration value in various
    # places but is not configurable. It is supported here for historic reasons.
    if sickbeard.WEB_HOST and sickbeard.WEB_HOST != '0.0.0.0':
        webhost = sickbeard.WEB_HOST
    else:
        if sickbeard.WEB_IPV6:
            webhost = '::'
        else:
            webhost = '0.0.0.0'

    try:
        initWebServer({
                      'port': startPort,
                      'host': webhost,
                      'data_root': os.path.join(sickbeard.PROG_DIR, 'data'),
                      'web_root': sickbeard.WEB_ROOT,
                      'log_dir': log_dir,
                      'username': sickbeard.WEB_USERNAME,
                      'password': sickbeard.WEB_PASSWORD,
                      'enable_https': sickbeard.ENABLE_HTTPS,
                      'https_cert': sickbeard.HTTPS_CERT,
                      'https_key': sickbeard.HTTPS_KEY,
                      })
    except IOError:
        logger.log(u"Unable to start web server, is something else running on port %d?" % startPort, logger.ERROR)
        if sickbeard.LAUNCH_BROWSER and not sickbeard.DAEMON:
            logger.log(u"Launching browser and exiting", logger.ERROR)
            sickbeard.launchBrowser(startPort)
        sys.exit()

    # Build from the DB to start with
    logger.log(u"Loading initial show list")
    loadShowsFromDB()

    # Fire up all our threads
    sickbeard.start()

    # Launch browser if we're supposed to
    if sickbeard.LAUNCH_BROWSER and not noLaunch and not sickbeard.DAEMON:
        sickbeard.launchBrowser(startPort)

    # Start an update if we're supposed to
    if forceUpdate:
        sickbeard.showUpdateScheduler.action.run(force=True)  # @UndefinedVariable

    # Stay alive while my threads do the work
    while (True):

        if sickbeard.invoked_command:
            sickbeard.invoked_command()
            sickbeard.invoked_command = None

        time.sleep(1)

    return

if __name__ == "__main__":
    if sys.hexversion >= 0x020600F0:
        freeze_support()
    main()