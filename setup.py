from cx_Freeze import setup, Executable

executables = [
        Executable("CompileSource.py"),
        Executable("CopyData.py"),
        Executable("DbDebugger.py"),
        Executable("DescribeObject.py"),
        Executable("DescribeSchema.py"),
        Executable("DumpCSV.py"),
        Executable("DumpData.py"),
        Executable("ExportColumn.py"),
        Executable("ExportData.py"),
        Executable("ExportObjects.py"),
        Executable("ExportXML.py"),
        Executable("GeneratePatch.py"),
        Executable("GenerateView.py"),
        Executable("ImportColumn.py"),
        Executable("ImportData.py"),
        Executable("ImportXML.py"),
        Executable("RebuildTable.py"),
        Executable("RecompileSource.py"),
]

buildOptions = dict(
        compressed = True)
msiOptions = dict(
        upgrade_code = "{A77F0AB1-3E2A-4242-B6DD-700CF582345C}")

setup(
        name = "cx_OracleTools",
        version = "7.5b1",
        description = "Set of tools for managing Oracle data and source code.",
        license = "See LICENSE.txt",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        url = "http://cx-oracletools.sourceforge.net",
        executables = executables,
        options = dict(build_exe = buildOptions, bdist_msi = msiOptions))

