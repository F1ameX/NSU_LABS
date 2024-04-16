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


void save_huffman_code(HuffmanCode *huffman_array, int huffman_len)
{
    FILE* data_file = fopen("data.txt", "r+");
    for (int i = 0; i < huffman_len; i++)
        fprintf(data_file, "_%lc %s\t", huffman_array[i].symbol, huffman_array[i].code);
    fclose(data_file);
}


void load_huffman_code(HuffmanCode **huffman_array, int *huffman_len)
{
    FILE *data_file = fopen("data.txt", "r");
    wchar_t symbol;
    char code[256] = "";
    int is_code = 0, len_code = 0;

    while ((symbol = getwc(data_file)) != WEOF)
    {
        if (symbol == L'_')
        {
            symbol = getwc(data_file);
            *huffman_array = realloc(*huffman_array, (*huffman_len + 1) * sizeof(HuffmanCode));
            (*huffman_array)[*huffman_len].symbol = symbol;
            is_code = 1;
        }
        else if ((symbol == L'0' || symbol == L'1') && is_code)
        {
            code[len_code++] = (char)symbol;
            code[len_code] = '\0';
        }
        else if (symbol == L'\t')
        {
            strcpy((*huffman_array)[*huffman_len].code, code);
            (*huffman_len)++;
            is_code = 0;
            len_code = 0;
        }
    }

    fclose(data_file);
}


int is_tree()
{
    wchar_t symbol;
    char code[256];
    FILE* data_input;
    data_input = fopen("data.txt", "r+");
    if (fscanf(data_input, "_%lc %s", &symbol, code) == 2)
        return 1;
    return 0;
}


void code_data(int *huffman_len, HuffmanCode *huffman_array)
{

    FILE* input_file, *data_input, *output_file;
    input_file = fopen("in.txt", "r+");
    data_input = fopen("data.txt", "r+");

    if (is_tree() == 1)
        return;

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
    save_huffman_code(huffman_array, *huffman_len);
    fclose(input_file);
    fclose(output_file);
}


void decode_data(int *huffman_len, HuffmanCode *huffman_array)
{

    FILE* input_file, *output_file;
    input_file = fopen("in.txt", "r");
    output_file = fopen("out.txt", "w");
    char bit;
    char buffer[256];
    int len = 0;
    load_huffman_code(&huffman_array, huffman_len);

    if (is_tree() == 0)
        return;
    while (fscanf(input_file, "%c", &bit) == 1)
    {
        if (bit == '0' || bit == '1')
        {
            buffer[len++] = bit;
            buffer[len] = '\0';
            for (int i = 0; i < *huffman_len; i++)
            {
                if (strcmp(buffer, huffman_array[i].code) == 0)
                {
                    fprintf(output_file, "%lc", huffman_array[i].symbol);
                    len = 0;
                    break;
                }
            }
        }
    }

    fclose(input_file);
    fclose(output_file);
}


int main(int argc, char *argv[])
{
    setlocale(LC_ALL, "");
    int huffman_len = 0;
    HuffmanCode* huffman_array = (HuffmanCode*)malloc(huffman_len * sizeof(HuffmanCode));

    char* flag = argv[1];

    if (strcmp(flag, "c") == 0)
        code_data(&huffman_len, huffman_array);
    else if (strcmp(flag, "d") == 0)
        decode_data(&huffman_len, huffman_array);

    return 0;
}
