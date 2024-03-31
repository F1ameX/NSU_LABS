#pragma once


typedef struct Stack {
    int* data;
    int top;
} Stack;


void init_stack(Stack* stack, int size);
int pop(Stack* stack);
void push(Stack* stack, int value);
