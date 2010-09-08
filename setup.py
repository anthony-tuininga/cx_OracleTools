import cx_Freeze
import sys

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

    def run(self):
        self.build_extension("cx_Logging")
        self.build_extension("cx_Oracle")
        self.add_to_path("cx_PyGenLib")
        self.add_to_path("cx_PyOracleLib")
        cx_Freeze.build_exe.run(self)


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
    options["bdist_msi"] = dict(
            upgrade_code = "{A77F0AB1-3E2A-4242-B6DD-700CF582345C}")
else:
    docFiles = "LICENSE.txt README.txt HISTORY.txt doc/cx_OracleTools.html"
    options["bdist_rpm"] = dict(doc_files = docFiles)

cx_Freeze.setup(
        name = "cx_OracleTools",
        version = "8.0",
        description = "Tools for managing Oracle data and source code.",
        long_description = "Tools for managing Oracle data and source code.",
        license = "See LICENSE.txt",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        url = "http://cx-oracletools.sourceforge.net",
        data_files = dataFiles,
        cmdclass = dict(build_exe = build_exe),
        executables = executables,
        options = options)

