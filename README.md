# Cplus2Python
speedup python with ctypes.
# step
## 1.cd cpython
edit cpp/h to realize metric compute or other funcs.
use 
$ g++ -lstdc++ `python-config --ldflags` -o funcs.o funcs.cpp $
to link cpp as dynamic c++ lib "func.o"

## 2.cd ..
import ctypes ndpointer as interferce between cpp array to python array.
