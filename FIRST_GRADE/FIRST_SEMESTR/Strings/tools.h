#ifndef LABS_TOOLS_H
#define LABS_TOOLS_H

#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <math.h>
#include <string.h>


int max(int num1, int num2){
    if(num1 > num2)
        return num1;
    return num2;
}


int min(int num1, int num2){
    if(num1 < num2)
        return num1;
    return num2;
}


int count(char* str, char symb){
    int cnt = 0;
    for(int i = 0; i < strlen(str); i++)
        if (str[i] == symb)
            cnt++;
    return cnt;
}


int hasDups(char* str){
    int len = strlen(str);
    for(int i = 0; i < len - 1; i++)
        for(int j = i + 1; j < len; j++)
            if (str[i] == str[j])
                return 1;
    return 0;
}


char** spaceSplit(char *input, int* len){
    *len = 0;
    char* token,** str = (char **)malloc(sizeof(char *) * count(input, ' '));
    token = strtok(input, " ");
    while(token != NULL){
        str[(*len)++] = strdup(token);
        token = strtok(NULL, " ");
    }
    return str;
}


void push(char* str, char symbol){
    int len = strlen(str);
    str[len++] = symbol;
    str[len++] = '\0';
    str = (char *)realloc(str, len * sizeof(char));
}


char *getStr(){
    int len = 0, capacity = 1;
    char *str = (char*)malloc(sizeof(char)), c = getchar();
    while (c != '\n'){
        str[len++] = c;
        if (len >= capacity){
            capacity *= 2;
            str = (char*)realloc(str, capacity * sizeof(char));
        }
        c = getchar();
    }
    str[len] = '\0';
    return str;
}


char *getStrl(int *len){
    *len = 0;
    int capacity = 1;
    char *str = (char*) malloc(sizeof(char)), c = getchar();
    while (c != '\n') {
        str[(*len)++] = c;
        if (*len >= capacity) {
            capacity *= 2;
            str = (char*)realloc(str, capacity * sizeof(char));
        }
        c = getchar();
    }
    str[*len] = '\0';
    return str;
}


void toLower(char* str, int len){
    for(int i = 0; i < len; i++)
        if (str[i] >= 'A' && str[i] <= 'Z')
            str[i] += 32;
}


char* makEmpty(){
    char* str;
    str = (char *)malloc(0);
    str[0] = (char)0;
    return str;
}


void convert(char* inputArr, int* outputArr){
    for(int i = 0; i < strlen(inputArr); i++)
        outputArr[i] = inputArr[i] - '0';
}


#endif //LABS_TOOLS_H
