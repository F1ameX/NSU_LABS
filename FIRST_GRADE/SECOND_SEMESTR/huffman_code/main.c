#include <locale.h>
#include <stdio.h>
#include <stdlib.h>
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


void print_huffman_tree(Node* root, char* code, int depth)
{
    if (root == NULL)
        return;


    if (root->left == NULL && root->right == NULL)
    {
        printf("%lc: %s\n", root->symbol, code);
        return;
    }

    code[depth] = '0';
    code[depth + 1] = '\0';
    print_huffman_tree(root->left, code, depth + 1);

    code[depth] = '1';
    code[depth + 1] = '\0';
    print_huffman_tree(root->right, code, depth + 1);
}


int main()
{
    setlocale(LC_ALL, "");
    PriorityQueue* queue = init_queue();
    FILE* input_file;
    wchar_t c;

    input_file = fopen("../in.txt", "r");

    while (fwscanf(input_file, L"%lc", &c) == 1)
    {
        Node* symbol_node = NULL;
        int found_flag = 0;

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
    char code[256] = "";
    print_huffman_tree(queue->heap[0], code, 0);
    return 0;
}
