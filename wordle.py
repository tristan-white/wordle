#!/usr/bin/python3
import cmd, sys
from tqdm import tqdm

char_freq = {"e":12.6,"t":9.37,"a":8.34,"o":7.7,"n":6.8,"i":6.7,"h":6.11,"s":6.11,"r":5.68,"l":4.24,"d":4.14,"u":2.85,"c":2.73,"m":2.53,"w":2.34,"y":2.04,"f":2.03,"g":1.92,"p":1.66,"b":1.54,"v":1.06,"k":0.87,"j":0.23,"x":0.20,"q":0.09,"z":0.06}

class App(cmd.Cmd):
    intro = "\n~~ The Wordle Wizard ~~\n\nEnter 'help' to see commands\n"
    prompt = ">>> "

    mode = ""

    dict_file = "la.txt"
    freq_sums = {}
    sorted_words = []
    guess = ""

    num_guesses = 1

    correct = {}        # letters that are in the correct spot
    almost = {}         # letters that are not in the correct spot
    wrong = []          # letters that are not in the wordle
    
    def help_exit(self):
        print("Exits the program.")

    def do_exit(self, arg):
        exit()
    
    def wiz_art(self):
        with open("wizard.txt", "r") as f:
            print(f.read())

    def help_stats(self):
        with open("./txt/help_stats.txt", "r") as f:
            print(f.read())

    def do_stats(self, arg):
        guess_counts = {}
        for i in range(1,13):
            guess_counts[i] = 0        
        total = 0
        dict_file = "la.txt" if arg == "" else arg
        with open(dict_file, "r") as f:
            words = f.read().splitlines()
            with tqdm(total=len(words), desc="Progress...", unit="words") as pbar:
                for w in words:
                    self.setup()
                    while self.guess != w:
                        self.read_clue(self.getFeedback(w))
                        self.guess = self.get_guess()
                    # Record number of guesses
                    guess_counts[self.num_guesses] += 1
                    total += 1
                    pbar.update(1)
        # Figure out stats
        average = 0
        for key in guess_counts.keys():
            average += key * (guess_counts[key] / total)
            print(f"{key} Guess: {(guess_counts[key] / total) * 100}%")
        print(f"{'=' * 12}\nAverage: {average}")
    
    def help_interactive(self):
        with open("./txt/help_interactive.txt", "r") as f:
            print(f.read())

    def do_interactive(self, arg):
        self.mode = "interactive"
        self.prompt = "(interactive) "
        print(f"WIZARD: My guess is {self.guess.upper()}")
        while self.mode == "interactive":
            x = input("\t  feedback: ")
            self.feedback(x)

    def getFeedback(self, word: str) -> str:
        ret = ""
        for i,c in enumerate(self.guess):
            if c in word:
                if word[i] == c:
                    ret += "+"
                else:
                    ret += "*"
            else:
                ret += "-"
        return ret

    def help_auto(self):
        with open("./txt/help_auto.txt", "r") as f:
            print(f.read())

    def do_auto(self, arg):
        target = input("Enter the word for the Wizard to guess: ")
        print(f"WIZARD: My guess is {self.guess.upper()}")

        while self.guess != target:
            self.feedback(self.getFeedback(target))
        self.setup()

    def setup(self):
        self.guess = "atone"
        self.wrong = []
        self.almost = {}
        self.correct = {}
        self.num_guesses = 1
        if not self.sorted_words:
            with open(self.dict_file, "r") as f:
                words = f.read().splitlines()
                for w in words:
                    temp = "".join(set(w))
                    sum = 0
                    for letter in temp:
                        sum += char_freq[letter]
                    self.freq_sums[w] = sum
            # sort `freq_sums` by value, from high to low
            self.freq_sums = dict(sorted(self.freq_sums.items(), key=lambda x:x[1], reverse=True))
            self.sorted_words = self.freq_sums.keys()

    def viable(self, word) -> bool:
        # TODO: figure out what to do for repeat letters in words
        for i,c in enumerate(word):
            if c in self.wrong:
                return False
            if c in self.almost.keys():
                if i in self.almost[c]:
                    return False
            if c in self.correct.keys():
                if i not in self.correct[c]:    
                    for pos in self.correct[c]:
                        if c != word[pos]:
                            return False

            # check if all clues are being used
            for letter in self.correct.keys():
                if letter not in word:
                    return False
            for letter in self.almost.keys():
                if letter not in word:
                    return False
        return True

    def read_clue(self, clue):
        for i, mark in enumerate(clue):
            letter = self.guess[i]
            if mark == '-' or mark == 'b':
                # Check that the letter isn't marked elsewhere as 'almost' or 'correct'
                if letter not in self.wrong:
                    self.wrong.append(letter)
            if mark == '*' or mark == 'y':
                if letter not in self.almost.keys():
                    self.almost[letter] = [i]
                elif i not in self.almost[letter]:
                    self.almost[letter].append(i)
            if mark == '+' or mark == 'g':
                if letter not in self.correct.keys():
                    self.correct[letter] = [i]
                else:
                    self.correct[letter].append(i)

    # Makes a new guess based off of info from self.wrong, self.correct, and self.almost
    # Typically, read_clue() should be called first
    def get_guess(self) -> str:
        if not len(self.sorted_words):
            return ""
        self.num_guesses += 1
        viable_words = []
        for word in self.sorted_words:
            if self.viable(word):
                viable_words.append(word)
        if len(viable_words):
            self.guess = viable_words[0]
            return self.guess

    def help_feedback(self):
        with open("./txt/help_feedback.txt", "r") as f:
                print(f.read())

    def feedback(self, arg: str):
        # First check format of feedback. Feedback should consist of either +,-,* chars or b,y,g chars
        def verify(input: str):
            if len(input) != 5:
                return False
            valid = "+-*byg"
            for c in input:
                if c not in valid:
                    return False
            return True
        
        if not verify(arg):
            print("Incorrect format.")
            with open("./txt/help_feedback.txt", "r") as f:
                print(f.read())

        else:
            self.read_clue(arg)
                                        
        # Make new educated guess
        guess = self.get_guess()
        if guess:
            print(f"WIZARD: My guess is {guess.upper()}")
            if len(self.sorted_words) == 1:
                print("If that's not your word, double check your feedback.")
                self.mode = "menu"
                self.prompt = ">>> "
                self.setup()
        else:
            print("Idk. You're word may not exist. You sure you gave me the correct clues?")
            self.mode = "menu"
            self.prompt = ">>> "
            self.setup()

    def emptyline(self) -> bool:
        return super().emptyline()
    
    # def postcmd(self, stop: bool, line: str) -> bool:
    #     return super().postcmd(stop, line)

if __name__ == "__main__":
    app = App()
    app.wiz_art()
    app.setup()
    app.cmdloop()