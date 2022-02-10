from entropy import distribution
import re
import math


class EntropyCalculator:
    """General class for calculating entropies in text
    """

    def __init__(self, corpus_path, only_letters=True, word_separator=" ", log_base=2):
        """[summary]

        Args:
            corpus_path (String): Path to the text
            word_separator (str, optional): What separates the words. Defaults to " ".
            log_base (int, optional): Which logarithm to be used. Defaults to 2.
        """
        self.only_letters = only_letters
        self.corpus = self.read_corpus(corpus_path)
        # getting dictonary to have mapping of words. May be usefull if words are very long and we want to save some memory
        self.word_mapping = self.get_words_mapping(
            word_separator=word_separator)
        self.words_distributions = {}
        self.chars_distributions = {}
        self.log_base = log_base

    def add_distribution(self, order=0, words=False):
        """We just check whether we've calculated this distribution already if not we calculate it and add to the dictonary

        Args:
            order (int, optional): Which conditional order to be calculate_distribution. Defaults to 0.
            words (bool, optional): Whether we want words or characters distribution. Defaults to False.
        """
        if (order not in self.words_distributions) and words:
            self.words_distributions[order] = distribution.calculate_distribution(
                inf_source=self.corpus, order=order, words=words, mapping=self.mapping)
        elif (order not in self.chars_distributions):
            self.chars_distributions[order] = distribution.calculate_distribution(
                inf_source=self.corpus, order=order, words=words)

    def remove_distribution(self, order=0):
        """If we are sure that we won't need some distribution we can remove the distribution easily

        Args:
            order (int, optional): [description]. Defaults to 0.
        """
        if order in self.words_distributions:
            del self.words_distributions[order]
            print(f"Removed: {order} from words dictonary")
        if order in self.chars_distributions:
            del self.chars_distributions[order]
            print(f"Removed: {order} from characters dictonary")

    def read_corpus(self, corpus_path):
        """Function reading and preprocessing the corpus

        Args:
            corpus_path ([type]): [description]

        Returns:
            String: processed corpus
        """
        with open(corpus_path, "r") as f:
            corpus = f.read()
            # get rid of all newline characters
            corpus = corpus.replace("\n", "")

            if self.only_letters:
                # version of the text that do not contain any numbers and special characters
                corpus = re.sub(r'[^a-zA-Z ]', "", string=corpus)
                # we may get some double spaces in case of "in 1942 there" etc.
                corpus = re.sub("\s\s+", " ", string=corpus)

        return corpus.strip()

    def append_to_corpus(self, appendix_path):
        """If we want to merge few corpuse we should use this"""
        appendix = self.read_corpus(corpus_path=appendix_path)
        self.corpus = ''.join([self.corpus, appendix])

    # It seems reasonable to somehow encode the strings to int not to use so much memory
    # For characters we can just use their ASCII encoding. Another benefit is that we could then use it to generate some text
    def get_words_mapping(self, word_separator=" "):
        """This just maps each word to the number. With characters we can just use ord(). However with words enumeration seems to be the best choice

        Args:
            word_separator (str, optional): [description]. Defaults to " ".

        Returns:
            [type]: [description]
        """
        mapping = {}
        for index, word in enumerate(set(self.corpus.split(word_separator))):
            mapping[word] = index

        return mapping

    def mapping(self, word="hello world"):
        """Functions that maps given word to the number

        Args:
            word (str, optional): [description]. Defaults to "hello world".

        Returns:
            [type]: [description]
        """
        return self.word_mapping[word]

    def calculate_conditional_entropy(self, order=1, words=False):
        """Function calculating entropy by iterating over distributions dictonaries and just using the equations for 
           Conditional Entropies 
        Args:
            order (int, optional): which order do we calculate. Defaults to 1.
            words (bool, optional): To calculate words or chars entropy. Defaults to False.

        Returns:
            Float: Entropy value
        """
        self.add_distribution(
            order, words)  # If distribution is already added it won't do nothing
        if words:
            distributions = self.words_distributions[order]
        else:
            distributions = self.chars_distributions[order]

        entropy = 0
        if order == 1:
            for probability in distributions.values():
                entropy -= probability*math.log(probability, self.log_base)
        else:
            for distribution in distributions.values():

                # This is so wrong I should put this value in separate placeholder!
                p_of_x = distribution['p_of_x']
                entropy_of_y_given_x = 0
                for k, p_of_y_given_x in distribution.items():
                    if k == "p_of_x":
                        continue
                    entropy_of_y_given_x -= p_of_y_given_x * \
                        math.log(p_of_y_given_x, self.log_base)

                entropy += p_of_x * entropy_of_y_given_x

        return entropy

    def get_num_of_chars(self):
        return len(set(list(self.corpus)))

    def get_num_of_words(self):
        return len(set(self.corpus.split(" ")))
