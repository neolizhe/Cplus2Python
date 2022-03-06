#!/bin/env python
#conding:utf-8

import numpy as np
from ctypes import *
global DISFUNCS,C_POINT,DISMATRIX

C_POINT = POINTER(c_double)
DISFUNCS =pydll.LoadLibrary("/home/strategy_04/neolizhe/data/funcs.so").funcs
DISFUNCS.argtypes = [C_POINT, C_POINT]
DISFUNCS.restype = c_double

DISMATRIX =pydll.LoadLibrary("/home/strategy_04/neolizhe/data/funcs.so").matrix_funcs
DISMATRIX.argtypes = [C_POINT, c_int, C_POINT, c_int]
DISMATRIX.restype = py_object

def compute_dis(arr1, arr2):
    arr1 = arr1.ctypes.data_as(C_POINT)
    arr2 = arr2.ctypes.data_as(C_POINT)
    return DISFUNCS(arr1, arr2)
def matrix_cmp(X,Y):
    size1 = len(X)
    size2 = len(Y)
    matrix1 = X.reshape(-1).ctypes.data_as(C_POINT)
    matrix2 = Y.reshape(-1).ctypes.data_as(C_POINT)
    res_list = DISMATRIX(matrix1, size1, matrix2, size2)
    res_array = np.array(res_list).reshape(len(X),len(Y))
    return res_array
if __name__=='__main__':
    dt = 'float64'
    arr1 = np.array([[0,1,2,4,5,6],[1,2,3,4,5,7]],dtype = dt)
    arr2 = np.array([[0,1,10,4,1,4],[1,1,3,4,2,5]],dtype = dt)
    #arr1 = arr1.reshape(-1).ctypes.data_as(C_POINT)
    #arr2 = arr2.reshape(-1).ctypes.data_as(C_POINT)
    res_list = matrix_cmp(arr1,arr2)
    #for i in res_list:
    arr3 = np.array([0,1,2,4,5,6],dtype = dt)
    arr4 = np.array([1,1,10,4,1,4],dtype = dt)
    res = compute_dis(arr3,arr4)
    print "i %.5f"%res
    print res_list
