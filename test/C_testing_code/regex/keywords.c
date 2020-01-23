#include <stdio.h>
int main() {
    if (1) {
        do {
            while (1) { continue; }
        } while (1);
    } else {
        switch(1) {
            case 1:

                goto two;

                break;
            default:
        }
    }
    two:

    int x;
    short t;
    long rrr;
    float qqq;
    double aaa;
    struct ssss;
    union qqq;
    enum aaaaa;
    auto wewew;
    const int a = sizeof(x);
    register int b;
    signed int c;
    static int d;
    unsigned int e;
    volatile int f;
    typedef int g;
    extern int h;
    int y = NULL;

    return 1;
}