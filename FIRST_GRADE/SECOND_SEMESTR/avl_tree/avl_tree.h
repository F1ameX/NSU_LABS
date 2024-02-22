#ifndef AVL_TREE_AVL_TREE_H
#define AVL_TREE_AVL_TREE_H
#pragma once

#include <stdio.h>
#include <stdlib.h>


typedef struct AVL_TREE {
    int value;
    struct AVL_TREE* left;
    struct AVL_TREE* right;
} AVL_TREE;


int max(int num_1, int num_2)
{
    if (num_1 > num_2)
        return num_1;
    return num_2;
}


int get_height(AVL_TREE* node)
{
    if (node == NULL)
        return -1;
    return max(get_height(node->left), get_height(node->right)) + 1;
}


int get_balance(AVL_TREE* node)
{
    if (node == NULL)
        return 0;
    return get_height(node->right) - get_height(node->left);
}


void swap_node(AVL_TREE* node_1, AVL_TREE* node_2)
{
    int value_1 = node_1->value;
    node_1->value = node_2->value;
    node_2->value = value_1;
}


void left_rotate(AVL_TREE* node)
{
    AVL_TREE* buffer = node->left;
    swap_node(node, node->right);
    node->left = node->right;
    node->right = node->left->right;
    node->left->right = node->left->left;
    node->left->left = buffer;
}


void right_rotate(AVL_TREE* node)
{
    AVL_TREE* buffer = node->right;
    swap_node(node, node->left);
    node->right = node->left;
    node->left = node->right->left;
    node->right->left = node->right->right;
    node->right->right = buffer;
}


void balance(AVL_TREE* node)
{
    int balance = get_balance(node);
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


AVL_TREE* create_node(int value)
{
    AVL_TREE* node = (AVL_TREE*)malloc(sizeof(AVL_TREE));

    if (node != NULL)
    {
        node->value = value;
        node->left = NULL;
        node->right = NULL;
    }

    return node;
}


void delete_tree(AVL_TREE* root)
{
    if (root != NULL)
    {
        delete_tree(root->left);
        delete_tree(root->right);
        free(root);
    }
}


void in_order(AVL_TREE* node)
{
    if (node == NULL)
        return;
    in_order(node->left);
    printf("%d ", node->value);
    in_order(node->right);
}


void insert(AVL_TREE* node, int value)
{
    if (value < node->value)
    {
        if (node->left == NULL)
            node->left = create_node(value);
        else
            insert(node->left, value);
    }
    else if (value >= node->value)
    {
        if (node->right == NULL)
            node->right = create_node(value);
        else
            insert(node->right, value);
    }

    balance(node);
}


int search(AVL_TREE* node, int key)
{
    if (node == NULL)
        return -1;

    else if (node->value == key)
        return node->value;

    else if (node->value < key)
        search(node->right, key);
    else
        search(node->left, key);
}


#endif
