from rake_nltk import Rake


def r_a_k_e(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()[0]
