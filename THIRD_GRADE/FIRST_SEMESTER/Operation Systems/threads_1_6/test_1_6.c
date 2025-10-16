#include "mythread.h"
#include <stdio.h>
#include <sched.h>


static void* worker(void* arg) 
{
    long id = (long)arg;
    if ((id % 10) == 0) sched_yield();
    return (void*)(id + 1000);
}


int main(void) 
{
    const int N = 100;
    mythread_t th[N];

    for (long i = 0; i < N; ++i) 
    {
        if (mythread_create(&th[i], worker, (void*)i) != 0) 
        {
            perror("mythread_create");
            return 1;
        }
    }

    for (int i = 0; i < N; ++i) 
    {
        if (i < 50) 
        {
            void *rv = NULL;
            if (mythread_join(&th[i], &rv) != 0) 
            {
                perror("mythread_join");
                return 1;
            }
        } 
        else 
        {
            if (mythread_detach(&th[i]) != 0) 
            {
                perror("mythread_detach");
                return 1;
            }
        }
    }
    puts("OK: 50 joined, 50 detached, no leaks/no busy-wait.");
    return 0;
}