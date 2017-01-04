scriptPath=`dirname $0`
cloc ${scriptPath}/benchmark --exclude-dir=js > ${scriptPath}/loc.txt

