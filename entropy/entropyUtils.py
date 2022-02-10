import os
from entropy import entropyCalculator, plots
import pandas as pd


def entropy_of_one_language(corpus_path, max_order=5, entropy_calculator=None, force_update=False, outcome_folder="entropy_outcomes", print_details=True, only_letters=True):
    """Function that calulates entropy of a text given by the corpus_path, eventually you can just pass the entropy_calculator. By default it saves the results to the csv
        File and when it is possible it read it again given the same corpus path. To force the update set force_update flas to be True

    Args:
        corpus_path (String): Path where we store our corpus
        max_order (int, optional): Up to which order we want to calculate the entropy. Defaults to 5.
        entropy_calculator (EntropyCalculator, optional): If it is given we do not read corpus but assumes that it is already read. Defaults to None.
        force_update (bool, optional): Even if we have csv file found we will repeat our calculations. Defaults to False.
        outcome_folder (str, optional): Where to store outcome csv file. Defaults to "outcomes".
        print_details (bool, optional): Whether to print some details like How many words/characters corpus has. Defaults to True.

    Returns:
        tuple: Tuple containing two arrays, character and words entropy up to max_order respectively
    """
    if entropy_calculator is None:
        entropy_calculator = entropyCalculator.EntropyCalculator(
            corpus_path=corpus_path, only_letters=only_letters)

    if print_details:
        print(
            f"This language consist of: {entropy_calculator.get_num_of_chars()} different characters")
        print(
            f"This language consist of: {entropy_calculator.get_num_of_words()} different words")

    if not os.path.isdir(outcome_folder):
        os.mkdir(outcome_folder)
    outcome_path = os.path.join(
        outcome_folder, f"entropy_{os.path.basename(corpus_path).split('.')[0]}.csv")

    chars_entropy = []
    words_entropy = []
    if os.path.isfile(outcome_path) and not force_update:
        entropy = pd.read_csv(outcome_path)
        return list(entropy['characters']), list(entropy['words'])
    else:
        for i in range(max_order):
            entropy_calculator.add_distribution(order=i+1, words=False)
            entropy_calculator.add_distribution(order=i+1, words=True)

            chars_entropy.append(
                entropy_calculator.calculate_conditional_entropy(order=i+1, words=False))
            words_entropy.append(
                entropy_calculator.calculate_conditional_entropy(order=i+1, words=True))

        with open(outcome_path, "w") as f:
            f.write("order,characters,words\n")
            for order, (char, word) in enumerate(zip(chars_entropy, words_entropy)):
                f.write(f"{order},{char},{word}\n")

    return chars_entropy, words_entropy


def normalize(numbers):
    """Funcion that just divides every array member by the array maximum"""
    max_of_numbers = max(numbers)
    return [x/max_of_numbers for x in numbers]


def analyze_entropy(corpus_path, language_name, max_order=1, marker='o', force_update=False, normalize=False, only_letters=True):
    """Function that just uses function above and then optionally normalize results and make a plot of the results.

    Args:
        corpus_path (String): Path to the file to be analyzed
        language (String): Name of the language that is analyzed (just for making legend on the plot)
        max_order (Int): [description]
        marker (str, optional): Which marker to be used in the plot. Defaults to 'o'.
        force_update (bool, optional): Even if we have csv file we can force the updates to be recalculated. Defaults to False.
        normalize (bool, optional): Whether to divide entropies by their maximum then entrop will be in the interval [1,0]. Defaults to False.
    """
    chars_entropy, words_entropy = entropy_of_one_language(
        corpus_path, max_order, force_update=force_update, only_letters=only_letters)

    print(f"{language_name} characters entropy: {chars_entropy}")
    print(f"{language_name} words entropy: {words_entropy}")

    if normalize:
        chars_entropy = normalize(chars_entropy)
        words_entropy = normalize(words_entropy)

    plots.get_plot([chars_entropy], [words_entropy],
                   languages=[language_name], marker=marker)
