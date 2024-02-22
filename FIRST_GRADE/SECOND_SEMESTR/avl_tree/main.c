#include "avl_tree.h"
#include <stdio.h>


int main() {
    int N, value;
    scanf("%d", &N);

    AVL_TREE* root = NULL;

    for (int i = 0; i < N; i++) {
        scanf("%d", &value);
        if (root == NULL)
            root = create_node(value);
        else
            insert(root, value);
    }

    printf("%d\n", get_height(root) + 1);
    delete_tree(root);
    return 0;
}
