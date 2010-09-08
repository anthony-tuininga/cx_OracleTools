"""
Import data from an XML file into a table in an Oracle database.
"""

import cx_Logging
import cx_LoggingOptions
import cx_OptionParser
import cx_OracleUtils
import sys
import time
import xml.etree.cElementTree

import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.ARRAY_SIZE)
parser.AddOption(Options.COMMIT_POINT)
parser.AddOption(Options.REPORT_POINT)
parser.AddOption(Options.SET_ROLE)
parser.AddOption(Options.DATE_FORMAT)
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("fileName", required = True,
        help = "the name of the file from which to read the data or "
               "'-' to read the exported data from stdin")
parser.AddArgument("tableName", required = True,
        help = "the name of the table into which to import the data")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)

# define class for managing the import
class Handler(object):

    def __init__(self, options):
        self.connection = cx_OracleUtils.Connect(options.schema,
                options.setRole)
        self.cursor = self.connection.cursor()
        if options.arraySize:
            self.cursor.arraysize = options.arraySize
        self.commitPoint = options.commitPoint
        self.reportPoint = options.reportPoint
        self.dateFormat = options.dateFormat
        self.cursor.execute("select * from %s" % options.tableName)
        self.columnIndexes = {}
        self.dateColumns = {}
        bindVars = []
        bindVarNames = []
        columnNames = []
        for item in self.cursor.description:
            name, dataType, size, internalSize, prec, scale, nullsOk = item
            if dataType == self.connection.DATETIME:
                self.dateColumns[name.upper()] = None
            elif dataType != self.connection.CLOB:
                dataType = self.connection.STRING
            self.columnIndexes[name.upper()] = len(bindVars)
            bindVars.append(self.cursor.var(dataType, size))
            columnNames.append(name)
            bindVarNames.append(":%s" % len(bindVars))
        sql = "insert into %s (%s) values (%s)" % \
                (options.tableName, ",".join(columnNames),
                 ",".join(bindVarNames))
        self.cursor.prepare(sql)
        self.cursor.setinputsizes(*bindVars)
        self.allowCustomTags = False
        self.columnValue = None

    def _GetRowFromElement(self, element):
        row = [None] * len(self.columnIndexes)
        for subElement in element:
            name = subElement.tag.upper()
            value = subElement.text
            if not value:
                value = None
            if value is not None and name in self.dateColumns:
                dateValue = time.strptime(value, self.dateFormat)
                value = self.connection.Timestamp(*dateValue[:6])
            columnIndex = self.columnIndexes[subElement.tag.upper()]
            row[columnIndex] = value
        return row

    def Process(self, inputFile):
        rowsImported = 0
        rowsToInsert = []
        for event, elem in xml.etree.cElementTree.iterparse(inputFile):
            if elem.tag != "ROW":
                continue
            row = self._GetRowFromElement(elem)
            rowsToInsert.append(row)
            rowsImported += 1
            commit = (self.commitPoint \
                    and rowsImported % self.commitPoint == 0)
            if commit or len(rowsToInsert) == self.cursor.arraysize:
                self.cursor.executemany(None, rowsToInsert)
                rowsToInsert = []
                if commit:
                    self.connection.commit()
            if self.reportPoint and rowsImported % self.reportPoint == 0:
                cx_Logging.Trace("%d rows imported.", rowsImported)
            elem.clear()
        if rowsToInsert:
            self.cursor.executemany(None, rowsToInsert)
        if self.commitPoint is None or rowsImported % self.commitPoint != 0:
            self.connection.commit()
        if self.reportPoint is None or rowsImported % self.reportPoint != 0:
            cx_Logging.Trace("%d rows imported.", rowsImported)

# parse the XML data stream
if options.fileName == "-":
    inputFile = sys.stdin
else:
    inputFile = file(options.fileName, "r")
handler = Handler(options)
handler.Process(inputFile)

