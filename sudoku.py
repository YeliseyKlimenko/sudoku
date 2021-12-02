#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import json
import matplotlib.pyplot as plt
import doctest


# ### Import initial tables

# In[4]:


file_name1='sudoku_01.json'
file_name2='sudoku_02.json'

with open(file_name1, 'r') as jsonfile:
    sudoku1 = json.load(jsonfile)
    
with open(file_name2, 'r') as jsonfile:
    sudoku2 = json.load(jsonfile)


# ### Plot initial tables

# In[5]:


def sudoku_plot(M):
    fig, ax = plt.subplots()
    im = ax.imshow(M, cmap='Blues', vmin=0, vmax=0, interpolation='none')
    plt.axis('off')
    for i in range(len(M)):
        for j in range(len(M[0])):
            if (M[i][j]==0):
                text = ax.text(i, j, M[i][j], ha="center", va="center", color="black")
            else:
                text = ax.text(i, j, M[i][j], ha="center", va="center", color="red")


# ### Dependencies

# In[8]:


class Square:  #class that represents each square in a soduku table
    def __init__(self,K):
        if K==0:
            self.K = [1,2,3,4,5,6,7,8,9] #labels
        else:
            self.K = [K]
        self.N = [] #neighbors
        self.L = [] #links
    
    def is_paired(self,k1,S2):  #function that tests whether 2 squares have a pair of linked labels
        for link in self.L:
            if link.S[1] == S2 and link.K[0] == k1:
                return True
        return False
        

class Link:  #class that represents each link(arc) between neighboring squares and their states
    def __init__(self,S1,S2,K1,K2):
        self.S = [S1, S2] #neighbor pair
        self.K = [K1, K2] #label pair


# In[9]:


def Mto_class(M): #function that takes the sudoku table (9x9 list) as an input and converts it into a 9x9 matrix of 'square' type objects
    A = []  
    l = range(len(M))
    for i in l:
        Al = []
        for j in l:
            Al.append(Square(M[i][j]))
        A.append(Al)
    for i in l:
        for j in l:
            N = []
            for k in l:
                if k!=j:
                    N.append(A[i][k])
            for k in l:
                if (k!=i):
                    N.append(A[k][j])
            if [0,3,6].count(i)!=0:
                if [0,3,6].count(j)!=0:
                    N.extend(A[i+1][j+1:j+3])
                    N.extend(A[i+2][j+1:j+3])
                elif [1,4,7].count(j)!=0:
                    N.append(A[i+1][j-1])
                    N.append(A[i+1][j+1])
                    N.append(A[i+2][j-1])
                    N.append(A[i+2][j+1])
                else:
                    N.extend(A[i+1][j-2:j])
                    N.extend(A[i+2][j-2:j])
            elif [1,4,7].count(i)!=0:
                if [0,3,6].count(j)!=0:
                    N.extend(A[i-1][j+1:j+3])
                    N.extend(A[i+1][j+1:j+3])
                elif [1,4,7].count(j)!=0:
                    N.append(A[i-1][j-1])
                    N.append(A[i-1][j+1])
                    N.append(A[i+1][j-1])
                    N.append(A[i+1][j+1])
                else:
                    N.extend(A[i-1][j-2:j])
                    N.extend(A[i+1][j-2:j])
            else:
                if [0,3,6].count(j)!=0:
                    N.extend(A[i-1][j+1:j+3])
                    N.extend(A[i-2][j+1:j+3])
                elif [1,4,7].count(j)!=0:
                    N.append(A[i-1][j-1]) 
                    N.append(A[i-1][j+1]) 
                    N.append(A[i-2][j-1])
                    N.append(A[i-2][j+1])
                else:
                    N.extend(A[i-1][j-2:j])
                    N.extend(A[i-2][j-2:j])
            A[i][j].N.extend(N)
    return A


# In[10]:


def Lto_class(A):  #function that attaches the appropriate links to each 'square' type object in the matrix
    for i in range(len(A)):
        for square in A[i]:
            L = []
            for k in square.K:
                for neighbor in square.N:
                    for kk in neighbor.K:
                        if (kk!=k):
                            L.append(Link(square,neighbor,k,kk))
            square.L.extend(L)


# In[11]:


def ACalg(A):  #arc_consistency enforcement algorithm
    l = range(len(A))
    flag = 0
    '''label check'''
    for i in l:
        Alt = []
        for square in A[i]:
            for k in square.K:
                if np.all([square.is_paired(k,N) for N in square.N])!=True:
                    square.K.remove(k)
                    flag = 1
    '''link check'''
    for i in l:
        for square in A[i]:
            for link in square.L:
                if link.S[0].K.count(link.K[0])==0 or link.S[1].K.count(link.K[1])==0:
                    square.L.remove(link)
                    flag = 1

    if flag==1:
        return ACalg(A)
    else:
        return A


# In[29]:


def class_to_M(A):  #function that converts a matrix of 'square' type objects into a 9x9 list
    M = []
    for i in range(len(A)):
        Mt = []
        for j in range(len(A)):
            if len(A[i][j].K)==1:
                Mt.append(A[i][j].K[0])
            else:
                Mt.append(0)
        M.append(Mt)
    return M
        
def finish(A):  #brute force algorithm
    B = A.copy()
    M = class_to_M(B)
    for i in range(len(M)):
        for j in range(len(M)):
            if M[i][j]==0:
                for k in A[i][j].K:
                    B[i][j].K = [k]
                    B = ACalg(B)
                    if np.any([square.K==[] for square in np.array(B).ravel()])!=True:
                        return finish(B)
    return A


# ### Arc-consistency algorithm

# In[35]:


def solve(M):  #function that takes a sudoku table (9x9 list) as an input and returns a solved table (9x9 list) or reports on the puzzle's insolubility
    
    """
    >>> solve([[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1]])
    the csp cannot be solved
    >>> solve([[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]])
    there may be a solution, but the a-c algorithm was unable to find it (no polymorphism)
    >>> solve([[2,4,8,3,6,5,7,9,1],[9,3,7,8,1,4,6,2,5],[5,1,6,7,2,9,3,8,4],[7,8,1,4,3,2,5,6,9],[4,6,9,5,8,1,2,7,3],[3,5,2,9,7,6,4,1,8],[8,9,5,2,4,7,1,3,6],[6,0,4,1,9,3,8,5,0],[1,0,3,6,5,8,9,4,0]])
    [[2, 4, 8, 3, 6, 5, 7, 9, 1], [9, 3, 7, 8, 1, 4, 6, 2, 5], [5, 1, 6, 7, 2, 9, 3, 8, 4], [7, 8, 1, 4, 3, 2, 5, 6, 9], [4, 6, 9, 5, 8, 1, 2, 7, 3], [3, 5, 2, 9, 7, 6, 4, 1, 8], [8, 9, 5, 2, 4, 7, 1, 3, 6], [6, 2, 4, 1, 9, 3, 8, 5, 7], [1, 7, 3, 6, 5, 8, 9, 4, 2]]
    """
    A = Mto_class(M)
    Lto_class(A)
    R = ACalg(A)
    if np.any([square.K==[] for square in np.array(R).ravel()]):
        print('the csp cannot be solved')
        return None
    R = finish(R)
    M = class_to_M(R)
    if np.all([x!=0 for x in np.array(M).ravel()]):
        return M
    else:
        print('there may be a solution, but the a-c algorithm was unable to find it (no polymorphism)')
        return None

