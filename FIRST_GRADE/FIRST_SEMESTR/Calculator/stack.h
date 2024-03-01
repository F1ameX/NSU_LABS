#pragma once
#ifndef CALCULATOR_STACK_H
#define CALCULATOR_STACK_H

#include <stdio.h>
#include <stdlib.h>

#define STACK struct stack


STACK
{
    int value;
    STACK* next;
};


STACK* init()
{
    STACK* terminal_element;
    terminal_element = (STACK*)malloc(sizeof(STACK));
    terminal_element->value = 0;
    terminal_element->next = NULL;
    return terminal_element;
}


void push(STACK* stack, int value)
{
    STACK* head = stack->next;
    STACK* element;
    element = (STACK*)malloc(sizeof(STACK));
    element->value = value;
    element->next = head;
    stack->next = element;
}


int is_empty(STACK* stack)
{
    if (stack->next != NULL)
        return 0;
    return 1;
}


void pop(STACK* stack)
{
    STACK* to_delete = stack->next;
    if (!is_empty(stack))
    {
        stack->next = to_delete->next;
        free(to_delete);
    }
}


int get(STACK* stack)
{
    STACK* head = stack->next;
    return head->value;
}


int get_pop(STACK* stack)
{
    STACK* head = stack->next;
    int to_pop = head->value;
    pop(stack);
    return to_pop;
}


int stack_len(STACK* stack)
{
    int len = 0;
    STACK* current = stack;
    while (current->next)
    {
        len++;
        current = current->next;
    }
    return len;
}


void clear(STACK* stack)
{
    while (stack->next)
        pop(stack->next);
}

#endif //CALCULATOR_STACK_H