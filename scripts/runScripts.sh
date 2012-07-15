#!/usr/bin/env bash

echo "test"

JBOOST_HOME=`pwd`

if [ $# -eq 0 ] 
then 
    NAME="spambase"
else 
    NAME=$1
fi

cd $JBOOST_HOME/demo

INAME=${NAME}_idx
SB=$JBOOST_HOME/scripts

echo creating directory for $NAME
mkdir $NAME
cp $NAME.* $NAME
cd $NAME

echo running $NAME a single time
java -Xmx500M jboost.controller.Controller -S $NAME -a -2

echo generating graphs for the single run
perl $SB/atree2dot2ps.pl  --info $NAME.info --tree $NAME.output.tree --threshold 10 

python $SB/error.py --info=$NAME.info --logaxis

python $SB/margin_test_train.py --boost-info-test=$NAME.test.boosting.info --boost-info-train=$NAME.train.boosting.info --iteration=5,10,50,100

echo running 6 fold cross validation for $NAME

cp $NAME.train $NAME.data
cat $NAME.test >> $NAME.data

echo adding index to $NAME to create $INAME

python $SB/AddRandomIndex.py $NAME

echo running 6 fold cross validation

python $SB/nfold.py --folds=6 --data=$INAME.data --spec=$INAME.spec --booster=AdaBoost  --rounds=30 --tree=ADD_ALL --generate

echo Visualizing the margins for the 6-fold cross validation of $INAME

python $SB/VisualizeScores.py $INAME.data.folds_6/cvdata*/ADD_ALL/trial


