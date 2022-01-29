#!/usr/bin/python3
import cmd, sys

char_freq = {"e":12.6,"t":9.37,"a":8.34,"o":7.7,"n":6.8,"i":6.7,"h":6.11,"s":6.11,"r":5.68,"l":4.24,"d":4.14,"u":2.85,"c":2.73,"m":2.53,"w":2.34,"y":2.04,"f":2.03,"g":1.92,"p":1.66,"b":1.54,"v":1.06,"k":0.87,"j":0.23,"x":0.20,"q":0.09,"z":0.06}

class App(cmd.Cmd):
    intro = "\n~~ The Wordle Wizard ~~\n\nEnter 'help' to see commands\n"
    prompt = "(menu) "

    dict_file = "la.txt"
    freq_sums = {}
    sorted_words = []
    guess = ""

    num_guesses = 1

    correct = {}        # letters that are in the correct spot
    almost = {}         # letters that are not in the correct spot
    wrong = []          # letters that are not in the wordle

    mode = "menu"

    def do_menu(self):
        with open("menu.txt", "r") as f:
            print(f.read())
    
    def help_menu(self):
        self.onecmd("menu")
    
    def do_exit(self, arg):
        exit()
    
    def do_wiz_art(self, arg):
        with open("wizard.txt", "r") as f:
            print(f.read())

    # def do_batch(self, dict_file):
    #     with open(dict_file, "r"):



    def do_interactive(self, arg):
        self.mode = "interactive"
        self.prompt = "(interactive) "
        print(f"WIZARD: My guess is {self.guess.upper()}")
        while self.mode == "interactive":
            x = input("\t  feedback: ")
            self.onecmd("feedback " + x)

    def do_auto(self, arg):
        self.mode = "auto"
        target = input("Enter the word for the Wizard to guess: ")
        print(f"WIZARD: My guess is {self.guess.upper()}")

        def getFeedback(word: str) -> str:
            ret = ""
            for i,c in enumerate(self.guess):
                if c in word:
                    if word[i] == c:
                        ret += "+"
                    else:
                        ret += "*"
                else:
                    ret += "-"
            print(ret)
            return ret

        while self.mode == "auto":
            self.onecmd("feedback " + getFeedback(target))
        return self.num_guesses


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

    def do_f(self, arg):
        self.onecmd("feedback " + arg)

    def do_feedback(self, arg: str):
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
            self.onecmd("help feedback")

        else:
            for i, mark in enumerate(arg):
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

        # Now update the list of viable words based off of most recent feedback
        def viable(word) -> bool:
            # TODO: figure out what to do for repeat letters in words
            for i,c in enumerate(word):
                if c in self.wrong:
                    return False
                if c in self.almost.keys():
                    if i in self.almost[c]:
                        return False
                if c in self.correct.keys():
                    if i not in self.correct[c]:
                        return False
                # check if all clues are being used
                for letter in self.correct.keys():
                    if letter not in word:
                        return False
                for letter in self.almost.keys():
                    if letter not in word:
                        return False
            return True

        viable_words = []
        for word in self.sorted_words:
            if viable(word):
                viable_words.append(word)
        
        # Sort words by freq and put them back into self.freq_sums
        # bad_words = set(self.sorted_words) - set(viable_words)
        # for w in bad_words:
        #     self.freq_sums.pop(w)
                            
        # Make new educated guess
        if len(viable_words):
            self.guess = viable_words[0]
            print(f"WIZARD: My guess is {self.guess.upper()}")
            self.num_guesses += 1
            if len(viable_words) == 1:
                print("If that's not your word, double check your feedback.")
                self.mode = "menu"
                self.prompt = "(menu) "
                self.setup()
        else:
            print("Idk. You're word may not exist. You sure you gave me the correct clues?")
            exit()
            self.mode = "menu"
            self.prompt = "(menu) "
            self.setup()
    
    def help_feedback(self):
        print("Feedback should be a 5 character string. Letters should be marked accordingly:\n")
        print("'-' -> letter is not in the target word")
        print("'*' -> letter is in the target word but in the incorrect position")
        print("'+' -> letter is in the target word and in the correct position")
        print("\nAlternatively, 'b', 'y', and 'g' (representing the black, yellow, and green words from the original Wordle game) can be used instead of '-', '*', '+' respectively")
        print()

    def emptyline(self) -> bool:
        return super().emptyline()
    
    # def postcmd(self, stop: bool, line: str) -> bool:
    #     return super().postcmd(stop, line)

if __name__ == "__main__":
    app = App()
    app.onecmd("wiz_art")
    app.setup()
    app.cmdloop()