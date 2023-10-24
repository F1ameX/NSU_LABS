#include "tools.h"


void printRevrs(char* input, int len){
    int end = len;
    
    for(int i = len - 1; i >= 0; i--) {
        if (input[i] == ' ') {
            for(int j = i + 1; j < end; j++)
                printf("%c", input[j]);
            printf(" ");
            end = i;
        }
        else if (i == 0)
            for(int j = 0; j < end; j++)
                printf("%c", input[j]);
    }
}


int main(){
    int len;
    char* input, *output;
    input = getStrl(&len);
    printRevrs(input, len);
    return 0;
}
