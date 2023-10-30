#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>

/*The biggest possible template len + 1 the end of string symbol*/
#define TEMPLATE_LEN (16 + 1)
/*Initial value of start of counting*/
#define INITIAL_VAL 1


/*Template shift function*/
int shift(char* template, char symbol, int template_len)
{
    /*Iterate through the template from penultimate element until coincidence*/
    for(int i = template_len - 2; i >= 0; i--)
        /*On coincidence with current symbol
         *Shift to right on length to the template`s end*/
        if (template[i] == symbol)
            return template_len - i - 1;
    /*Else shift to whole template`s length*/
    return template_len;
}


/*Comparison template and text function*/
int comparison(char* text, char* template, int check_idx, int template_len)
{
    /*Iterate through the template from start to the end*/
    for(int i = 0; i < template_len; i++)
    {
        /*Output comparing id of text symbol*/
        printf("%d ", check_idx - i + INITIAL_VAL);
        /*Compare end-to-start template and text symbols
         *If they don`t match then shift index*/
        if (template[template_len - i - 1] != text[check_idx - i])
            return shift(template, text[check_idx], template_len);
    }
    /*If whole template match with part of text shift index too*/
    return shift(template, template[check_idx - template_len], template_len);
}


int main()
{
    /*Initialization text`s length, template`s length, text comparing index*/
    int text_len = 0, template_len, check_idx, symbol;
    char *text, template[TEMPLATE_LEN];
    gets(template);
    template_len = strlen(template);
    text = (char *)malloc(sizeof(char) * 0);
    symbol = fgetc(stdin);
    /*Initially - check_idx equals template`s last index*/
    check_idx = template_len - 1;

    /*Input by symbol loop while end of file won`t reached*/
    while (symbol != EOF)
    {
        text_len++;
        text = (char *)realloc(text, text_len * sizeof(char));
        text[text_len - 1] = (char)symbol;
        symbol = fgetc(stdin);
    }

    /*Changing comparing text index position*/
    while (check_idx < text_len)
        check_idx += comparison(text, template, check_idx, template_len);

    return 0;
}
