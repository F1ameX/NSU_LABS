#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>


void swap(int* a, int* b)
{
    int tmp = *a;
    *a = *b;
    *b = tmp;
}


void quick_sort(int* array, int left, int right)
{
    int checker = array[(left + right) / 2], i = left, j = right;

    if (left < right)
    {
        while (i <= j)
        {
            while (array[i] < checker)
                i++;

            while (array[j] > checker)
                j--;

            if (i <= j)
                swap(&array[i++], &array[j--]);
        }
        quick_sort(array, left, j);
        quick_sort(array, i, right);
    }
}


int main()
{
    int N, *array;
    scanf_s("%d", &N);
    array = (int*)malloc(sizeof(int) * N);

    for (int i = 0; i < N; i++)
        scanf_s("%d", &array[i]);

    quick_sort(array, 0, N - 1);

    for (int i = 0; i < N; i++)
        printf("%d ", array[i]);

    free(array);
    return 0;
}
