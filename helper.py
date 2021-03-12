import nltk

#@paragraph should be a word tokenized paragraph
#@phrases should be a LIST of word tokenized phrases
def get_after_prefix(paragraph, phrases):
    post = set()
    for p in phrases:
        for i in range(len(paragraph)):
            if p[0] == paragraph[i]:
                match = True
                L = len(p)
                if i+L < len(paragraph):
                    for k in range(1,L):
                        w1 = p[k]
                        w2 = paragraph[i+k]
                        if p[k] != paragraph[i+k]:
                            match = False
                            break
                    if match:
                        post.add(paragraph[i+L])
    return post

"""
@paragraph should be a POS tokenized paragraph
@phrases should be a LIST of word tokenized phrases 
@POS should be a LIST of pos
@ignore is whether you ignore the pos, or search for the pos
"""
def get_POS_after_prefix(paragraph, phrases, POS, ignore=False):
    post = set()
    for p in phrases:
        for i in range(len(paragraph)):
            (word_i, pos_i) = paragraph[i]
            if p[0] == word_i:
                match = True
                L = len(p)
                if i+L < len(paragraph):
                    for k in range(1,L):
                        #w1 = p[k]
                        (word_ik, pos_ik) = paragraph[i+k]
                        if p[k] != word_ik:
                            match = False
                            break
                    if match:
                        for j in range(i+L,len(paragraph)):
                            (word_j, pos_j) = paragraph[j]
                            if not ignore:
                                if pos_j in POS:
                                    post.add(word_j)
                                    break
                            else:
                                if pos_j in POS:
                                    1+1
                                else:
                                    post.add(word_j)
                                    break
    return post

def apply(func, array):
    A = []
    for a in array:
        A.append(func(a))
    return A

para = 'Whisk lemon juice, oil, vinegar, onion flakes, garlic, lemon zest, Greek seasoning, poultry seasoning, oregano, pepper, and thyme together in a bowl and pour into a resealable plastic bag.'
p = ["use", "in"]
nouns = ["NN","NNP","NNS"]
adj = ["JJ","JJR","JJS","DT"]
p = apply(nltk.word_tokenize,p)
para = nltk.word_tokenize(para)
#print(get_after_prefix(para, p))

para = nltk.pos_tag(para)
#print(get_POS_after_prefix(para, p, adj,ignore=True))