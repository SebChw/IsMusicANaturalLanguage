import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from IPython.display import display

PLOT_COLORS = ['blue', 'green', 'red', 'yellow', 'magenta', 'black']


def get_plot(chars_entropy, words_entropy, unit="bits", languages=["English"], marker='0', save_path = None):
    """Function given two arrays generate two plots in one figure

    Args:
        chars_entropy (List): list of lists of characters entrop. Just to easily be able to plot many lines at the same plot
        words_entropy (List): List of lists of word entropy_of_y_given_x
        unit (str, optional): Unit in which we've calculated the entropy. Defaults to "bits".
        languages (list, optional): Languages for which we calculated the entropies. Defaults to ["English"].
        marker (str, optional): Which marker to be used. Defaults to '0'.
    """
    fig, ax = plt.subplots(1, 2, figsize=(20, 7))
    orders = range(len(chars_entropy[0]))

    ax[0].set_title("Entropy of next character, given n previous characters")
    ax[1].set_title("Entropy of next word, given n previous words")

    types = ["characters", "words"]
    for i in range(len(ax)):
        ax[i].set_xlabel(f"n previous {types[i]}")
        ax[i].set_ylabel(f"Condional Entropy [{unit}]")
        ax[i].xaxis.set_major_locator(MaxNLocator(integer=True))

    for i in range(len(chars_entropy)):
        ax[0].plot(orders, chars_entropy[i], label=languages[i],
                   color=PLOT_COLORS[i], marker=marker)
        ax[1].plot(orders, words_entropy[i],
                   color=PLOT_COLORS[i], marker=marker)

    fig.legend()
    
    if save_path is not None:
        fig.savefig(save_path, dpi=800)
        
        
def get_words_plot(words_entropy, unit="bits", languages=["English"], marker='0', save_path = None):
    """Function given two arrays generate two plots in one figure

    Args:
        chars_entropy (List): list of lists of characters entrop. Just to easily be able to plot many lines at the same plot
        words_entropy (List): List of lists of word entropy_of_y_given_x
        unit (str, optional): Unit in which we've calculated the entropy. Defaults to "bits".
        languages (list, optional): Languages for which we calculated the entropies. Defaults to ["English"].
        marker (str, optional): Which marker to be used. Defaults to '0'.
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 7), facecolor='#EEEEEE')
    ax.set_facecolor("#EEEEEE")
    orders = range(len(words_entropy[0]))

    ax.set_title("Entropy of next word, given n previous words")

    type_ = "words"
    
    ax.set_xlabel(f"n previous {type_}")
    ax.set_ylabel(f"Condional Entropy [{unit}]")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    
    for i in range(len(words_entropy)):
        ax.plot(orders, words_entropy[i],label=languages[i],
                   color=PLOT_COLORS[i], marker=marker)

    fig.legend(loc=7)
    
    if save_path is not None:
        fig.savefig(save_path, dpi=800)
