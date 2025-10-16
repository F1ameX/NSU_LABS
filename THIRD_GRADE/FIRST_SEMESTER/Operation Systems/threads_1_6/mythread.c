#define _GNU_SOURCE
#include "mythread.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#include <sched.h>
#include <sys/mman.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>


static int futex_wait(atomic_int *addr, int expected) {return syscall(SYS_futex, addr, FUTEX_WAIT, expected, NULL, NULL, 0);}
static int futex_wake(atomic_int *addr, int n) {return syscall(SYS_futex, addr, FUTEX_WAKE, n, NULL, NULL, 0);}

static int mythread_entry(void *arg) 
{
    mythread_t *thread = (mythread_t *)arg;

    thread->retval = thread->start_routine(thread->arg);
    atomic_store_explicit(&thread->completed, 1, memory_order_release);
    futex_wake(&thread->completed, 1);

    if (atomic_load_explicit(&thread->detached, memory_order_acquire) &&
        !atomic_load_explicit(&thread->joined, memory_order_relaxed)) munmap(thread->stack, STACK_SIZE);
    return 0;
}

int mythread_create(mythread_t *thread, void *(*start_routine)(void *), void *arg) 
{
    if (!thread || !start_routine) { errno = EINVAL; return -1; }

    memset(thread, 0, sizeof(*thread));
    atomic_store(&thread->completed, 0);
    atomic_store(&thread->detached, 0);
    atomic_store(&thread->joined, 0);

    thread->start_routine = start_routine;
    thread->arg = arg;
    thread->retval = NULL;

    thread->stack = mmap(NULL, STACK_SIZE, PROT_READ | PROT_WRITE,
                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

    if (thread->stack == MAP_FAILED) 
    {
        perror("mmap");
        return -1;
    }

    void *child_stack = (char *)thread->stack + STACK_SIZE;

    int flags = CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD;
    if (clone(mythread_entry, child_stack, flags, thread) == -1) 
    {
        int e = errno;
        perror("clone");
        munmap(thread->stack, STACK_SIZE);
        errno = e;
        return -1;
    }

    return 0;
}

int mythread_join(mythread_t *thread, void **retval) 
{
    if (!thread) { errno = EINVAL; return -1; }
    if (atomic_load(&thread->detached)) { errno = EINVAL; return -1; }

    for (;;) 
    {
        int done = atomic_load_explicit(&thread->completed, memory_order_acquire);
        if (done == 1) break;
        futex_wait(&thread->completed, 0);
    }

    if (retval) *retval = thread->retval;

    if (!atomic_exchange(&thread->joined, 1)) munmap(thread->stack, STACK_SIZE);
    
    return 0;
}

int mythread_detach(mythread_t *thread) 
{
    if (!thread) { errno = EINVAL; return -1; }

    atomic_store(&thread->detached, 1);

    if (atomic_load_explicit(&thread->completed, memory_order_acquire) &&
        !atomic_exchange(&thread->joined, 1)) munmap(thread->stack, STACK_SIZE);
    
    return 0;
}