#include <stdio.h>
#include "tools.h"


int main(){
    int len, cnt;
    char* input;
    input = getStr();

    for(int i = 0; i < strlen(input); i++) {
        cnt = 0;
        for(int j = 0; j < strlen(input); j++) {
            if (input[i] == input[j])
                cnt++;
        }
        
        if (cnt == 3) {
            printf("%c", input[i]);
            return 0;
        }
    }
    
    puts("There is no symbol that repeated 3 times");
    return 0;
}
