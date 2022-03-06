#!/bin/env python
#coding:utf-8

import sklearn.cluster as sc
import sklearn.metrics as sm
from sklearn.utils import check_random_state,check_X_y,_safe_indexing
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.cluster._unsupervised import check_number_of_labels
from distance_matrix import *
import numpy as np
import pandas as pds

# DBSCAN算法:从样本空间中任意选择一个样本，以事先给定的半径做圆，凡被该圆圈中的样本都视为与该样本处于相同的聚类，
#     以这些被圈中的样本为圆心继续做圆，重复以上过程，不断扩大被圈中样本的规模，直到再也没有新的样本加入为止，
#     至此即得到一个聚类。于剩余样本中，重复以上过程，直到耗尽样本空间中的所有样本为止。

# DBSCAN算法的特点：
#     1.事先给定的半径会影响最后的聚类效果，可以借助轮廓系数选择较优的方案。
#     2.根据聚类的形成过程，把样本细分为以下三类：
#         外周样本：被其它样本聚集到某个聚类中，但无法再引入新样本的样本。
#         孤立样本：聚类中的样本数低于所设定的下限，则不称其为聚类，反之称其为孤立样本。
#         核心样本：除了外周样本和孤立样本以外的样本。
def log_transfer(x):
    return np.log10(x)
def generate_ep_ary(left,right,nums=10,mid_num=None):
    if left == 0:
        left += 1e-6
    if right / left < 50:
        return np.linspace(left,right,nums)
    else:
        log_ary = np.linspace(log_transfer(left),log_transfer(right),nums)
    log_ary = [10**x for x in log_ary]
    if mid_num:
        log_ary.append(mid_num)
    return np.sort(log_ary)
def davies_bouldin_score(X,labels):
#     overwrite with sp metric
    X, labels = check_X_y(X, labels)
    le = LabelEncoder()
    labels = le.fit_transform(labels)
    n_samples, _ = X.shape
    n_labels = len(le.classes_)
    check_number_of_labels(n_labels, n_samples)
    intra_dists = np.zeros(n_labels)
    centroids = np.zeros((n_labels, len(X[0])), dtype=np.float)
    for k in range(n_labels):
        cluster_k = _safe_indexing(X, labels == k)
        centroid = cluster_k.mean(axis=0)
        centroids[k] = centroid
        intra_dists[k] = np.average(compute_matrix(
        np.array(cluster_k), np.array([centroid])))
    centroid_distances = compute_matrix(centroids)
    if np.allclose(intra_dists, 0) or np.allclose(centroid_distances, 0):
        return 0.0
    centroid_distances[centroid_distances == 0] = np.inf
    combined_intra_dists = intra_dists[:, None] + intra_dists
    scores = np.max(combined_intra_dists / centroid_distances, axis=1)
    return np.mean(scores)

def DBSCAN_loop(matrix,X,score_thres,nums,min_cluster):
    # 选择最优半径
    init_left = np.min(matrix)
    init_right = np.max(matrix)
    epsilons = generate_ep_ary(init_left,init_right,nums)
    score,iters =10,0
    while True:
        # 针对每个半径构建DBSCAN模型
        old_score = score
        models, scores=[],[]
        for epsilon in epsilons:
            model = sc.DBSCAN(eps=epsilon, metric='precomputed',min_samples=2)
            model.fit(matrix)
            if (len(set(model.labels_)) < min_cluster) | (len(set(model.labels_)) >= len(X)):
                scores.append(10)
                models.append(10)
                continue
            score = davies_bouldin_score(X,model.labels_)
            models.append(model)
            scores.append(score)
        if scores == []:
            continue
        index = np.array(scores).argmin()
        score = scores[index]
        if (np.abs(old_score - score ) < score_thres) | (old_score < score):
            # print(old_score,score)
            break
        best_model = models[index]
        
        if (index >= 2) & (index < nums - 2):
            epsilons = generate_ep_ary(epsilons[index-2],epsilons[-1],nums,mid_num = epsilons[index])
        elif index < 2:
            epsilons = generate_ep_ary(epsilons[0],epsilons[-1],nums,mid_num = epsilons[index])
        else:
            epsilons = generate_ep_ary(epsilons[index-2],epsilons[-1],nums,mid_num = epsilons[index])
        iters += 1
        print("Iteration No.%d"%iters,"Best score:%.3f"%score)
    # DBSAN算法的副产品   获取核心样本的下标
    try:
        core_indices = best_model.core_sample_indices_
        # 获取孤立样本的掩码#     offset_mask = best_model.labels_ == -1
        # 获取外周样本的掩码#     p_mask = ~(core_mask | offset_mask)
        return X[core_indices],best_model.labels_[core_indices]
    except:
        rand_size = int(len(X)**0.5)
        rand_index = np.random.randint(len(X),size = rand_size)
        print("Data isnot enough & use random cores")
        return X[rand_index],np.arange(rand_size)

def output_cores(cores,labels):
    cores_df=pds.DataFrame({'cluster_id':labels,'start_lng':cores[:,0],'start_lat':cores[:,1]
                             ,'start_time':cores[:,2],'end_lng':cores[:,3],'end_lat':cores[:,4]
                             ,'end_time':cores[:,5]})
    cores_df = cores_df.groupby('cluster_id').mean().reset_index()
    return cores_df
def unite_compute(inputs,min_cluster,load_m = False):
    if load_m:
        dis_matrix = np.load('/home/strategy_04/neolizhe/data/matrix_data.npz')
        dis_matrix = dis_matrix['arr_0']
    else:
        dis_matrix = parallel_cmp(X=inputs.values,parallel_size=20)
    cores,labels = DBSCAN_loop(dis_matrix.astype('float16'),inputs.values,score_thres = 1e-6,nums = 20,min_cluster = min_cluster)
    res_df = output_cores(cores,labels)
    return res_df
