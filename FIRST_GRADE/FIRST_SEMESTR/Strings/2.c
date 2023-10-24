#include <stdio.h>
#include "tools.h"


int bigSequence(char* str, int len){
    int cnt = 1, result = 0;

    for(int i = 1; i < len; i++) {

        if (str[i - 1] == str[i])
            cnt++;
        else {
            result = max(result, cnt);
            cnt = 1;
        }

    }

    result = max(result, cnt);
    return result;
}


int main(){
    int len;
    char* input;
    input = getStrl(&len);
    printf("%d", bigSequence(input, len));
    return 0;
}
