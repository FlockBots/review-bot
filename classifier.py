from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import os

def append_dir(dir, fname):
    return dir + '/' +fname

vectorizer = TfidfVectorizer(
    input         = 'filename',
    stop_words    = 'english',
    strip_accents = 'ascii'
)

training_set = [append_dir('train', f) for f in os.listdir('train')]
# test_set = [append_dir('test', f) for f in os.listdir('test')]

X_train = vectorizer.fit_transform(training_set)
y_train = 225 * [-1] + 225 * [1]

# X_test = vectorizer.transform(test_set)

clf = LinearSVC()
clf.fit(X_train, y_train)

# predictions = clf.predict(X_test)

# for doc, cls in zip(test_set, predictions):
#     print('[{}] {}'.format(cls, doc))