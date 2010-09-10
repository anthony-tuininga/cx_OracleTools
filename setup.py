import cx_Freeze
import distutils.util
import distutils.version
import os
import struct
import sys

from distutils.errors import DistutilsSetupError

NAME = "cx_OracleTools"
VERSION = "8.0"

class build_exe(cx_Freeze.build_exe):
    user_options = cx_Freeze.build_exe.user_options + [
            ('cx-logging=', None, 'location of cx_Logging sources'),
            ('cx-oracle=', None, 'location of cx_Oracle sources'),
            ('cx-pygenlib=', None, 'location of cx_PyGenLib sources'),
            ('cx-pyoraclelib=', None, 'location of cx_PyOracleLib sources')
    ]

    def initialize_options(self):
        cx_Freeze.build_exe.initialize_options(self)
        self.cx_logging = None
        self.cx_oracle = None
        self.cx_pygenlib = None
        self.cx_pyoraclelib = None 

    def finalize_options(self):
        cx_Freeze.build_exe.finalize_options(self)
        self.set_source_location("cx_Logging", "trunk")
        self.set_source_location("cx_Oracle", "trunk")
        self.set_source_location("cx_PyGenLib", "trunk")
        self.set_source_location("cx_PyOracleLib", "trunk")
        dirName = "exe.%s-%s-%s" % \
                (distutils.util.get_platform(), sys.version[0:3],
                 oracleVersion)
        self.build_exe = os.path.join(os.path.dirname(self.build_exe), dirName)
        command = self.distribution.get_command_obj("build")
        command.build_exe = self.build_exe
        command = self.distribution.get_command_obj("install_exe")
        command.build_dir = self.build_exe

    def run(self):
        self.build_extension("cx_Logging")
        self.build_extension("cx_Oracle")
        self.add_to_path("cx_PyGenLib")
        self.add_to_path("cx_PyOracleLib")
        cx_Freeze.build_exe.run(self)


# tweak the RPM build command to include the Oracle version
class bdist_rpm(cx_Freeze.bdist_rpm):

    def run(self):
        cx_Freeze.bdist_rpm.run(self)
        specFile = os.path.join(self.rpm_base, "SPECS",
                "%s.spec" % self.distribution.get_name())
        queryFormat = "%{name}-%{version}-%{release}.%{arch}.rpm"
        command = "rpm -q --qf '%s' --specfile %s" % (queryFormat, specFile)
        origFileName = os.popen(command).read()
        parts = origFileName.split("-")
        parts.insert(2, oracleVersion)
        newFileName = "-".join(parts)
        self.move_file(os.path.join("dist", origFileName),
                os.path.join("dist", newFileName))


# method for determining Oracle version
def GetOracleVersion(directoryToCheck):
    if sys.platform in ("win32", "cygwin"):
        subDirs = ["bin"]
        filesToCheck = [
                ("11g", "oraocci11.dll"),
                ("10g", "oraocci10.dll"),
                ("9i", "oraclient9.dll")
        ]
    elif sys.platform == "darwin":
        subDirs = ["lib"]
        filesToCheck = [
                ("11g", "libclntsh.dylib.11.1"),
                ("10g", "libclntsh.dylib.10.1"),
                ("9i", "libclntsh.dylib.9.0")
        ]
    else:
        if struct.calcsize("P") == 4:
            subDirs = ["lib", "lib32"]
        else:
            subDirs = ["lib", "lib64"]
        filesToCheck = [
                ("11g", "libclntsh.so.11.1"),
                ("10g", "libclntsh.so.10.1"),
                ("9i", "libclntsh.so.9.0")
        ]
    for version, baseFileName in filesToCheck:
        fileName = os.path.join(directoryToCheck, baseFileName)
        if os.path.exists(fileName):
            return version
        for subDir in subDirs:
            fileName = os.path.join(directoryToCheck, subDir, baseFileName)
            if os.path.exists(fileName):
                return version
            dirName = os.path.dirname(directoryToCheck)
            fileName = os.path.join(dirName, subDir, baseFileName)
            if os.path.exists(fileName):
                return version

# try to determine the Oracle home
userOracleHome = os.environ.get("ORACLE_HOME")
if userOracleHome is not None:
    oracleVersion = GetOracleVersion(userOracleHome)
    if oracleVersion is None:
        messageFormat = "Oracle home (%s) does not refer to an " \
                "9i, 10g or 11g installation."
        raise DistutilsSetupError(messageFormat % userOracleHome)
else:
    for path in os.environ["PATH"].split(os.pathsep):
        oracleVersion = GetOracleVersion(path)
        if oracleVersion is not None:
            break
    if oracleVersion is None:
        raise DistutilsSetupError("cannot locate an Oracle software " \
                "installation")

executables = [
        cx_Freeze.Executable("CopyData.py"),
        cx_Freeze.Executable("DbDebugger.py"),
        cx_Freeze.Executable("DescribeObject.py"),
        cx_Freeze.Executable("DescribeSchema.py"),
        cx_Freeze.Executable("DumpCSV.py"),
        cx_Freeze.Executable("DumpData.py"),
        cx_Freeze.Executable("ExportColumn.py"),
        cx_Freeze.Executable("ExportData.py"),
        cx_Freeze.Executable("ExportObjects.py"),
        cx_Freeze.Executable("ExportXML.py"),
        cx_Freeze.Executable("GeneratePatch.py"),
        cx_Freeze.Executable("GenerateView.py"),
        cx_Freeze.Executable("ImportColumn.py"),
        cx_Freeze.Executable("ImportData.py"),
        cx_Freeze.Executable("ImportXML.py"),
        cx_Freeze.Executable("PatchDB.py"),
        cx_Freeze.Executable("RebuildTable.py"),
        cx_Freeze.Executable("RecompileSource.py"),
]

if sys.platform != "win32":
    dataFiles = []
else:
    dataFiles = [ ("", [ "LICENSE.TXT", "README.TXT", "HISTORY.txt",
                         "doc/cx_OracleTools.html" ] ) ]

buildOptions = dict(
        compressed = True,
        optimize = 2,
        replace_paths = [("*", "")])
options = dict(build_exe = buildOptions)
if sys.platform == "win32":
    sversion = "%d.%d.%d" % \
            distutils.version.StrictVersion(VERSION).version
    oldUpgradeCode = "{A77F0AB1-3E2A-4242-B6DD-700CF582345C}"
    if struct.calcsize("P") == 4:
        upgradeCode = "{DA558DAE-C9C1-4C6F-82BC-5508DEBD4762}"
    else:
        upgradeCode = "{ED509B82-C0E2-4111-ADFF-F463F03B8548}"
    upgradeData = [(oldUpgradeCode, None, sversion, None, 513, None,
                    "REMOVEOLDOLDVERSION")]
    options["bdist_msi"] = dict(
            add_to_path = True,
            data = dict(Upgrade = upgradeData),
            target_name = "%s-%s-%s" % (NAME, VERSION, oracleVersion),
            upgrade_code = upgradeCode)
else:
    docFiles = "LICENSE.txt README.txt HISTORY.txt doc/cx_OracleTools.html"
    options["bdist_rpm"] = dict(doc_files = docFiles)

cx_Freeze.setup(
        name = NAME,
        version = VERSION,
        description = "Tools for managing Oracle data and source code.",
        long_description = "Tools for managing Oracle data and source code.",
        license = "See LICENSE.txt",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        url = "http://cx-oracletools.sourceforge.net",
        data_files = dataFiles,
        cmdclass = dict(build_exe = build_exe, bdist_rpm = bdist_rpm),
        executables = executables,
        options = options)

