#!/usr/bin/env bash
# cloc: count lines of code

scriptPath=`dirname $0`
cloc ${scriptPath}/benchmark ${scriptPath}/benchmark_dashboard ${scriptPath}/python_benchmark | tee  ${scriptPath}/loc.txt
