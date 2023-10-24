#include "tools.h"


int minWord(char* input){
    int cnt = 0, result = INT_MAX;
    for(int i = 0; i < strlen(input); i++){
        if (input[i] != ' ')
            cnt++;
        else {
            result = min(cnt, result);
            cnt = 0;
        }
    }
    result = min(cnt, result);
    return result;
}


int main(){
    int len;
    char* input, *output;
    input = getStrl(&len);
    printf("%d", minWord(input));
    return 0;
}
