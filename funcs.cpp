#include <cstdlib>
#include <iostream>
#include <sys/time.h>
#include "math.h"
#include "dis_compute.h"
#include "dis_compute.cpp"
#include <python2.7/Python.h>

extern "C" {
        float funcs(float *arr_p1, float *arr_p2);
        int adds(int a, int b);
        PyObject* matrix_funcs(float *matrix_p1, int size1, float *matrix_p2, int size2);
}

int adds(int a, int b) {
    return a+b;
}

float funcs(float *arr_p1, float *arr_p2) {
    // uint64_t t1 = timems();
    Point p1(*arr_p1,*(arr_p1 + 1),*(arr_p1 + 2));
    Point p2(*(arr_p1 + 3),*(arr_p1 + 4),*(arr_p1 + 5));
    Point p3(*arr_p2,*(arr_p2 + 1),*(arr_p2 + 2));
    Point p4(*(arr_p2 + 3),*(arr_p2 + 4),*(arr_p2 + 5));
    Distance* d_p = new Distance(Line(p1, p2), Line(p3, p4));
    // uint64_t t2 = timems();
    float res = d_p->execute();
    delete d_p;
    return res > 50000 ? 50000 : res;
}

// float funcs(float arr1[6], float arr2[6]) {
//     // uint64_t t1 = timems();
//     Point p1(arr1[0], arr1[1], arr1[2]);
//     Point p2(arr1[3], arr1[4], arr1[5]);
//     Point p3(arr2[0], arr2[1], arr2[2]);
//     Point p4(arr2[3], arr2[4], arr2[5]);
//     Distance* d_p = new Distance(Line(p1, p2), Line(p3, p4));
//     // uint64_t t2 = timems();
//     float res = d_p->execute();
//     delete d_p;
//     return res > 50000 ? 50000 : res;
// }


float timems() {
    timeval time;
    ::gettimeofday(&time, 0);
    return time.tv_usec;
}

PyObject* matrix_funcs(float *matrix_p1, int size1, float *matrix_p2, int size2) {
    PyObject* res_list = PyList_New(0);
    int row_nums = size1;
    int col_nums = size2;
    for (float *pi = matrix_p1; pi != matrix_p1 + size1*6; pi += 6) {
        for (float *qi = matrix_p2; qi != matrix_p2 + size2*6; qi += 6) {
            // float arr1[6] = {*pi, *(pi + 1), *(pi + 2), *(pi + 3), *(pi + 4), *(pi + 5)};
            // float arr2[6] = {*pi, *(pi + 1), *(pi + 2), *(pi + 3), *(pi + 4), *(pi + 5)};
            PyList_Append(res_list, PyFloat_FromDouble(funcs(pi, qi)));
            // res += funcs(pi, qi);
        }
    }
    return res_list;
}

// int main() {
//     float t1 = timems();
//     float ar1[6] = {0.11612454, 0.03990476, 4.31666667, 0.11622075, 0.0399047 ,
//         0.06705362};
//     float ar2[6] = {0.11638768, 0.03987004, 2.9       , 0.11650025, 0.03990155,
//         0.0721538};
//     // float ar2[6] = {5,4,2,3,5,4};
//     // float *p = ar1[0];
//     PyObject* pb = matrix_funcs(ar1[0], 2, ar2[0], 2);
//     // cout << PyList_GET_SIZE(pb) << endl;
//     float res = funcs(ar1,ar2);
//     float t2 = timems();
//     cout << res <<"\n" << t2 -t1 << endl;
// }
