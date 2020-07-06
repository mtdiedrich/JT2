from rake_nltk import Rake

import pandas as pd
import numpy as np

import string
import time
import tqdm


def r_a_k_e(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()[0]
