"""
Script for creating all of the binaries that are released for the current
platform.
"""

import os
import sys

oracleHomes = os.environ["CX_ORACLE_HOMES"].split(",")
origPath = os.environ["PATH"]

for oracleHome in oracleHomes:
    if sys.platform == "win32":
        os.environ["PATH"] = oracleHome + os.pathsep + origPath
    else:
        os.environ["ORACLE_HOME"] = oracleHome
    if sys.platform == "win32":
        subCommand = "bdist_msi"
        subCommandArgs = ""
    else:
        subCommand = "bdist_rpm"
        subCommandArgs = "--no-autoreq --python %s" % sys.executable
    command = "%s setup.py %s %s" % \
            (sys.executable, subCommand, subCommandArgs)
    messageFragment = "%s for home %s" % (subCommand, oracleHome)
    sys.stdout.write("Executing %s.\n" % messageFragment)
    sys.stdout.write("Running command %s\n" % command)
    if os.system(command) != 0:
        msg = "Stopping. execution of %s failed.\n" % messageFragment
        sys.exit(msg)

