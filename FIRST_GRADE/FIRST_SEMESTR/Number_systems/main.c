#include <stdio.h>
#include <math.h>
#include <ctype.h>
#include <string.h>


int errors(int b1, int b2, char* X) {
    int len = strlen(X), dot_cnt = 0;

    if ((b1 < 2 || b1 > 16) || (b2 < 2 || b2 > 16))
        return 1;

    for (int i = 0; i < len; i++) {
        if (X[i] == '.')
            dot_cnt++;

        if ((X[i] < '0' && X[i] != '.') || (X[i] > '9' && X[i] < 'A'))
            return 1;

        if ((X[i] >= '0' && X[i] <= '9') && ((X[i] - '0') >= b1))
            return 1;
        else if ((tolower(X[i]) >= 'a' && tolower(X[i]) <= 'f') && ((tolower(X[i]) - 'a' + 10) >= b1))
            return 1;
    }

    if (dot_cnt > 1)
        return 1;

    if (X[0] == '.' || X[len - 1] == '.')
        return 1;

    return 0;
}


double to_decimal(int b1, char* X){
    int len = strlen(X), dot_idx = len;
    double decimal_base = 0;

    for(int i = 0; i < len; i++)
        if (X[i] == '.')
            dot_idx = i;

    if (b1 == 10) {
        for(int i = 0; i < len; i++){
            if (i < dot_idx)
                decimal_base += (X[i] - '0') * pow(10, dot_idx - i - 1);
            else if (i > dot_idx)
                decimal_base += (X[i] - '0') * pow(10, dot_idx - i);
        }
    }

    else {
        for(int i = 0; i < len; i++)
            if (i < dot_idx)
                decimal_base += (isdigit(X[i])) ? (X[i] - '0') * pow(b1, dot_idx - i - 1) :
                        (tolower(X[i]) - 'a' + 10) * pow(b1, dot_idx - i - 1);
            else if (i > dot_idx)
                decimal_base += (isdigit(X[i])) ? (X[i] - '0') * pow(b1, dot_idx - i) :
                        (tolower(X[i]) - 'a' + 10) * pow(b1, dot_idx - i);
    }

    return decimal_base;
}


void to_required(int b2, double decimal_base) {
    int int_idx = 0, digit;
    long long int int_part = (long long int)decimal_base;
    double real_part = decimal_base - int_part;
    char int_partStr[64], reversed_int[64];


    for (int i = 0; i < 64; i++)
        int_partStr[i] = '0';

    while (int_part > 0) {
        int_partStr[int_idx] = (int_part % b2 <= 9) ? (int_part % b2 + '0') :(char)(int_part % b2 + 87);
        int_part /= b2;
        int_idx++;
    }

    if (int_idx == 0) {
        int_partStr[int_idx] = '0';
        int_idx++;
    }

    for (int i = 0; i < int_idx; i++)
        reversed_int[i] = int_partStr[int_idx - i - 1];

    reversed_int[int_idx] = '\0';
    printf("%s", reversed_int);

    if (real_part > 0) {
        printf(".");
        for (int i = 0; i < 12; i++) {
            real_part *= b2;
            digit = (int)real_part;
            printf("%c", (digit <= 9) ? (char)(digit + '0') : (char)(digit + 87));
            real_part -= digit;
        }
    }
}


int main(){
    int b1, b2;
    double decimal_num;
    char X[14];
    scanf_s("%d %d", &b1, &b2);
    scanf_s("%s", &X);
    if (errors(b1, b2, X)){
        puts("bad input");
        return 0;
    }

    decimal_num = to_decimal(b1, X);
    to_required(b2, decimal_num);
    return 0;
}