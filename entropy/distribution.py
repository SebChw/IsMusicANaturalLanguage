import string


def calculate_distribution(inf_source=string.ascii_lowercase + ' ', mapping=lambda a: ord(a), order=1, words=False, words_separator=" "):
    """Function that given some inf_source (text) and order of approximation produces probability distribution
       of conditional probability dristribution depending on order we choose.

    Args:
        inf_source (string, optional): [text from which we calculate distributio, by default english alphabet]. Defaults to string.ascii_lowercase+' '.
        mapping (function): This may be very usefull to map words, characters to some integers so that we can generate new text.
        order (int, optional): [order of approximation]. Defaults to 0. Where 0 -> no conitional probability, 1-> taking into account one letter etc.
        words (Boolean, optional): [if set to True we calculate probabilities of entire words, otherwise of characters].

    Returns:
        [dictonary]: In case of 0th and 1st order approximation dict with keys as ASCII code letters and probabilities. In case of >2 approximations
        dicotnary in form event:distribution. when event is occured string and distribution is probability of any letter after that string 
    """
    distr = {}  # We will store our distribution here

    if words:
        inf_source = inf_source.split(words_separator)
    else:
        # just to have the same form with words and characters
        inf_source = list(inf_source)
    src_len = len(inf_source)

    if order == 1:
        # We just count ocurencess of all events and at the end divide them by cardinality of omega.
        # String are encoded into integers so that we can convert this array into numpy.
        for event in inf_source:
            event = event
            if event in distr:
                distr[event] += 1
            else:
                distr[event] = 1

        omega_len = len(inf_source)
        #omega_len = sum(list(distr.values()))

        for k, v in distr.items():
            distr[k] = v/omega_len

    else:
        omega_len = len(inf_source) - order + 1
        for i in range(src_len):
            # In that case we iterate until we can't take more from our source. For every event that occured we create its own sample space
            # and count probabilities separately.
            if i + order > src_len:
                break
            event = inf_source[i:i+order]
            # Condition - event that occured, next_letter just one letter that occured after condition
            condition, next_event = "".join(event[:-1]), event[-1]
            #print(condition, next_event)
            # We sum up all ocurencess of letters after some order-length string
            if condition not in distr:
                distr[condition] = {}

            if next_event in distr[condition]:
                distr[condition][next_event] += 1
            else:
                distr[condition][next_event] = 1

        for condition, distribution in distr.items():
            all_ocurences = sum(list(distribution.values()))

            for letter, occurences in distribution.items():
                distr[condition][letter] = occurences/all_ocurences
            # We store additional information about overall probability of the even x -> usefull in etropy calculations
            distr[condition][f'p_of_x'] = all_ocurences/omega_len

    return distr
