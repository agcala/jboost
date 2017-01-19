SITE="jboost.sourceforge.net"
DIR="/"

rm -rf css images 

wget -r -o wget.log http://${SITE}/${DIR}
mv  ${SITE}/${DIR}/* .

rm -rf ${SITE}
rm wget.log 

