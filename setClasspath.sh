#######################################
# setClasspath.sh
#   This script sets up necessary 
#   classpaths for JBoost. 
# Usage:
#   cd jboost
#   source setClasspath.sh
######################################

#!/bin/sh

SN="setClasspath.sh"

echo $0 | grep -qE $SN
if [ $? -eq 0 ] 
then
    echo "Fail to set up the JBoost classpath."
    echo "Please run \"source $SN\" instead of \"$0\"."
    exit 1
fi

JBOOST_HOME=`pwd`
export CLASSPATH="$JBOOST_HOME/dist/jboost.jar:$JBOOST_HOME/lib/jcommon-1.0.8.jar:$JBOOST_HOME/lib/jfreechart-1.0.10.jar:$CLASSPATH"

echo "JBoost classpath is ready."
