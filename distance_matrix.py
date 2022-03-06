#!/bin/python
#coding:utf-8

from vector_metric import *
from tqdm import tqdm
import numpy as np
import multiprocessing
from multiprocessing import Manager
import time
from ctypes import *
multiprocessing.connection.BUFSIZE='50000'
global DISFUNCS,DISMATRIX,P_TYPE,C_TYPE

P_TYPE = 'float32'
C_TYPE = c_float
file_path = "/home/strategy_04/neolizhe/data/funcs.so"

array_p_2d = np.ctypeslib.ndpointer(dtype=P_TYPE,ndim=2,flags='C_CONTIGUOUS')
array_p_1d = np.ctypeslib.ndpointer(dtype=P_TYPE,ndim=1,flags='C_CONTIGUOUS')

DISFUNCS = pydll.LoadLibrary(file_path).funcs
DISFUNCS.argtypes = [array_p_1d, array_p_1d]
DISFUNCS.restype = C_TYPE

DISMATRIX = pydll.LoadLibrary(file_path).matrix_funcs
DISMATRIX.argtypes = [array_p_2d, c_int, array_p_2d, c_int]
DISMATRIX.restype = py_object

def compute_dis(arr1,arr2):
    if not (arr1.flags['C_CONTIGUOUS'] and arr2.flags['C_CONTIGUOUS']):
        arr1 = np.ascontiguousarray(arr1,dtype=P_TYPE)
        arr2 = np.ascontiguousarray(arr2,dtype=P_TYPE)
    else:
        arr1 = arr1.astype(P_TYPE)
        arr2 = arr2.astype(P_TYPE)
    return DISFUNCS(arr1, arr2)
def matrix_cmp(X,Y):
    size1 = len(X)
    size2 = len(Y)
    if not (X.flags['C_CONTIGUOUS'] and Y.flags['C_CONTIGUOUS']):
        matrix1 = np.ascontiguousarray(X,dtype=P_TYPE)
        matrix2 = np.ascontiguousarray(Y,dtype=P_TYPE)
    else:
        matrix1 = X.astype(P_TYPE)
        matrix2 = Y.astype(P_TYPE)
    res_list = DISMATRIX(matrix1, c_int(size1), matrix2, c_int(size2))
    res_array = np.array(res_list).reshape(size1,size2)
    return res_array
def compute_dis_old(line1_array,line2_array):
    if (len(line1_array)<6) | (len(line2_array)<6):
        raise "length < 6"
    p1 = Point(line1_array[:3])
    p2 = Point(line1_array[3:])
    p3 = Point(line2_array[:3])
    p4 = Point(line2_array[3:])
    line1=Line(p1,p2)
    line2 = Line(p3,p4)
    dis =Distance(line1,line2)
    return dis.dis_compute()
def compute_matrix(X,Y=None):
    #     dim n*[[3],[3]]
    if Y is None:
        output_array = matrix_cmp(X, X)
    else:
        output_array = matrix_cmp(X, Y)
    return output_array
def compute_chunk_matrix(X,q,start,end,Y=None):
    #     dim n*[[3],[3]]
    if Y is None:
        with tqdm(range(1),"Matrix Dis processing...") as t:
            for _ in t:
                output_array = matrix_cmp(X, X)
    else:
        with tqdm(range(1),"X-Y Dis processing...") as t:
            for _ in t:
                output_array = matrix_cmp(X, Y)
        # np.savez("/home/strategy_04/neolizhe/data/matrix_2",output_array)
    q.put([start,end,output_array])
def parallel_cmp(X,Y=None,func='compute_chunk_matrix',parallel_size=15):
    with Manager() as mn:
        q=mn.Queue()
        p_l=[]
        num = len(X)
        batch_size=num//parallel_size
        left_size=num % parallel_size
        if left_size>0:
            tol_p_size=parallel_size+1
        else:
            tol_p_size=parallel_size
        if Y is None:
            for i in range(tol_p_size):
                if i==parallel_size:
                    start,end=num-left_size,num
                    b_X = X[start:end]
                    kw={'X':b_X,'q':q,'start':start,'end':end}
                    p_l.append(multiprocessing.Process(target=eval(func),kwargs=kw))
                else:
                    start,end=i*batch_size,(i+1)*batch_size
                    b_X = X[start:end]
                    b_Y = X[start:]
                    kw={'X':b_X,'Y':b_Y,'q':q,'start':start,'end':end}
                    p_l.append(multiprocessing.Process(target=eval(func),kwargs=kw))
        else:
            for i in range(tol_p_size):
                if i==parallel_size:
                    start,end=tol_p_size-left_size,tol_p_size
                else:
                    start,end=i*batch_size,(i+1)*batch_size
                b_X = X[start:end]
                b_Y = Y
                kw={'X':b_X,'Y':b_Y,'q':q,'start':start,'end':end}
                p_l.append(multiprocessing.Process(target=eval(func),kwargs=kw))
        for i in range(tol_p_size):
            p_l[i].start()
        for i in range(tol_p_size):
            p_l[i].join()
        res_list=[]
        while True:
            try:
                tmp = q.get(False)
                res_list.append(tmp)
            except:
                pass
            allExited = True
            for t in p_l:
                if t.exitcode is None:
                    allExited = False
                    break
            if allExited & q.empty():
                break
    print("parallel run done!")
    # 
    res_list = sorted(res_list,key=lambda x:x[0])
    if Y is None:
        res_array = np.zeros(shape=(1,num),dtype=P_TYPE)
        for i in res_list:
            v_array = np.zeros(shape=(i[1]-i[0],num),dtype=P_TYPE)
            v_array[:,i[0]:] = i[2]
            res_array = np.concatenate((res_array,v_array),axis=0)
        res_array = res_array[1:]
        for i in range(num):
            for j in range(i+1):
                res_array[i][j] = 0
        res_array += np.transpose(res_array)
        print("Output dis matrix to csv")
        np.savez('/home/strategy_04/neolizhe/data/matrix_data',res_array)
    else:
        res_array = np.zeros(shape=(1,len(Y)),dtype=P_TYPE)
        for i in res_list:
            res_array = np.concatenate((res_array,i[2]),axis=0)
            res_array = res_array[1:]
        print("Output dis X-Y to csv")
        np.savez('/home/strategy_04/neolizhe/data/array_data',res_array)
    return res_array
