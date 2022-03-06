#ifndef DIS_COMPUTE_H_
#define DIS_COMPUTE_H_
#include <iostream>
#include <stdlib.h>
#include <stdio.h>

using namespace std;

class Point {
 public:
    float x;
    float y;
    float t;

    Point(float x_ , float y_ , float t_):x(x_), y(y_), t(t_) {}
   //  ~Point();
};

class Line {
 public:
    void length();
    void orient();

    Line(Point pa, Point pb);
   //  ~Line();
 public:
    Point p1;
    Point p2;
    Point p;
    Point e;
    float leng;
};

class Distance {
 private:
    /* data */
    Line la;
    Line lb;
    Line p_vector;
    Line cross_vector;
    float la_mid_p;
    float lb_mid_p;
    float origin_dis;
    float finial_dis;
 public:
    Distance(Line l1, Line l2);
   //  ~Distance();
    void p_vectors();
    const Point cross_operate(const Point&, const Point&);
    const float dot_operate(const Point&, const Point&);
    const Point add_operate(const Point&, const Point&);
    void linea_mid_p();
    void lineb_mid_p();
    float l_p_map(const float&);
    void origin_distance();
    void finial_distance();
    float execute();
};
#endif
