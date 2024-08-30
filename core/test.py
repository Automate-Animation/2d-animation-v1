import nltk

nltk.download("averaged_perceptron_tagger_eng")

from g2p_en import G2p

g2p = G2p()

text = "I have $250 in my pocket."
output = g2p(text)
print(output)
