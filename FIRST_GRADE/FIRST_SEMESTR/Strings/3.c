#include <stdio.h>
#include "tools.h"


void rmvDupsChr(char* str, int *len) {
    for(int i = 0; i < *len; i++) {
        for(int j = i + 1; j < *len;) {

            if (str[i] == str[j]) {
                for(int k = j; k < *len; k++)
                    str[k] = str[k + 1];
                *len = *len - 1;
            }

            else
                j++;
        }
    }
}


int main(){
    int len, cnt = 0;
    char* input;
    input = getStrl(&len);
    toLower(input, len);
    rmvDupsChr(input, &len);

    for(int i = 0; i < len; i++)
        if (input[i] >= 'a' && input[i] <= 'z')
            cnt++;

    printf("%d", cnt);
    return 0;
}
