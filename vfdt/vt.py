import pandas as pd
import math
import operator
from heuristic import *
from txtCls import *

#define possible classes (binned)
#the more classes, we get greater accuracy and less precision
NCLASSES = 2
CLASSES = range(NCLASSES)
#define names of review attributes
FTR_LABELS = ["length", "rating", "NBrating", "NBuse"]
max_vals = dict(length=25, rating=5, NBrating=5, NBuse=1)

class HoeffdingTree:
    def __init__(self):
        self.root = dtNode(None)


class dtNode:
    count = 0
    def __init__(self, parent, attr_val):
        dtNode.count += 1
        self.parent = parent
        self.children = list()


        cols = list()
        if parent != None:
            self.attr_label = parent.split_attr
            self.attr_val = attr_val
            cols = list(parent.records.columns)
            cols.remove(self.attr_label)

        else:
            self.attr_label = None
            self.attr_val = None
            cols = list(FTR_LABELS)
            cols.append("class")

        self.records = pd.DataFrame(columns=cols)
        #internal nodes are split on an attribute
        self.split_attr = None
        self.classf = None
        #nodes in the Hoeffding tree are always leafs at creation
        self.isLeaf = True

    def splitNode(self, attr):
        self.isLeaf = False
        self.split_attr = attr
        print "splitting on:", attr
        for child in range(max_vals[attr]+1):
            self.children.append( dtNode(self, child) )
        self.records = pd.DataFrame()

    #add record with a dictionary of features
    def addRecord(self, ftrs):
        #print ftrs
        ftr_frame = pd.DataFrame([ftrs, ])
        self.records = (self.records).append(ftr_frame, ignore_index=True)
        
#pass a record down the tree to its leaf, return leaf
def sort(ftr_dict, start, add):
    node = start
    while (node.isLeaf) == False:
        spl_attr = node.split_attr
        branches = node.children
        node = [child for child in branches if ftr_dict[ spl_attr ] == child.attr_val]
        if len(node) == 1:
            node = node[0]
        else:
            print "Error: Multiple children with same value"

        del ftr_dict[spl_attr]
        """for child in branches:
            if ftr_dict[ spl_attr ] == child.attr_val:
                node = child
        """
    #add record to leaf's dataframe
    if add:
        node.addRecord(ftr_dict)
    return node

def getHoeffdingBound(delta, n):
    poss_range = math.log( (NCLASSES), 2 )
    numer = math.sqrt( poss_range * math.log( 1/float(delta) ) )
    return (numer / (2*n))


def main():
    
    #instead of checking for a split every new record, we check every nmin new records
    nmin = 150
    #certainty required before splitting on a node
    cert = 0.99
    delta = 1 - cert

    #initialize root node in Hoeffding tree
    root = dtNode(None, None)
    #get text classifiers

    NBrate, NBuse = textClass()
    print "Got classifiers"

    #open database file for record by record reading
    dbFile = open("all.txt")

    #G is the heuristic calculated to decide attribute for splitting
    #calculate G for the null attribute

    #initialize counters for root leaf to 0

    tot_recs = 0
    #read datastream from file
    while tot_recs < 150000:#True:
        rawRvw = readRec(dbFile)
        if len(rawRvw) == 0:
            break
        """for k,v in rawRvw.iteritems():
        print k
        print v"""
        tot_recs += 1
        features = parse4ftrs(rawRvw)
        features["NBrating"] = round( float( NBrate.classify(word_feats(rawRvw["text"])) ))
        features["NBuse"] = int( NBuse.classify(word_feats(rawRvw["text"])) )

        #print features
        #pass records features down to appropriate leaf
        leaf = sort(features, root, True)
        #increment counters at said leaf
        #determine majority classification at said leaf
        freqs = leaf.records["class"].value_counts()
        most_freq_class = freqs.index[0]
        leaf.classf = most_freq_class
        num_freq_class = freqs[0]
        num_recs = len(leaf.records)
        attr_labels = list(leaf.records.columns)
        attr_labels.remove("class")

        need_test_and_split = (num_freq_class < num_recs) and (num_recs%nmin == 0)
        if need_test_and_split and len(attr_labels) > 0:
             print "db record num:", tot_recs
             #calculate heuristic for attributes at leaf
             Gvals = dict()
             for name in attr_labels:
                 Gvals[name] = IG(leaf.records, name, "class")
             Gvals["null"] = 0#Info(leaf.records, "class")
             print Gvals
             #attrs with best and second best heuristics:
             dmax = max(Gvals.iteritems(), key=operator.itemgetter(1))
             Xa = dmax[0]
             G_Xa = dmax[1]

             del Gvals[Xa]
             d2max = max(Gvals.iteritems(), key=operator.itemgetter(1))
             G_Xb = d2max[1]
             eps = getHoeffdingBound(delta, num_recs)
             print Xa, d2max[0]
             if eps < (G_Xa - G_Xb) and Xa != "null":
                 leaf.splitNode(Xa)

             #determineSplit()

    """print most_freq_class
    print root.records.columns, root.records.index
    print root.records
    print len(root.records)
    print "reached EOF"
    """
    print dtNode.count
    #test VFDT
    correct = 0
    incorrect = 0
    while tot_recs < 200000:
        rawRvw = readRec(dbFile)
        if len(rawRvw) == 0:
            break
        tot_recs += 1
        features = parse4ftrs(rawRvw)
        features["NBrating"] = round( float( NBrate.classify(word_feats(rawRvw["text"])) ))
        features["NBuse"] = int( NBuse.classify(word_feats(rawRvw["text"])) )

        #pass records features down to appropriate leaf
        leaf = sort(features, root, False)
        #increment counters at said leaf
        #determine majority classification at said leaf
        if leaf.classf == None:
            leaf.classf = leaf.parent.classf

        if features["class"] == leaf.classf:
            correct += 1
        else:
            incorrect += 1

    dbFile.close()
    print "Accuracy:", float(correct)/(incorrect+correct)
    return 0



if __name__ == "__main__":
    main()



