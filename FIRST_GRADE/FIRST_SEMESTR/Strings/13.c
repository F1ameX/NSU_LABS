#include "tools.h"


int isLuck(int* arr, int len){
    int leftExp = 0, rightExp = 0;

    if (len % 2 != 0)
        return 0;

    for(int i = 0; i < len / 2; i ++) {
        leftExp += arr[i];
        rightExp += arr[len - i - 1];
    }

    if (leftExp == rightExp)
        return 1;
    else
        return 0;
}


int main() {
    int len, cnt = 1, *number;
    char* input;

    input = getStrl(&len);
    number = (int *)malloc(sizeof(int) * len);
    convert(input, number);

    while (isLuck(number, len) == 0){
        cnt++;
        input = getStrl(&len);
        number = (int *)malloc(sizeof(int) * len);
        convert(input, number);
    }

    printf("Congratulations! You enterd lucky number! Ordinal number is %d", cnt);
    return 0;
}
