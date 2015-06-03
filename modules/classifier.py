from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from itertools import chain
import sqlite3
import os
import random
from collections import namedtuple
from pprint import pprint

# data table structure:
''' CREATE TABLE `data` (
        `id`    VARCHAR,
        `comment_text`  VARCHAR NOT NULL,
        `comment_author`    VARCHAR NOT NULL,
        `submission_author` VARCHAR NOT NULL,
        `permalink` VARCHAR NOT NULL,
        `url`   VARCHAR,
        `title` VARCHAR NOT NULL,
        `class` INTEGER,
        `user`  VARCHAR,
        PRIMARY KEY(id)
    );
'''

class DataSet:

    def __init__(self, positive, negative):
        self.positive = positive
        self.negative = negative

        self.classes = len(self.positive) * [1] + len(self.negative) * [-1]

    def __iter__(self):
        return chain(self.positive, self.negative).__iter__()


class Classifier:

    def __init__(self, database_file='data/classified_reviews.db'):
        training_set, test_set = create_sets(database_file)

        self.vectorizer = TfidfVectorizer(
            input         = 'content',
            stop_words    = 'english',
            strip_accents = 'ascii'
        )
        self.classifier = self.train(training_set)

    def create_sets(self, database_file):
        """ Create data sets from the database (assumes table format as defined above).

            Args:
                database_file: (string) path to the database
            Returns:
                A tuple containing the training and test sets.
                The training set is twice as big as the test set.
        """
        connection = sqlite3.connect(database_file)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        # Get all reviews and all regular comments separately.
        cursor.execute('SELECT comment_text FROM data WHERE class = 1')
        positive = [item[0] for item in cursor.fetchall()]
        cursor.execute('SELECT comment_text FROM data WHERE class = 0')
        negative = [item[0] for item in cursor.fetchall()]

        # calculate sizes
        data_size = len(positive), len(negative)
        train_size = (data_size[0] // 3) * 2, (data_size[1] // 3) * 2

        # shuffle the data
        random.shuffle(positive)
        random.shuffle(negative)

        # create sets
        training_set = DataSet(positive[:train_size[0]], negative[:train_size[1]])
        test_set = DataSet(positive[train_size[0]:], negative[train_size[1]:])
        return training_set, test_set

    def train(self, training_set):
        """ Train the classifier on a training set 

            Args:
                training_set: (DataSet) data to train on
            Returns:
                A trained Linear SVM classifier.
        """
        train_data = self.vectorizer.fit_transform(training_set)
        train_expected = training_set.classes

        classifier = LinearSVC()
        classifier.fit(train_data, train_expected)
        return classifier

    def test(self, test_set):
        """ See how well the classifier performs on the given test_set.

            Args:
                test_set: (DataSet) containing positive and negative samples.
            Returns:
                The number of 'True Negatives' (tn), 'False Negatives' (fn), 'True Positives' (tp),
                 'False Positives' (fp), 'accuracy', 'precision' and 'recall' of the classifier in a dictionary.
        """
        test_data = self.vectorizer.transform(test_set)
        predictions = self.classifier.predict(test_data)
        results = {'fn': 0, 'fp': 0, 'tn': 0, 'tp': 0}
        for predicted_class, expected_class in zip(predictions, test_set.classes):
            if predicted_class == 1 and expected_class == -1:
                results['fp'] += 1
            elif predicted_class == -1 and expected_class == 1:
                results['fn'] += 1
            elif predicted_class == -1:
                results['tn'] += 1
            else:
                results['tp'] += 1
        results['precision'] = results['tp'] / (results['tp'] + results['fp'])
        results['recall'] = results['tp'] / (results['tp'] + results['fn'])
        results['accuracy'] = (results['tp'] + results['tn']) / (results['tp'] + results['tn'] + results['fp'] + results['fn'])
        return results

    def classify(text):
        """ Classifies a body of text a whisky review or not.

            Args:
                text: (string) the text to classify
            Returns:
                True, if text is a whisky review
                False, otherwise

        """
        data = self.vectorizer.transform([text])
        prediction = self.classifier.predict(data)[0]
        return prediction == 1
