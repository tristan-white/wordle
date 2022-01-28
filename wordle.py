#!/usr/bin/python
import cmd
import sys



char_freq = {"e":12.6,"t":9.37,"a":8.34,"o":7.7,"n":6.8,"i":6.7,"h":6.11,"s":6.11,"r":5.68,"l":4.24,"d":4.14,"u":2.85,"c":2.73,"m":2.53,"w":2.34,"y":2.04,"f":2.03,"g":1.92,"p":1.66,"b":1.54,"v":1.06,"k":0.87,"j":0.23,"x":0.20,"q":0.09,"z":0.06}

class App(cmd.Cmd):
    intro = "~ The Wordle Wizard ~\n"
    prompt = "Which letters were correct? "

    dict_file = "dict.txt"
    freq_sums = {}
    guess = ""

    correct = {}        # letters that are in the correct spot
    almost = {}         # letters that are not in the correct spot
    wrong = []          # letters that are not in the wordle

    def do_setup(self, arg):
        with open("dict.txt", "r") as f:
            words = f.read().splitlines()
            for w in words:
                temp = "".join(set(w))
                sum = 0
                for letter in temp:
                    sum += char_freq[letter]
                self.freq_sums[w] = sum
        # sort `freq_sums` by value, from high to low
        self.freq_sums = dict(sorted(self.freq_sums.items(), key=lambda x:x[1], reverse=True))
        # print(list(self.freq_sums)[:10])

    def default(self, arg):
        for i, c in enumerate(self.lastcmd):
            if c != '*' or c != '-' or c != '+':
                print("\nInvalid input. Note:\n'*' indicates the letter is correct AND in the correct spot.\n'+' indicates the letter is correct and NOT in the correct spot.\n'-' indicates the letter is not in the word.\n")
                print("Exiting...")
                sys.exit()

            if c == '-':
                self.wrong.append(c)
            if c == '*':
                self.almost[c] = i
            if c == '+':
                self.correct[c] = i

    def emptyline(self) -> bool:
        return super().emptyline()

    def do_foo(self, arg):
        print("hello world")

    def do_test(self, arg):
        print(arg)
        print(arg)
    
    def postcmd(self, stop: bool, line: str) -> bool:
        # Update list of viable words
        words = {}
        for key in self.freq_sums.keys():
            for c in self.wrong:
                if c in key:
                    continue
            for c in self.almost.keys():
                if c not in key or key[self.almost[c]] 

        return super().postcmd(stop, line)

if __name__ == "__main__":
    app = App()
    app.onecmd("setup")
    app.cmdloop()