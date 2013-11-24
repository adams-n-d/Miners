import pandas as pd
import sys
import string

def getNaiveBayes(testInst, likDict, possClasses, numPriors, numInsts):
    maxlk = 0
    for cls in possClasses:
        estim = numPriors[cls] / float(numInsts)
        for ftr in testInst.index[1:]:
            estim *= (likDict[ftr][ testInst[ftr] ][ cls ]) / float(numPriors[cls])
        if estim > maxlk:
            maxlk = estim
            lklyCls = cls
    return lklyCls


#import training dataset
train = pd.read_csv(sys.argv[1], sep='\t', header=None)

classifications = train['X.1'].unique()
features = train.columns[1:]

#get counts for each possible classification category
clsCnt = list()
for c in classifications:
    clsCnt.append( len( train[ train['X.1']==c ]) )

priorInst = dict( zip(classifications, clsCnt) )

numFtrs = len(features)
numInsts = len(train['X.1'])

likelihoods = list() #holds all training data by number of co-appearances with classifications

#initialize classifying counter -- # of times feature occurs with class
for ftr in features:
    classifier = pd.DataFrame(index = train['X.1'].unique(), columns = train[ftr].unique())
    #
    for cls in classifier.index:
        priors = train[ train['X.1']==cls]
        for attr in classifier.columns:
            classifier[attr][cls] = len( priors[ priors[ftr]==attr] )
    likelihoods.append(classifier)

lik = dict(zip(features, likelihoods))

test = pd.read_csv(sys.argv[2], sep='\t', header=None)


outputLst = list()
#use naive bayesian method to guess classification for test instances
correct = 0
for t in test.index:
    guess = getNaiveBayes(test.ix[t], lik, classifications, priorInst, numInsts)
    outputLst.append( (guess, test.ix[t][0]) )
    if guess == test.ix[t][0]:
        correct += 1

accuracy = correct/float(len(test.index))*100
print "% correct: ", accuracy 
print correct, " out of ", len(test.index)

#write output file
with open(sys.argv[3], 'w') as outFile:
    outFile.write(string.join( ("Training set: ", sys.argv[1], '\n')))
    outFile.write(string.join( ("Test set: ", sys.argv[2], '\n')))
    outFile.write(string.join( ("Percent correct: ", str(accuracy), '\n' )))
    outFile.write(string.join( (str(correct), "out of", str(len(test.index)), '\n' )))
    for r in outputLst:
        outFile.write( string.join(("Class: ", r[1], "   Naive guess: ", r[0], '\n')) )

 



'''
maxlk = 0
for cls in classifications:
    estim = priorInst[cls] / float(numInsts)
    for ftr in testInst.index[1:]:
        estim *= (lik[ftr][ testInst[ftr] ][ cls ])
    estim = estim / (priorInst[cls])**len(testInst.index[1:])
    if estim > maxlk:
        maxlk = estim
        lklyCls = cls

print maxlk, lklyCls
'''




