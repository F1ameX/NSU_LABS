#include "tools.h"


void game(int* secretNum, int* guessNum, int* bulls, int* cows, int len){
    *bulls = 0, *cows = 0;

    for (int i = 0; i < len; i++) {
        if (secretNum[i] == guessNum[i])
            (*bulls)++;
        else
            for (int j = 0; j < len; j++)
                if (secretNum[i] == guessNum[j] && i != j) {
                    (*cows)++;
                    break;
                }
    }
}




int main() {
    int len, *intSecretNum, *intGuessNum, bulls, cows;
    char* secretNum, *guessNum;

    secretNum = getStrl(&len);
    intSecretNum = (int *)malloc(sizeof(int) * len);
    intGuessNum = (int *)malloc(sizeof(int) * len);
    convert(secretNum, intSecretNum);

    for(int i = 0; i < 25; i++)
        puts("\n");

    for(int i = 0; i < 10; i++) {
        guessNum = getStr();
        convert(guessNum, intGuessNum);
        game(intSecretNum, intGuessNum, &bulls, &cows, len);
        printf("Bulls: %d Cows: %d\n", bulls, cows);
        
        if (bulls == len) {
            puts("Victory!");
            return 0;
        }
    }
    
    puts("Loss!");
    return 0;
}
