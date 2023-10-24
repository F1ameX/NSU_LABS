#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>


void swap(char* a, char* b) /*Swap char variables values*/
{
    char tmp = *a;
    *a = *b;
    *b = tmp;
}


void reverse(char *p, int perm_idx) { /*Reverse "tail" of char string*/
    int len = strlen(p), j =0;    /*j - index of one swap cycle*/
    for (int i = perm_idx + 1; j < (len - perm_idx - 1) / 2; i++)
    {
        /*Reversing tail by using swap first and last values*/
        swap(&p[i], &p[len - j - 1]);
        j++;
    }
}


int errors(char *p)                 /*Bad input recognizing function*/
{
    int len = strlen(p);

    for (int i = 0; i < len; i++) {
        /*Check if symbol not a number*/
        if (p[i] < '0' || p[i] > '9')
            return 1;
        else
        {
        /*Check if duplicates in a string*/
            for (int j = 0; j < len; j++)
                if (p[i] == p[j] && i != j)
                    return 1;
        }
    }
    return 0;
}


int decline(char *p) {                /*Find first decline in a string*/
    int len = strlen(p);

    for (int i = len - 1; i > 0; i--) {
        if (p[i] > p[i - 1]) {
            return i - 1;
            /*If decline found - return prev index of the tail`s head*/
        }
    }
    return -1; /*If decline did not find*/

}


/*Find lexicographical minimum index in the string*/
int lex_min(char* p, int perm_idx) {
    int perm_val = p[perm_idx] + '0', min = INT_MAX, idx;

    /*Iterate through the string, starting from the provided perm_idx*/
    for (int i = perm_idx + 1; i < strlen(p); i++)
    {
        /*Check if the character's value is greater than perm_val
         *and less than the current minimum*/
        if (p[i] + '0' > perm_val && p[i] + '0' < min)
        {
            min = p[i] + '0';
            idx = i;
        }
    }
    /*Return the index of the lexicographical minimum character*/
    return idx;
}


/*Getting dynamic string while user won`t press enter*/
char* get_str()
{
    int len = 0, capacity = 1;
    char* str = (char *)malloc(sizeof(char)), c = getchar();

    while (c != '\n')
    {
        str[len++] = c;

        /*Change capacity and reallocate memory if len is out limits*/
        if (len >= capacity)
        {
            capacity *= 2;
            str = (char *)realloc(str, capacity * sizeof(char));
        }
        c = getchar();
    }
    /* 'Close' the string with the EOS symbol*/
    str[len++] = '\0';
    return str;
}


/*Output next N lexicographical permutations of p-string*/
void dijkstra_permutation(char *p, int N) {
    int perm_idx, lex_minIdx;
    char tmp;

    for (int i = 0; i < N; i++)
    {
        /*Taking permutation index in decline position
         *If there are no decline positions end function because
         *lexicographical maximum already achieved*/
        perm_idx = decline(p);

        if (perm_idx == -1)
            return;
        /*Swap permutation and lexicographical minimum index and reverse 'tail'*/
        lex_minIdx = lex_min(p, perm_idx);
        swap(&p[perm_idx], &p[lex_minIdx]);
        reverse(p, perm_idx);

        puts(p);
    }
}


int main(){
    int N;
    char *p;

    p = get_str();
    scanf_s("%d",&N);

    if (errors(p)) {
        puts("bad input");
        return 0;
    }

    dijkstra_permutation(p,N);
    free(p);

    return 0;
}