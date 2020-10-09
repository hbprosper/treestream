DIR="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
export PYTHONPATH=$DIR:$DIR/lib:$PYTHONPATH
export LD_LIBRARY_PATH=$DIR/lib:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$DIR/lib:$DYLD_LIBRARY_PATH
export PATH=$DIR/bin:$PATH
export TREESTREAM_PATH=$DIR
echo $DIR
