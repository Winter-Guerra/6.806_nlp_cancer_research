import nltk.data
import sys
import yaml


# This program works using pipes. Thus,
# for line in sys.stdin:
#     sys.stdout.write(line)

text = ''.join(sys.stdin)



sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

# save the sentences in an array

sentences = sent_detector.tokenize(text.strip())

# Format sentences in yaml form
sys.stdout.write(yaml.dump(sentences))


# print('\n-----\n'.join(sent_detector.tokenize(text.strip())))
