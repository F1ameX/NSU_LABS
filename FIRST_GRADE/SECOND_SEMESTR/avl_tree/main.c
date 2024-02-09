#include "avl_tree.h"
#include <stdio.h>
#include <stdlib.h>


int main() {
    int N;
    scanf("%d", &N);

    AVL_TREE* root = NULL;

    for (int i = 0; i < N; ++i) {
        int key;
        scanf("%d", &key);
        if (root == NULL)
            root = create_node(i, key);
        else
            insert(root, i, key);
    }
    printf("%d\n", get_height(root) + 1);

    return 0;
}