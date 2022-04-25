#!/usr/bin/python3
from tqdm import tqdm
import random
from itertools import product
from math import log2
from copy import deepcopy
import matplotlib.pyplot as plt
 
BLACK = "\U00002B1B"
YELLOW = "\U0001F7E8"
GREEN = "\U0001F7E9"

class Clues():
    wrong = {}
    correct = {}
    almost = {}
    last_guess = ""
    last_pattern = ""

    black_letters = []
    gy_letters = []

    def __str__(self):
        return f"{self.wrong = }\n{self.correct = }\n{self.almost = }"

def getPattern(target: str, guess: str):
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
                elif target.count(l) > seen[l]:
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

def entropy(viable: list, guess: str):
    assert(guess in viable)
    temp = list(product(["b", "y", "g"], repeat=5))
    patterns = {}
    for x in temp:
        s = "".join(x)
        patterns[s] = 0
    # find patter for every word
    for w in viable:
        patterns[getPattern(w, guess)] += 1

    probs = []
    for p in patterns:
        probs.append(patterns[p]/len(viable))
    sum = 0
    for p in probs:
        if p:
            sum += p * log2(1/p)
    return sum

def letter_counter(letters: list, c: str):
    '''Count occurences of char c in letters'''
    ret = 0
    for l in letters:
        if l == c:
            ret += 1
    return ret

def valid(clues: Clues, word, debug=False):
    # Green pass
    if "g" in clues.last_pattern:
        for c in clues.correct:
            for i in clues.correct[c]:
                if word[i] != c:
                    return False
    # Black pass
    if "b" in clues.last_pattern:
        # black_letters = [clues.last_guess[i] for i,c in enumerate(clues.last_pattern) if c == "b"]
        # gy_letters = [clues.last_guess[i] for i,c in enumerate(clues.last_pattern) if c != "b"]
        for l in clues.black_letters:
            if l in word:
                if l not in clues.gy_letters:
                    return False
                if letter_counter(clues.gy_letters, l) < word.count(l):
                    return False
    # Yellow pass
    if "y" in clues.last_pattern:
        for c in clues.almost:
            if c not in word:
                return False
            for i in clues.almost[c]:
                if word[i] == c:
                    return False
    return True
    
def read_pattern(clues: Clues, pattern: str, guess: str):
    """Reads a pattern returned from `getPattern()` and then 
    updates Clues class to reflect new information learned.
    """
    # Green pass:
    for i, mark in enumerate(pattern):
        letter = guess[i]
        if mark == 'g':
            if letter not in clues.correct:
                clues.correct[letter] = [i]
            elif i not in clues.correct[letter]:
                clues.correct[letter].append(i)
    # Yellow pass:
    for i, mark in enumerate(pattern):
        letter = guess[i]
        if mark == 'y':
            if letter not in clues.almost:
                clues.almost[letter] = [i]
            elif i not in clues.almost[letter]:
                clues.almost[letter].append(i)
    # Black pass:
    for i, mark in enumerate(pattern):
        letter = guess[i]
        if mark == 'b':
            if letter not in clues.wrong:
                clues.wrong[letter] = [i]
            elif i not in clues.wrong[letter]:
                clues.wrong[letter].append(i)

def bestGuess(viable: list):
    assert(len(viable) != 0)
    if len(viable) == 1:
        return viable[0]
    guess = ""
    bits = 0
    for w in viable:
        temp = entropy(viable, w)
        if temp > bits:
            bits = temp
            guess = w
    return guess

def refine_list(clues: Clues, viable: list):
    ret = []
    for w in viable:
        clues.black_letters = [clues.last_guess[i] for i,c in enumerate(clues.last_pattern) if c == "b"]
        clues.gy_letters = [clues.last_guess[i] for i,c in enumerate(clues.last_pattern) if c != "b"]
        if valid(clues, w):
            ret.append(w)
    return ret

def loadWords(path):
    words = []
    with open(path, "r") as f:
        words = f.read().splitlines()
    return words

def solve(starter: str, target: str, words: list, display=False, debug=False):
    """
    starter: the first guess
    target: the secret word (ie the solution)
    words: list of words that are possibly the solution
    display=False: prints each guess if True
    """
    clues = Clues()
    clues.almost = {}
    clues.correct = {}
    clues.wrong = {}
    num_guess = 1
    clues.last_guess = starter

    while clues.last_guess != target:
        if display:
            print(f"Guess #{num_guess}: {clues.last_guess} {emojize(getPattern(target, clues.last_guess))}")
        num_guess += 1
        pattern = getPattern(target, clues.last_guess)
        clues.last_pattern = pattern
        if debug:
            # print(words)
            print(clues)
        read_pattern(clues, pattern, clues.last_guess)
        words = refine_list(clues, words)
        clues.last_guess = bestGuess(words)
        if num_guess > 10:
            print(f"\tAlert: high guess count for '{target}'")
            exit()
    if display:
        print(f"Guess #{num_guess}: {clues.last_guess} {emojize(getPattern(target, clues.last_guess))}")
    return num_guess

def avg(score_dict):
    word_count = 0
    guess_count = 0
    for n in score_dict:
        word_count += score_dict[n]
        guess_count += n * score_dict[n]
    return guess_count / word_count

def guessAvg(starter):
    score = {}
    for i in range(1,15):
        score[i] = 0
    words = loadWords("al.txt")
    with tqdm(total=len(words), desc="Progress...", unit="words") as pbar:
        for i,w in enumerate(words):
            words_copy = deepcopy(words)
            # print(f"TARGET:  {w}")
            n = solve(starter, w, words_copy, display=False)
            score[n] += 1
            pbar.update(1)
            # print(i)
    print(score)
    print(avg(score))
    return score

def test():
    with open("al.txt", "r") as f:
        words = f.read().splitlines()
        n = solve("frame", words, display=True, debug=False)
        print(n)
        # solve("world", words)

# test()
# guessAvg("crane")

def interactive():
    """Takes input and then guesses the solution"""
    words = loadWords("./al.txt")
    while True:
        target = input("Enter the target word (or 'exit' to exit): ")
        if target == "exit":
            exit()
        if target not in words:
            print("That is not a viable solution")
            continue
        solve("raise", target, words, display=True)
# interactive()

def plotScore(score: dict, title: str):
    fig = plt.figure()
    counts = [i for i in score if score[i]]
    guesses = [score[x] for x in score if score[x]]
    bars = plt.bar(counts, guesses, width=0.9)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x(), yval + 1, yval)
    plt.title(title)
    plt.show()

# plotScore({1: 1, 2: 131, 3: 970, 4: 936, 5: 217, 6: 48, 7: 10, 8: 2, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0},
# "Maximum Entropy Results")
guessAvg("serai")