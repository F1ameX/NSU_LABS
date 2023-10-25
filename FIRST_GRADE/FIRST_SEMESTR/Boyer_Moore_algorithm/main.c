#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>

#define TEMPLATE_LEN (16 + 1)
#define INITIAL_VAL 1


int shift(char* template, char symbol, int template_len)
{
    for(int i = template_len - 2; i >= 0; i--)
        if (template[i] == symbol)
            return template_len - i - 1;
    return template_len;
}


int comparison(char* text, char* template, int check_idx, int template_len)
{
    for(int i = 0; i < template_len; i++)
    {
        printf("%d ", check_idx - i + INITIAL_VAL);
        if (template[template_len - i - 1] != text[check_idx - i])
            return shift(template, text[check_idx], template_len);
    }
    return shift(template, template[check_idx - template_len], template_len);
}


int main()
{
    int text_len = 0, template_len, check_idx, template_idx = 1, symbol;
    char *text, template[TEMPLATE_LEN];

    gets(template);
    template_len = strlen(template);

    text = (char *)malloc(sizeof(char) * 0);
    symbol = getc(stdin);
    check_idx = template_len - 1;

    while (symbol != EOF)
    {
        text_len++;
        text = (char *)realloc(text, text_len * sizeof(char));
        *(text + text_len - 1) = (char)symbol;
        symbol = getc(stdin);

    }

    while (check_idx < text_len)
        check_idx += comparison(text, template, check_idx, template_len);

    return 0;
}
