#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include "stack.h"

/*Two num constants that over limit of int size to return errors*/
#define SYNTAX_ERROR (INT16_MAX + 1)
#define DIV_BY_ZERO (INT16_MAX + 2)


/*Function of recognizing operand in stack*/
int is_operand(char symbol)
{
    switch (symbol)
    {
        case '(':
            return 3;

        case ')':
            return 2;

        case '+':
        case '-':
        case '*':
        case '/':
            return 1;

        default:
            return 0;
    }
}


/*Function of recognizing operand priority on stack calculations*/
int operand_priority(char symbol)
{
    switch (symbol)
    {
        case '*':
        case '/':
            return 4;

        case '+':
        case '-':
            return 3;

        case ')':
            return 2;

        case '(':
            return 1;

        default:
            return 0;
    }
}


/*Function of getting dynamic any len string*/
char* get_string(int* len)
{
    *len = 0;

    int capacity = 1;
    char* string = (char *)malloc(sizeof(char)), symbol = getchar();

    /*Error handler only "enter-symbol" strings*/
    if (symbol == '\n')
        return "X";

    /*Loop of getting symbol, adding to string and reallocating memory*/
    while (symbol != '\n')
    {
        string[(*len)++] = symbol;

        if (*len >= capacity)
        {
            capacity *= 2;
            string = (char *)realloc(string, sizeof(char) * capacity);
        }

        symbol = getchar();
    }
    /*On the end of the string adding corresponding symbol
     * that means end of the line*/
    string[*len] = '\0';
    return string;
}


/*Function of translation infix calculator expression to postfix expression*/
char* to_postfix(char* infix_expression, int len)
{
    int priority, postfix_iterator = 0;
    char symbol, *postfix_expression = (char *)malloc(sizeof(char) * len * 2);
    STACK* operator_stack = init();

    if (operand_priority(infix_expression[0]) > 1 || is_operand(infix_expression[len - 1]) > 2)
        return "X";

    for (int i = 0; i < len; i++)
    {
        if (isdigit(infix_expression[i]))
            postfix_expression[postfix_iterator++] = infix_expression[i];

        else if (is_operand(infix_expression[i]))
        {
            /*If met operand, adding spaces to work normally
             * with two or more digit numbers*/
            postfix_expression[postfix_iterator++] = ' ';

            /*If met first closing circle bracker - return error*/
            if (is_empty(operator_stack) && infix_expression[i] == ')')
                return "X";

            else if (is_empty(operator_stack))
                push(operator_stack, infix_expression[i]);

            else
            {
                if (infix_expression[i] == '(')
                    push(operator_stack, (int)infix_expression[i]);

                else if (infix_expression[i] == ')')
                {
                    /*If met wrong combination of circle bracket - return error*/
                    if (i == 0 || infix_expression[i-1] == '(')
                        return "X";

                    symbol = (char)get_pop(operator_stack);

                    while (symbol != '(')
                    {
                        postfix_expression[postfix_iterator++] = symbol;
                        symbol = (char)get_pop(operator_stack);
                    }
                }

                else
                {
                    /*Getting priority of operand in string
                     * and value of operand in stack*/
                    priority = operand_priority(infix_expression[i]);
                    symbol = (char)get(operator_stack);

                    while(operand_priority(symbol) >= priority)
                    {
                        postfix_expression[postfix_iterator++] = symbol;
                        pop(operator_stack);
                        if (is_empty(operator_stack))
                            break;
                        symbol = (char)get(operator_stack);
                    }

                    push(operator_stack, (int)infix_expression[i]);
                }
            }
        }
        /*If met wrong symbol - return error*/
        else
            return "X";
    }
    while (!is_empty(operator_stack))
        postfix_expression[postfix_iterator++] = (char)get_pop(operator_stack);

    /*Removing spaces at the end of string, reallocate and delete useless memory*/
    while (postfix_iterator > 0 && postfix_expression[postfix_iterator - 1] == ' ') {
        postfix_iterator--;
    }

    postfix_expression[postfix_iterator] = '\0';
    postfix_expression = (char *)realloc(postfix_expression, sizeof(char) * (postfix_iterator + 1));

    clear(operator_stack);
    return postfix_expression;
}


/*Stack calculations function*/
long int calculator(char* postfix_expression)
{
    int operand_1, operand_2, number, result, iterator = 0;
    STACK* calculator_stack = init();

    while (iterator < strlen(postfix_expression))
    {
        while (postfix_expression[iterator] == ' ')
            iterator++;

        if (isdigit(postfix_expression[iterator]))
        {
            /*Cycle of wo or more digit numbers crunching*/
            while (isdigit(postfix_expression[iterator]))
            {
                number = number * 10 + postfix_expression[iterator] - '0';
                iterator++;
            }

            push(calculator_stack, number);
            number = 0;
        }

        else
        {
            /*If met the operand and calculator stack empty
             *or has only 1 value - return error*/
            if (is_empty(calculator_stack) || stack_len(calculator_stack) == 1)
                return SYNTAX_ERROR;

            operand_2 = get_pop(calculator_stack);
            operand_1 = get_pop(calculator_stack);

            /*Calculating the resul of operation and push it back*/
            switch (postfix_expression[iterator])
            {
                case '+':
                    result = operand_1 + operand_2;
                    break;

                case '-':
                    result = operand_1 - operand_2;
                    break;

                case '*':
                    result = operand_1 * operand_2;
                    break;

                case '/':
                    if (operand_2 == 0)
                        return DIV_BY_ZERO;
                    else
                        result = operand_1 / operand_2;
                    break;
            }

            push(calculator_stack, result);
            iterator++;
        }
    }

    result = get(calculator_stack);
    return result;
}


int main()
{
    int len;
    char* expression, *postfix_expression;

    expression = get_string(&len);
    postfix_expression = to_postfix(expression, len);

    /*Error handler of infix and postfix expressions*/
    if (expression[0] == 'X' || postfix_expression[0] == 'X')
    {
        puts("syntax error");
        return 0;
    }

    /*Checker of calculations result that recognizing error*/
    switch (calculator(postfix_expression))
    {
        case SYNTAX_ERROR:
            puts("syntax error");
            return 0;

        case DIV_BY_ZERO:
            puts("division by zero");
            return 0;

        default:
            printf("%ld", calculator(postfix_expression));
            return 0;
    }

}