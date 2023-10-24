#include "tools.h"
#include <string.h>


int main() {
    int len, wrdCnt = 0;
    char* input, *token, **words;
    input = getStrl(&len);
    toLower(input, len);
    words = (char **)malloc(sizeof(char *) * count(input, ' '));
    words = spaceSplit(input, &wrdCnt);

    for(int i = 1; i < wrdCnt; i++) {
        if (words[i - 1][strlen(words[i - 1]) - 1] != words[i][0]){

            if (i % 2 == 0){
                puts("Ivan");
                return 0;
            }

            else{
                puts("Peter");
                return 0;
            }
        }
    }

    if (wrdCnt % 2 == 0)
        puts("Ivan");
    else
        puts("Peter");

    return 0;
}
