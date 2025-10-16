#ifndef MYTHREAD_H
#define MYTHREAD_H

#define _GNU_SOURCE
#include <stddef.h>
#include <stdatomic.h>

#ifndef STACK_SIZE
#define STACK_SIZE 8192
#endif

typedef struct {
    atomic_int completed;  
    atomic_int detached;
    atomic_int joined;

    void *(*start_routine)(void *);
    void *arg;
    void *retval;
    void *stack;
} mythread_t;

int mythread_create(mythread_t *thread, void *(*start_routine)(void *), void *arg);
int mythread_join(mythread_t *thread, void **retval);
int mythread_detach(mythread_t *thread);

#endif