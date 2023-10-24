#include "tools.h"


void uniqCharacter(char* str1, char* str2, char* str3){
    int chrCnt1[256] = {0}, chrCnt2[256] = {0}, chrCnt3[256] = {0};

    for(int i = 0; i < strlen(str1); i++)
        chrCnt1[(int)str1[i]] = 1;

    for(int i = 0; i < strlen(str2); i++)
        chrCnt2[(int)str2[i]] = 1;

    for(int i = 0; i < strlen(str3); i++)
        chrCnt3[(int)str3[i]] = 1;

    for(int i = 0; i < 256; i++) {
        if (chrCnt1[i] + chrCnt2[i] + chrCnt3[i] == 1)
            putchar((char)i);
    }
}


int main(){
    char* input1, *input2, *input3;
    
    input1 = getStr();
    input2 = getStr();
    input3 = getStr();
    
    uniqCharacter(input1, input2, input3);
    return 0;
}
