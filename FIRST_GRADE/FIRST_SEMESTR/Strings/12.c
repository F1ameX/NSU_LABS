#include "tools.h"
#include <string.h>


int isValidLtr(char c)
{
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}


int isValidDgt(char c)
{
    return (c >= '0' && c <= '9');
}


int isValidPython(char c)
{
    return isValidDgt(c) || isValidLtr(c) || c == '_';
}


int isKeyword(char* str) {
    char * keywords[]= {"False", "None", "True", "and", "as",
                        "assert", "async", "await","break", "class",
                        "continue", "def", "del", "elif", "else",
                        "except","finally", "for", "from", "global",
                        "if", "import", "in", "is", "lambda",
                        "nonlocal", "not", "or", "pass", "raise",
                        "return", "try", "while", "with", "yield"};

    for (int i = 0; i < 35; i++)
        if (strcmp(str, keywords[i]) == 0)
            return 1;
    return 0;
}


int main() {
    int len, valid = 1;
    char *var;
    var = getStrl(&len);

    if (!isValidLtr(var[0]) || isKeyword(var)) {
        puts("This variable name can't use in python");
        return 0;
    }
    
    else {
        for(int i = 1; i < len; i++)
            if(!isValidPython(var[i])) {
                puts("This variable name can't use in python");
                return 0;
            }
    }
    puts("This variable name can use in python");
    return 0;
}
