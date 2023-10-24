#include <stdio.h>
#include "tools.h"


int spacesCnt(char* str, int len){
    int cnt = 0, result = 0;

    for(int i = 0; i < len; i++) {

        if (str[i] == ' ')
            cnt++;
        else {
            result = max(result, cnt);
            cnt = 0;
        }

    }

    result = max(result, cnt);
    return result;
}


int main(){
    int len;
    char* input;
    input = getStrl(&len);
    printf("%d", spacesCnt(input, len));
    return 0;
}
