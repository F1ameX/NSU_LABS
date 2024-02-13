#ifndef AVL_TREE_AVL_TREE_H
#define AVL_TREE_AVL_TREE_H
#pragma once

#include <stdlib.h>


int max(int num_1, int num_2)
{
    if (num_1 > num_2)
        return num_1;
    return num_2;
}


typedef struct AVL_TREE {
    int key;
    int value;
    int height;
    struct AVL_TREE* left;
    struct AVL_TREE* right;
} AVL_TREE;


int get_height(AVL_TREE* node)
{
    if (node == NULL)
        return -1;
    return node->height;
}


int get_balance(AVL_TREE* node)
{
    if (node == NULL)
        return 0;
    return get_height(node->right) - get_height(node->left);
}


void swap_node(AVL_TREE* node_1, AVL_TREE* node_2)
{
    int key_1 = node_1->key;
    int value_1 = node_1->value;

    node_1->key = node_2->key;
    node_2->key = key_1;

    node_1->value = node_2->value;
    node_2->value = value_1;
}


void update_height(AVL_TREE* node)
{
    node->height = max(get_height(node->left), get_height(node->right)) + 1;
}


void left_rotate(AVL_TREE* node)
{
    AVL_TREE* buffer = node->left;
    swap_node(node, node->right);

    node->left = node->right;
    node->right = node->left->right;
    node->right->left = node->right->right;
    node->left->right = node->left->left;
    node->left->left = buffer;

    update_height(node->left);
    update_height(node);
}


void right_rotate(AVL_TREE* node)
{
    AVL_TREE* buffer = node->right;
    swap_node(node, node->left);

    node->right = node->left;
    node->left = node->right->left;
    node->right->left = node->right->right;
    node->right->right = buffer;

    update_height(node->right);
    update_height(node);
}


void balance(AVL_TREE* node)
{
    int balance = get_height(node);
    if (balance == -2)
    {
        if (get_balance(node->left) == 1)
            left_rotate(node->left);
        right_rotate(node);
    }
    else if (balance == 2)
    {
        if (get_balance(node->right) == -1)
            right_rotate(node->right);
        left_rotate(node);
    }
}


AVL_TREE* create_node(int key, int value)
{
    AVL_TREE* node = (AVL_TREE*)malloc(sizeof(AVL_TREE));

    if (node != NULL)
    {
        node->key = key;
        node->value = value;
        node->left = NULL;
        node->right = NULL;
        node->height = 0;
    }
    else
        node->height = -1;
    return node;
}


void delete_tree(AVL_TREE* root)
{
   if (root)
   {
       delete_tree(root->left);
       delete_tree(root->right);
       free(root);
   }
}


void insert(AVL_TREE* node, int key, int value)
{
    if (key < node->key)
    {
        if (node->left == NULL) node->left = create_node(key, value);
        else insert(node->left, key, value);
    }

    else if (key >= node->key)
    {
        if (node->right == NULL) node->right = create_node(key, value);
        else insert(node->right, key, value);
    }
    update_height(node);
    balance(node);
}
#endif
