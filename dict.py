import nltk
nltk.download('words')

english_words = set(nltk.corpus.words.words())

for w in english_words:
    if len(w) == 5 and w[0].islower():
        print(w)