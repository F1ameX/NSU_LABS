#include "stack.h"
#include <stdlib.h>


void init_stack(Stack* stack, int size)
{
    stack->data = (int *)malloc(size * sizeof(int));
    stack->top = -1;
}


int pop(Stack* stack)
{
    return stack->data[stack->top--];
}


void push(Stack* stack, int value)
{
    stack->data[++stack->top] = value;
}
