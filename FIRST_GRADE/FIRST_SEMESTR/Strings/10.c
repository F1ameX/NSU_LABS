#include "tools.h"
#include <string.h>


int main() {
    int len, wrdCnt = 0;
    char* input, *token, **words;
    input = getStrl(&len);
    words = (char **)malloc(sizeof(char *) * count(input, ' '));

    token = strtok(input, " ");
    while(token != NULL){
        if (wrdCnt == 0 || (!hasDups(token) && strcmp(token, words[0]) != 0))
            words[wrdCnt++] = strdup(token);
        token = strtok(NULL, " ");
    }

    for(int i = 1; i < wrdCnt; i++)
        printf("%s ", words[i]);

    return 0;
}
