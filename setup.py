import distutils.core
import cx_Freeze
import os
import sys

DEPENDENT_PROJECTS = [
        ("cx_Logging", "trunk"),
        ("cx_Oracle", "trunk"),
        ("cx_PyGenLib", "trunk"),
        ("cx_PyOracleLib", "trunk")
]

for projInfo in DEPENDENT_PROJECTS:
    name = projInfo[0]
    envName = "%s_SOURCE" % name.upper()
    value = os.environ.get(envName)
    if value is None:
        value = os.path.realpath(os.path.join("..", "..", *projInfo))
        if os.path.isdir(value):
            os.environ[envName] = value

class build_exe(cx_Freeze.build_exe):
    user_options = cx_Freeze.build_exe.user_options + [
            ('cx-logging=', None, 'location of cx_Logging sources'),
            ('cx-oracle=', None, 'location of cx_Oracle sources'),
            ('cx-pygenlib=', None, 'location of cx_PyGenLib sources'),
            ('cx-pyoraclelib=', None, 'location of cx_PyOracleLib sources')
    ]

    def _build_extension(self, name):
        sourceDir = getattr(self, name.lower())
        if sourceDir is None:
            return
        origDir = os.getcwd()
        scriptArgs = ["build"]
        command = self.distribution.get_command_obj("build")
        if command.compiler is not None:
            scriptArgs.append("--compiler=%s" % command.compiler)
        os.chdir(sourceDir)
        print "building", name, "in", sourceDir
        distribution = distutils.core.run_setup("setup.py", scriptArgs)
        module, = distribution.ext_modules
        command = distribution.get_command_obj("build_ext")
        command.ensure_finalized()
        command.build_extensions()
        dirName = os.path.join(sourceDir, command.build_lib)
        os.chdir(origDir)
        sys.path.insert(0, dirName)

    def _set_source_location(self, name, addToPath = True):
        envName = "%s_SOURCE" % name.upper()
        value = getattr(self, name.lower())
        if value is None:
            value = os.environ.get(envName)
        if value is not None:
            setattr(self, name.lower(), value)
            os.environ[envName] = value
            if addToPath:
                sys.path.insert(0, value)

    def initialize_options(self):
        cx_Freeze.build_exe.initialize_options(self)
        self.cx_logging = None
        self.cx_oracle = None
        self.cx_pygenlib = None
        self.cx_pyoraclelib = None 

    def finalize_options(self):
        cx_Freeze.build_exe.finalize_options(self)
        self._set_source_location("cx_Logging", addToPath = False)
        self._set_source_location("cx_Oracle", addToPath = False)
        self._set_source_location("cx_PyGenLib")
        self._set_source_location("cx_PyOracleLib")

    def run(self):
        self._build_extension("cx_Logging")
        self._build_extension("cx_Oracle")
        cx_Freeze.build_exe.run(self)


executables = [
        cx_Freeze.Executable("CompileSource.py"),
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
        cx_Freeze.Executable("RebuildTable.py"),
        cx_Freeze.Executable("RecompileSource.py"),
]

buildOptions = dict(
        compressed = True,
        optimize = 2,
        replace_paths = [("*", "")])
msiOptions = dict(
        upgrade_code = "{A77F0AB1-3E2A-4242-B6DD-700CF582345C}")

cx_Freeze.setup(
        name = "cx_OracleTools",
        version = "7.5b1",
        description = "Tools for managing Oracle data and source code.",
        long_description = "Tools for managing Oracle data and source code.",
        license = "See LICENSE.txt",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        url = "http://cx-oracletools.sourceforge.net",
        cmdclass = dict(build_exe = build_exe),
        executables = executables,
        options = dict(build_exe = buildOptions, bdist_msi = msiOptions))

