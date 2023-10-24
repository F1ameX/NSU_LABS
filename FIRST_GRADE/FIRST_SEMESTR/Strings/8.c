#include "tools.h"
#include <string.h>


int compare(const void *a, const void *b)
{
    return strlen(*(char **)a) - strlen(*(char **)b);
}


int main() {
    int len, wrdCnt = 0;
    char* input, *token, **words;

    input = getStrl(&len);
    words = spaceSplit(input, &wrdCnt);
    qsort(words, wrdCnt, sizeof(char *), compare);

    for(int i = 0; i < wrdCnt; i++)
        printf("%s ",words[i]);

    return 0;
}
