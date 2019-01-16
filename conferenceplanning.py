from __future__ import annotations

# conference planning problem
# solves the problem of allocating presentations to timeslots and rooms (of different capacity) taking account to
# 1) popularity (most popular are allocated first)
# 2) vote preferences (presentations voted for by the same people should preferably be allocated to different time slots)
#
#
# GIVEN:
# T[] time slots with slot descriptions
# rooms with sizes R[i], sorted by capacity in decreasing order
# presentations: L[T * len(R)] with presentation description
# votes with matrix of preferences: where V[i] is a vote of i person where vote is a List[len(L)]
# with free distribution of votes equal to number of lectures (can be 1 vote to every lecture, or all votes to one etc)
#
# for example T[0] == "9am", ...
# R[0] == 200, R[1] == 100, R[2] == 50 room capacity
# L[0] == ["Lecture1"], ...
# votes: V[1]==[0,2,0,0,0,5,2,0,0], ...
#
# TASK:
# Find optimal distribution of presentations as described above
#
# IMPLEMENTATION DETAILS:
# Use partly greedy approach because the problem seems to be NP-hard ("travelling politician problem")
# Bruteforce complexity is O(len(T)! * len(R))
#
# OUTPUT:
# List[room][timeslot] with index in L
#
###### Inspired by negative experiences of visiting some conferences

from typing import *
import sys

BRUTEFORCE_LIMIT = 10

DEBUG = True


def _commonvoices(V: List[List[int]], M: List[int], p, r) -> int:
    voices = 0
    for v in V:
        voices += v[M[p]] + v[M[r]]  # todo: sum cumulatively
    return voices


def _bruteforce(D: List[List[int]], M: List[int], p: int) -> List[int]:
    return _bruteforce2(D, M, p, set(), -1)[0]


def _bruteforce2(D: List[List[int]], M: List[int], p: int, visited: Set[int], row: int) -> (List[int], int):
    if row == len(D) - 2:
        for i in range(len(D)):
            if i not in visited:
                return [M[p + i]], D[row][i]

    min = sys.maxsize
    path = []

    for i in range(len(D)):
        if i in visited:
            continue
        subvisited = set(visited)
        subvisited.add(i)
        subpath, m = _bruteforce2(D, M, p, subvisited, row + 1)
        m += D[row][i]
        if m <= min:
            min = m
            subpath = [M[p + i]] + subpath
            path = subpath

    return path, min


def _greedy(D: List[List[int]], M: List[int], p: int) -> List[int]:
    r = []
    visited = set()
    for prev in D:
        min = sys.maxsize
        index = -1
        for i in range(len(D)):
            if i in visited:
                continue
            if prev[i] <= min:
                index = i
                min = prev[i]
        visited.add(index)
        r.append(M[p + index])
    return r


def plan(T: List[str], R: List[int], L: List[str], V: List[List[int]], **kwargs):
    if len(L) != len(T) * len(R):
        raise Exception("number of presentations should equal T * R")

    # find P popularity (rating) of each presentation
    P = [0] * len(L)
    for v in V:
        sum = 0
        for i in range(len(L)):
            P[i] += v[i]
            sum += v[i]
        if sum > len(L):
            raise Exception("incorrect vote")

    print("presentations' total popularity", P)
    M = [i for i in range(len(P))]
    M = sorted(M, key=lambda x: P[x], reverse=True)

    E = []

    if "greedy" in kwargs:
        greedy = kwargs["greedy"]
    else:
        greedy = len(T) > BRUTEFORCE_LIMIT

    if greedy:
        print("using GREEDY algorithm")
    else:
        print("using BRUTEFORCE algorithm")

    # for the largest room simply assign most popular presentations
    E.append(M[:len(T)])

    # do for each following room
    p = len(T)
    while p < len(T) * len(R):
        # calculate voices for each pair of presentations for this room with each of the previous rooms
        D = []
        for i in range(len(T)):
            D.append([_commonvoices(V, M, p - len(T) + k, p + i) for k in range(len(T))])
        if greedy:
            E.append(_greedy(D, M, p))
        else:
            E.append(_bruteforce(D, M, p))
        p += len(T)

    if DEBUG:
        for t in range(len(T)):
            print(T[t])
            for room in range(len(R)):
                print(R[room], L[E[room][t]])
    return E


T = ["morning", "noon", "evening"]
R = [30, 20, 10]
L = ["java1", "java2", "golang1", "golang2", "golang3", "python1", "python2", "haskell", "sponsor presentation"]

V = []
V.extend([5, 4, 0, 0, 0, 0, 0, 0, 0] for _ in range(16))  # javists
V.extend([0, 0, 5, 3, 1, 0, 0, 0, 0] for _ in range(15))  # golangers
V.extend([0, 0, 0, 0, 0, 6, 3, 0, 0] for _ in range(20))  # pythonista
V.extend([0, 0, 0, 0, 0, 2, 0, 7, 0] for _ in range(5))  # haskelists
V.extend([1, 1, 1, 1, 1, 1, 1, 1, 1] for _ in range(2))  # sponsor representatives

plan(T, R, L, V, greedy=True)
print()
plan(T, R, L, V)

# run:
#
# presentations' total popularity [82, 66, 77, 47, 17, 132, 62, 37, 2]
# using GREEDY algorithm
# morning
# 30 python1
# 20 golang2
# 10 sponsor presentation
# noon
# 30 java1
# 20 python2
# 10 golang3
# evening
# 30 golang1
# 20 java2
# 10 haskell
#
# presentations' total popularity [82, 66, 77, 47, 17, 132, 62, 37, 2]
# using BRUTEFORCE algorithm
# morning
# 30 python1
# 20 golang2
# 10 sponsor presentation
# noon
# 30 java1
# 20 python2
# 10 golang3
# evening
# 30 golang1
# 20 java2
# 10 haskell
