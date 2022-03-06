#include <stdio.h>
// #include <stdlib.h>
#include <cmath>
#include "dis_compute.h"

const Point ZERO_POINT(0, 0, 0);
const Point DELTA_P(1e-6, 1e-6, 1e-6);

Line::Line(Point pa, Point pb):p1(pa), p2(pb), p(ZERO_POINT), e(ZERO_POINT) {
    length();
    orient();
}
// Line::~Line();
void Line::length() {
    leng = sqrt((p1.x-p2.x)*(p1.x-p2.x)+(p1.y-p2.y)*(p1.y-p2.y)+(p1.t-p2.t)*(p1.t-p2.t));
}
void Line::orient() {
    e = Point(p2.x - p1.x, p2.y - p1.y, p2.t - p1.t);
}

Distance::Distance(Line l1, Line l2):la(l1), lb(l2),
        p_vector(ZERO_POINT, ZERO_POINT), cross_vector(ZERO_POINT, ZERO_POINT) {
}
// Distance::~Distance();
void Distance::p_vectors() {
    p_vector = Line(la.p1, lb.p1);
}
const Point Distance::cross_operate(const Point& p1, const Point& p2) {
    // x y t
    // A X B = ya * tb - ta * yb,ta*xb-xa*tb,xa*yb-ya*xb
    float x = p1.y * p2.t - p1.t * p2.y;
    float y = p1.t * p2.x - p1.x * p2.t;
    float t = p1.x * p2.y - p1.y * p2.x;
    return Point(x, y, t);
}
const float Distance::dot_operate(const Point& p1, const Point& p2) {
    return p1.x * p2.x + p1.y * p2.y + p1.t * p2.t;
}
const Point Distance::add_operate(const Point& p1, const Point& p2) {
    return Point(p1.x + p2.x, p1.y + p2.y, p1.t + p2.t);
}
void Distance::linea_mid_p() {
    float mode = cross_vector.leng * cross_vector.leng;
    la_mid_p = - dot_operate(cross_operate(p_vector.e, lb.e), cross_vector.e)/mode;
}
void Distance::lineb_mid_p() {
    float mode = cross_vector.leng * cross_vector.leng;
    lb_mid_p = - dot_operate(cross_operate(p_vector.e, la.e), cross_vector.e)/mode;
}
void Distance::origin_distance() {
    origin_dis = abs(dot_operate(p_vector.e, cross_vector.e))/sqrt(dot_operate(cross_vector.e, cross_vector.e));
}
void Distance::finial_distance() {
    float map_a = l_p_map(la_mid_p);
    float map_b = l_p_map(lb_mid_p);
    float f_dis = sqrt(pow(map_b*lb.leng, 2)+pow(map_a*la.leng, 2)+origin_dis*origin_dis);
    finial_dis = f_dis/sqrt(dot_operate(la.e, lb.e)+la.leng*lb.leng);
}
float Distance::l_p_map(const float& x) {
    if (x < 0) {
        return x;
    } else if (x < 1) {
        return 0;
    } else {
        return x - 1;
    }
}
float Distance::execute() {
    p_vectors();
    cross_vector = Line(ZERO_POINT, add_operate(cross_operate(lb.e, la.e), DELTA_P));
    linea_mid_p();
    lineb_mid_p();
    origin_distance();
    finial_distance();
    return finial_dis;
}

