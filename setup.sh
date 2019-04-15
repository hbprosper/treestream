DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$DIR:$DIR/lib:$PYTHONPATH
export LD_LIBRARY_PATH=$DIR/lib:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$DIR/lib:$DYLD_LIBRARY_PATH
export PATH=$DIR/bin:$PATH
export TREESTREAM_PATH=$DIR
export EXTERNAL=$HOME/external

