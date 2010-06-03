"""
Generates a patch for differences in objects in two directories (which may
have been created with ExportObjects) and ensures that the patch script can
be executed without fear of encountering errors because of dependencies between
objects.
"""

import cx_LoggingOptions
import cx_OptionParser
import cx_OracleObject
import cx_OracleParser
import cx_OracleUtils
import cx_Utils
import os
import sys

import Exceptions
import Options

# parse command line
parser = cx_OptionParser.OptionParser()
parser.AddOption(cx_OracleUtils.SchemaOption())
parser.AddOption(Options.NO_COMMENTS)
parser.AddOption(Options.NO_GRANTS)
parser.AddOption(Options.USE_DBA_VIEWS)
cx_LoggingOptions.AddOptions(parser)
parser.AddArgument("fromDir", required = 1,
        help = "the directory containing the source objects")
parser.AddArgument("toDir", required = 1,
        help = "the directory containing the target objects or the objects "
               "which the source objects will be transformed into using the "
               "generated script")
options = parser.Parse()
cx_LoggingOptions.ProcessOptions(options)
options.fromDir = os.path.normpath(options.fromDir)
if not os.path.exists(options.fromDir):
    raise Exceptions.SourceDirectoryNotFound()
options.toDir = os.path.normpath(options.toDir)
if not os.path.exists(options.toDir):
    raise Exceptions.TargetDirectoryNotFound()

# set up describe environment
connection = cx_OracleUtils.Connect(options.schema)
environment = cx_OracleObject.Environment(connection, options)
describer = cx_OracleObject.Describer(environment, options)
wantGrants = describer.wantGrants

# define some constants
CONSTRAINT_TYPES = ["PRIMARY KEY", "UNIQUE CONSTRAINT", "FOREIGN KEY",
        "CHECK CONSTRAINT"]
SOURCE_TYPES = ["FUNCTION", "PACKAGE", "PACKAGE BODY", "PROCEDURE", "TYPE",
        "TYPE BODY", "VIEW"]

# define parser and statement classes used
parser = cx_OracleParser.SimpleParser()
createConstraintClass = parser.parser.processor.CreateConstraintStatement
createStatementClass = parser.parser.processor.CreateObjectStatement
grantStatementClass = parser.parser.processor.GrantStatement

# define a function which will return the list of objects in the files
def ObjectsInFiles(files, baseDir):
    objs = {}
    for file_ in files:
        dir, objName = os.path.split(file_[:-4].upper())
        dir, objType = os.path.split(dir)
        dir, objOwner = os.path.split(dir)
        baseName = os.path.join(objOwner, objType, objName + ".sql").lower()
        file_ = os.path.join(baseDir, baseName)
        for statement in parser.Parse(open(file_).read(), objOwner):
            if isinstance(statement, createStatementClass):
                key = (statement.owner, statement.name, statement.type.upper())
                objs[key] = baseName
    return objs

# define a function which will return the statements in a given file
def Statements(baseDir, baseName, objType, objName):
    found = 0
    statements = []
    fileName = os.path.join(baseDir, baseName)
    for statement in parser.Parse(open(fileName).read()):
        if isinstance(statement, createStatementClass):
            if found:
                break
            found = (statement.type.upper() == objType
                    and statement.name == objName)
        if found:
            statements.append(statement)
    return statements

# define a function to return a dependency
def DependsOn(statement, objOwner, objName, objType):
    if objType == "PACKAGE BODY":
        return (objOwner, objName, "PACKAGE")
    elif objType == "TYPE BODY":
        return (objOwner, objName, "TYPE")
    else:
        words = statement.sql.lower().split()
        if objType == "INDEX":
            return (objOwner, words[4].upper(), "TABLE")
        elif objType in ("UNIQUE INDEX", "BITMAP INDEX"):
            return (objOwner, words[5].upper(), "TABLE")
        elif objType in CONSTRAINT_TYPES:
            return (statement.owner, statement.tableName, "TABLE")
        elif objType == "TRIGGER":
            index = words.index("on")
            return (objOwner, words[index].upper(), "TABLE")

# output drop statement for the given object
def OutputDropStatement(statement, objsToDrop, objOwner, objName, objType,
        hardDrop):
    dependsOn = DependsOn(statement[0], objOwner, objName, objType)
    if dependsOn:
        refOwner, refName, refType = dependsOn
        if objsToDrop.has_key((refOwner, refName, refType)):
            return
    if objType in ("UNIQUE INDEX", "BITMAP INDEX"):
        objType = "INDEX"
    elif objType in CONSTRAINT_TYPES:
        objType = "CONSTRAINT"
    describer.SetOwner(objOwner, objType)
    if not hardDrop and objType == "TABLE":
        print "--",
    if objType == "CONSTRAINT":
        print "alter table", refName.lower()
    print "drop", objType.lower(), objName.lower() + ";"
    print

# define a function which will return the grants in a set of statements
def ParseGrants(statements):
    grants = {}
    for statement in statements:
        statement = statement.sql.replace("\n", " ").strip()
        withGrantOption = ""
        if statement.endswith("with grant option"):
            withGrantOption = statement[-18:]
            statement = statement[:-18]
        pos = statement.index(" on ")
        privileges = [s.strip() for s in statement[6:pos].split(",")]
        pos = statement.index(" to ")
        grantees = [s.strip() for s in statement[pos + 4:].split(",")]
        for privilege in privileges:
            for grantee in grantees:
                grants[(privilege, grantee)] = withGrantOption
    return grants

# acquire the list of objects that have changed
print >> sys.stderr, "Acquiring differences..."
newFiles, modifiedFiles, removedFiles = \
        cx_Utils.PerformDiff(options.fromDir, options.toDir)

# determine the owner, name and type of object in each file that is of interest
oldObjs = ObjectsInFiles(modifiedFiles + removedFiles, options.fromDir)
newObjs = ObjectsInFiles(modifiedFiles + newFiles, options.toDir)

# sort the objects into three arrays for simpler processing
preSourceObjs = [(o, n, t) for o, n, t in newObjs \
        if t != "TRIGGER" and t not in SOURCE_TYPES]
sourceObjs = [(o, n, t) for o, n, t in newObjs if t in SOURCE_TYPES]
postSourceObjs = [(o, n, t) for o, n, t in newObjs if t == "TRIGGER"]
postSourceObjs.sort()

# order the pre source objects by acquiring dependencies
if preSourceObjs:

    # acquire the dependencies
    dependencies = []
    for obj in preSourceObjs:
        objOwner, objName, objType = obj
        statements = Statements(options.toDir, newObjs[obj], objType, objName)
        dependsOn = DependsOn(statements[0], objOwner, objName, objType)
        if dependsOn:
            refOwner, refName, refType = dependsOn
            dependencies.append((objOwner, objName, objType, refOwner, refName,
                    refType))

    # now order them
    print >> sys.stderr, "Ordering pre source objects..."
    preSourceObjs = cx_OracleObject.OrderObjects(preSourceObjs, dependencies)

# order the source objects by retrieving dependencies
if sourceObjs:

    # determine the list of schemas that are affected
    currentOwner = describer.currentOwner
    schemas = {}
    for objOwner, name, objType in sourceObjs:
        schemas[objOwner] = None
    describer.schemas = schemas.keys()
    describer.currentOwner = currentOwner

    # acquire the list of dependencies from the database
    print >> sys.stderr, "Acquiring dependencies..."
    dependencies = describer.RetrieveDependencies()

    # now order them
    print >> sys.stderr, "Ordering source objects..."
    sourceObjs = cx_OracleObject.OrderObjects(sourceObjs, dependencies)

# perform the drops
objsToDrop = {}
for obj in oldObjs:
    if obj not in newObjs:
        objsToDrop[obj] = None
if objsToDrop:
    print >> sys.stderr, "Dropping unused objects..."
    print "-- dropping unused objects"
    print
    objs = objsToDrop.keys()
    objs.sort()
    for obj in objs:
        objOwner, objName, objType = obj
        statements = Statements(options.fromDir, oldObjs[obj], objType,
                objName)
        OutputDropStatement(statements, objsToDrop, objOwner, objName, objType,
                True)

# output the statements for all of the objects
print >> sys.stderr, "Generating patch for new and modified objects..."
for obj in preSourceObjs + sourceObjs + postSourceObjs:

    # initialization
    objOwner, objName, objType = obj
    outputType = objType.lower()
    outputName = objName.lower()
    existed = oldObjs.has_key(obj)

    # retrieve the statements in the files
    newStatements = Statements(options.toDir, newObjs[obj], objType,
            objName)
    if existed:
        oldStatements = Statements(options.fromDir, oldObjs[obj], objType,
                objName)

    # handle the case where the object is new or is a trigger
    if not existed or objType == "TRIGGER":
      describer.SetOwner(objOwner, objType)
      if existed:
          print "-- modifying",
      else:
          print "-- creating",
      print outputType, outputName
      print
      for statement in newStatements:
          if wantGrants or not isinstance(statement, grantStatementClass):
              sys.stdout.write(statement.sql)
              sys.stdout.write("\n\n")

    # otherwise, perform comparisons and output applicable code to make changes
    else:

        # compare main object
        if newStatements[0].sql != oldStatements[0].sql:
          describer.SetOwner(objOwner, objType)
          print "-- modifying", outputType, outputName
          print
          if objType not in SOURCE_TYPES:
              OutputDropStatement(oldStatements, objsToDrop, objOwner,
                      objName, objType, False)
          newStatements[0].Write(sys.stdout)

        # acquire the grants
        if not wantGrants:
            continue
        newGrants = ParseGrants(newStatements[1:])
        oldGrants = ParseGrants(oldStatements[1:])

        # determine privileges to be revoked
        revokes = [r for r in oldGrants if r not in newGrants]

        # determine the privileges to be granted
        grants = []
        for row, withGrantOption in newGrants.items():
            origGrantOption = oldGrants.get(row)
            if withGrantOption != origGrantOption:
                grants.append((row[0], row[1], withGrantOption))
                if origGrantOption == " with grant option":
                    revokes.append(row)

        # output the privilege changes
        if grants or revokes:
            describer.SetOwner(objOwner, objType)
            print "-- modifying grants for", outputType, outputName
            print
            revokes.sort()
            for privilege, grantee in revokes:
                print "revoke", privilege, "on", outputName, "from",
                print grantee + ";"
            grants.sort()
            for privilege, grantee, withGrantOption in grants:
                print "grant", privilege, "on", outputName, "to",
                print grantee + withGrantOption + ";"
            print

