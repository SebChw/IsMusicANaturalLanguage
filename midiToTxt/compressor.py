def lossy_compresion(text: str, token_separator=" ") -> str:
    """Here we just remove every consecutive duplicate tokens, so we only track changes
        e.g text ABC ABC ABC EE A S X X SD will be compressed to:
                ABC EE A S X SD.

    Args:
        text (str): text to be compressed

    Returns:
        str: compressed text
    """
    compressed = []
    tokenized = text.split(token_separator)
    previous = None
    for token in tokenized:
        if token != previous:
            compressed.append(token)
            previous = token

    return " ".join(compressed)


def lossless_compression(text: str, token_separator=" ") -> str:
    compressed = []
    tokenized = text.split(token_separator)
    previous = tokenized[0]
    counter = 1
    for token in tokenized[1:]:
        if token != previous and counter > 0:
            compressed.append(previous)
            compressed.append(str(counter))
            previous = token
            counter = 1
        else:
            counter += 1

    # Last token won't be added in the loop
    compressed.append(previous)
    compressed.append(str(counter))

    return " ".join(compressed)


def decompress(text: str, token_separator=" ") -> str:
    decompressed = []
    tokenized = text.split(token_separator)

    for note, count in zip(range(0, len(tokenized), 2), range(1, len(tokenized), 2)):
        decompressed.append(
            " ".join([tokenized[note]] * int(tokenized[count])))

    return " ".join(decompressed)
