import nltk.classify.util
from nltk import NaiveBayesClassifier
from parser import *
from string import punctuation

def word_feats(words):
    return dict([(word, True) for word in words])


def textClass():
    #dbFile = open("samp.txt")
    dbFile = open("all.txt")

    reviews = list() #each list element is a list of words in the review
    ratings = list() #ratings given
    usefulness = list() #review classification

    tot_recs = 0
    len_tot = 0
    mlen = 0

    #parse the file and create the list to be passed to the NBClassifiers
    while tot_recs < 150000:#True:
        if tot_recs % 1000 == 0:
            print "num records:", tot_recs
        tot_recs += 1
        raw_rec = readRec(dbFile)
        if len(raw_rec) == 0:
            break
        review_text = [word.strip(punctuation) for word in raw_rec["text"]]
        rate_val = str( raw_rec["score"][0] )
        
        prs_rec = parse4ftrs(raw_rec)
        len_tot += prs_rec["length"]
        if prs_rec["length"] > mlen:
            mlen = prs_rec["length"]
        use_val = str( prs_rec["class"] )

        #print use_val, rate_val
        #word feature dictionary
        wfd = word_feats(review_text)

        ratings.append( ( wfd  , rate_val)  )
        usefulness.append( ( wfd, use_val)  )

    dbFile.close()
    print "avg length:", len_tot/tot_recs
    print "max len:", mlen
    #select a cutoff for test v training
    #nrecs = len(ratings)
    nrecs = tot_recs
    rate_cl = NaiveBayesClassifier.train(ratings)
    use_cl = NaiveBayesClassifier.train(usefulness)
    return rate_cl, use_cl
"""
    cutoff = nrecs*2/3
    usetrain = usefulness[:cutoff]
    usetest = usefulness[cutoff:]

    print 'train on %d instances, test on %d instances' % (len(usetrain), len(usetest))

    classifier = NaiveBayesClassifier.train(usetrain)
    print 'accuracy:', nltk.classify.util.accuracy(classifier, usetest)
    classifier.show_most_informative_features()
    tesxt = "the film was very good i laughed".split()
    print classifier.classify(word_feats(tesxt))
    return classifier
"""


if __name__ == "__main__":
    main()
