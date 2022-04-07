#!/usr/bin/python3
from email.policy import compat32
from tqdm import tqdm
import random
from itertools import product
from math import log

 
BLACK = "\U00002B1B"
YELLOW = "\U0001F7E8"
GREEN = "\U0001F7E9"

class Clues():
    wrong = []
    correct = {}
    almost = {}

def compare(target: str, guess: str):
    """Calculates expected bits (aka entropy)
    `viable`: list of viable words
    `guess`: string
    """
    # counts number of letter in word
    def count(letter, word):
        ret = 0
        for x in word:
            if x == letter:
                ret += 1
        return ret

    green_indexes = []
    yellow_indexes = []

    seen = {}
    # green pass
    for i,l in enumerate(guess):
        if l == target[i]:
            green_indexes.append(i)
            if l not in seen:
                seen[l] = 1
            else:
                seen[l] += 1
    # yellow pass
    for i,l in enumerate(guess):
        if l in target:
            if i not in green_indexes:
                if l not in seen:
                    yellow_indexes.append(i)
                    if l not in seen:
                        seen[l] = 1
                    else:
                        seen[l] += 1
                elif count(l, target) > seen[l]:
                    yellow_indexes.append(i)
                    seen[l] += 1
 
    ret = ""
    for i in range(5):
        if i in green_indexes:
            ret += "g"
        elif i in yellow_indexes:
            ret += "y"
        else:
            ret += "b"
    return ret

def emojize(pattern):
    return pattern.replace("b", BLACK).replace("y", YELLOW).replace("g", GREEN)

def entropy(viable, guess):
    assert(guess in viable)
    temp = list(product(["b", "y", "g"], repeat=5))
    patterns = {}
    for x in temp:
        s = "".join(x)
        patterns[s] = 0
    # find patter for every word
    for w in viable:
        patterns[compare(w, guess)] += 1

    probs = []
    for p in patterns:
        probs.append(patterns[p]/len(viable))
    sum = 0
    for p in probs:
        if p:
            sum += p * log(1/p, 2)
    return sum

def valid(clues, word) -> bool:
    # TODO: figure out what to do for repeat letters in words
    for i,c in enumerate(word):
        if c in clues.wrong:
            return False
        if c in clues.almost.keys():
            if i in clues.almost[c]:
                return False
        if c in clues.correct.keys():
            if i not in clues.correct[c]:    
                for pos in clues.correct[c]:
                    if c != word[pos]:
                        return False

        # check if all clues are being used
        for letter in clues.correct.keys():
            if letter not in word:
                return False
        for letter in clues.almost.keys():
            if letter not in word:
                return False
    return True

def read_pattern(clues: Clues, pattern: str, guess: str):
    for i, mark in enumerate(pattern):
        # print(guess, i)
        letter = guess[i]
        if mark == 'b':
            if letter not in clues.wrong:
                clues.wrong.append(letter)
        if mark == 'y':
            if letter not in clues.almost.keys():
                clues.almost[letter] = [i]
            elif i not in clues.almost[letter]:
                clues.almost[letter].append(i)
        if mark == 'g':
            if letter not in clues.correct.keys():
                clues.correct[letter] = [i]
            else:
                clues.correct[letter].append(i)

def bestGuess(viable):
    guess = ""
    bits = 0
    # with tqdm(total=len(viable), desc="Progress...", unit="words") as pbar:
    for w in viable:
        temp = entropy(viable, w)
        if temp > bits:
            bits = temp
            guess = w
            # pbar.update(1)
    # print(f"{guess = }; {bits = }")
    return guess

def refine_list(clues: Clues, viable):
    ret = []
    for w in viable:
        if valid(clues, w):
            ret.append(w)
    return ret

def solve(target):
    words = []
    with open("al.txt", "r") as f:
        words = f.read().splitlines()

    all_clues = []

    guess = "raise"
    while guess != target:
        print(f"{guess = } {emojize(compare(target, guess))}")
        pattern = compare(target, guess)

        clues = Clues()
        read_pattern(clues, pattern, guess)
        all_clues.append(clues)
        for c in all_clues:
            words = refine_list(c, words)

        guess = bestGuess(words)
    print(f"{guess = } {emojize(compare(target, guess))}")


def test():
    with open("al.txt", "r") as f:
        words = f.read().splitlines()

        solve("boxer")

test()