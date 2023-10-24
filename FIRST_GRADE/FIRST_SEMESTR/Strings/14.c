#include "tools.h"


void change(char* answer, char* cipher, char c, int len){
    for(int i = 0; i < len; i++)
        if (answer[i] == c)
            cipher[i] = c;
}


int main() {
    int len, type;
    char symb, *tip, *answer, *cipher, *attempt;
    tip = getStr();
    answer = getStrl(&len);
    cipher = (char *)malloc(sizeof(char) * (len + 1));

    for(int i = 0; i < len; i++)
        cipher[i] = '*';
    cipher[len] = '\0';

    for(int i = 0; i < 25; i++)
        puts("\n");

    printf("%s\n", tip);

    for(int i = 0; i < 10; i++) {
        printf("%s\n", cipher);
        printf("Letter or word (0 - letter, 1 - word)?");
        scanf_s("%d\n", &type);

        if (type == 0) {
            scanf_s("%c", &symb);
            change(answer, cipher, symb, len);
        }
        else if (type == 1) {
            attempt = getStr();
            if (!strcmp(answer, attempt)) {
                puts("Victory!");
                return 0;
            }
            else {
                puts("Loss!");
                return 0;
            }
        }

        if (!count(cipher, '*')) {
            puts("Victory!");
            return 0;
        }
    }
    puts("Loss!");
    return 0;
}
