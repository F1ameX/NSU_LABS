#include "tools.h"
#include <string.h>


int main() {
    int len, wrdCnt;
    char* input, *token, **words;
    input = getStrl(&len);
    words = (char **)malloc(sizeof(char *) * count(input, ' '));
    words = spaceSplit(input, &wrdCnt);

    for(int i = 0; i < wrdCnt; i++){
        for(int j = i + 1; j < wrdCnt; j++){
            if(strcmp(words[i], words[j]) == 0)
                printf("%s ", words[i]);
        }
    }
    return 0;
}
