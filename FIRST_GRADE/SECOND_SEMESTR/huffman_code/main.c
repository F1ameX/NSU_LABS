#include <locale.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>


typedef struct Node
{
    wchar_t symbol;
    int frequency;
    struct Node* left;
    struct Node* right;
} Node;


typedef struct PriorityQueue
{
    Node** heap;
    int capacity;
} PriorityQueue;


typedef struct HuffmanCode
{
    wchar_t symbol;
    char code[256];
} HuffmanCode;


PriorityQueue* init_queue()
{
    PriorityQueue* queue = (PriorityQueue*)malloc(sizeof(PriorityQueue));
    queue->heap = NULL;
    queue->capacity = 0;
    return queue;
}


void resize_queue(PriorityQueue* queue, int capacity)
{
    queue->heap = (Node **)realloc(queue->heap, capacity * sizeof(Node *));
    queue->capacity = capacity;
}


Node* create_node(wchar_t symbol, int frequency)
{
    Node* node = (Node *)malloc(sizeof(Node));
    node->symbol = symbol;
    node->frequency = frequency;
    node->left = NULL;
    node->right = NULL;
    return node;
}


void enqueue(PriorityQueue* queue, Node* node)
{
    resize_queue(queue, queue->capacity + 1);
    int idx = queue->capacity - 1;
    while (idx > 0 && node->frequency >= queue->heap[idx - 1]->frequency)
    {
        queue->heap[idx] = queue->heap[idx - 1];
        idx--;
    }
    queue->heap[idx] = node;
}


Node* combine_nodes(Node* left, Node* right)
{
    Node* combined = create_node(L'\0', left->frequency + right->frequency);
    combined->left = left;
    combined->right = right;
    return combined;
}


void build_huffman_code(HuffmanCode** huffman_array, int* huffman_len, Node* root, char* code, int depth)
{
    if (root == NULL)
        return;

    if (root->left == NULL && root->right == NULL)
    {
        HuffmanCode huffman_code;
        huffman_code.symbol = root->symbol;
        strcpy(huffman_code.code, code);
        *huffman_array = realloc(*huffman_array, (*huffman_len + 1) * sizeof(HuffmanCode));
        (*huffman_array)[*huffman_len] = huffman_code;
        (*huffman_len)++;
        return;
    }

    code[depth] = '0';
    code[depth + 1] = '\0';
    build_huffman_code(huffman_array, huffman_len, root->left, code, depth + 1);

    code[depth] = '1';
    code[depth + 1] = '\0';
    build_huffman_code(huffman_array, huffman_len, root->right, code, depth + 1);
}


void code_data(int *huffman_len, HuffmanCode *huffman_array)
{
    FILE* input_file, *output_file;
    input_file = fopen("in.txt", "r+");

    PriorityQueue* queue = init_queue();
    wchar_t c;
    int found_flag;
    char code[256] = "";

    while (fwscanf(input_file, L"%lc", &c) == 1)
    {
        Node* symbol_node = NULL;
        found_flag = 0;

        for (int i = 0; i < queue->capacity; i++)
        {
            if (queue->heap[i]->symbol == c)
            {
                queue->heap[i]->frequency++;

                while (i > 0 && queue->heap[i]->frequency >= queue->heap[i - 1]->frequency)
                {
                    Node* temp = queue->heap[i];
                    queue->heap[i] = queue->heap[i - 1];
                    queue->heap[i - 1] = temp;
                    i--;
                }

                found_flag = 1;
                break;
            }
        }

        if (!found_flag)
        {
            symbol_node = create_node(c, 1);
            enqueue(queue, symbol_node);
        }
    }

    fclose(input_file);

    while (queue->capacity > 1)
    {
        Node* left = queue->heap[--queue->capacity];
        Node* right = queue->heap[--queue->capacity];
        Node* combined = combine_nodes(left, right);
        enqueue(queue, combined);
    }

    build_huffman_code(&huffman_array, huffman_len, queue->heap[0], code, 0);

    input_file = fopen("in.txt", "r+");
    output_file = fopen("out.txt", "w+");

    while (fwscanf(input_file, L"%lc", &c) == 1)
    {
        for (int i = 0; i < *huffman_len; i++)
        {
            if (huffman_array[i].symbol == c)
            {
                fprintf(output_file, "%s", huffman_array[i].code);
                break;
            }
        }
    }
    fclose(input_file);
    fclose(output_file);
}


void decode_data(int *huffman_len, HuffmanCode *huffman_array)
{
    FILE* input_file, *output_file;
    input_file = fopen("in.txt", "r+");
    output_file = fopen("out.txt", "w+");
    int len = 0;
    char bit, *buffer = (char *)malloc(sizeof(char));

    while (fscanf(input_file, "%c", &bit) == 1)
    {
        if (bit == '0' || bit == '1')
        {
            buffer[len++] = bit;
            buffer = realloc(buffer, len + 1);
            buffer[len] = '\0';

            for (int i = 0; i < *huffman_len; i++)
            {
                if (strcmp(buffer, huffman_array[i].code) == 0)
                {
                    fprintf(output_file,"%lc", huffman_array[i].symbol);
                    len = 0;
                    break;
                }
            }
        }
    }

    free(buffer);
    fclose(input_file);
    fclose(output_file);
}


int main(int argc, char *argv[])
{
    setlocale(LC_ALL, "");
    int huffman_len = 0;
    HuffmanCode* huffman_array = (HuffmanCode*)malloc(huffman_len);
    char* flag = argv[1];

    if (strcmp(flag, "c") == 0)
    {
        code_data(&huffman_len, huffman_array);
        return 0;
    }
    else if (strcmp(flag, "d") == 0)
        decode_data(&huffman_len, huffman_array);

    return 0;
}
