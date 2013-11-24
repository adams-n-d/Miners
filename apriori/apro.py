import sys
import itertools as it
import math
from time import *
from collections import defaultdict



#remove candidates from a set (py dict) that are below support threshold
def prune_sup(candset, thresh):
    for grp in candset.keys():
        if candset[grp] < thresh:
            del candset[grp]
    return candset

#generate a {tuple(tx) : support} dictionary for one-sets
def gen1_set(db, min_sup):
    #we will simultaneously build a hash table for DHP on 2-itemsets
    numbkts = len(db) / min_sup
    Hlist = list() # each bucket is a list of tuples
    for b in range(numbkts):
        Hlist.append( list() )
    #
    onedic = dict()
    for iset in db:
        twosets = list(it.combinations(iset, 2) )
        for pair in twosets:
            bkt = (math.log(pair[0]+1)*10 + math.log(pair[1])) % numbkts
            Hlist[ int(bkt) ].append(pair)
        #
        for itm in iset:
            itup = tuple([itm]) #tuples are hashable, we use the for the dict keys
            if set(itup).issubset( [j for i in onedic.keys() for j in i] ): #if item already in C1, else create dict entry
                onedic[itup] = onedic[itup] + 1
            else:
                onedic[itup] = 1
    #
    return onedic, Hlist

#generate a k-candidate set -- each entry is a k-set tuple of items -- from a (k-1)-set
def genk_set(Lset):
    #sort itemsets and items
    tmplst = map(list, Lset)
    for s in tmplst:
        s.sort()
    tmplst.sort()
    Lset = map(tuple, tmplst)
    #first we do a self join on the
    Ck = []
    i = 0
    j = 1
    while i < len(Lset):
        while j < len(Lset) and Lset[i][:-1] == Lset[j][:-1]:
            j += 1
        for p in range(i,j):
            for q in range(p+1, j):
                Ck.append(Lset[p]+Lset[q][-1:])
        i = j
    #now, prune ineligible subsets
    #for cand in Ck:
    return Ck


def foutput(dic, ofile):
    f = open(ofile, 'w')
    for entry in dic.keys():
        for itm in entry:
            f.write(str(itm) + " ")
        f.write( '(' + str( dic[entry]) + ')' + '\n' )
    f.close()
        



#courtesy http://en.wikipedia.org/wiki/Trie
class Trie:
    def __init__(self):
        self.root = defaultdict(Trie)
        self.value = None
    #
    def add(self, s, value):
        """Add the string `s` to the 
        `Trie` and map it to the given value."""
        head, tail = s[0], s[1:]
        cur_node = self.root[head]
        if not tail:
            cur_node.value = value
            return  # No further recursion
        cur_node.add(tail, value)
    #
    def lookup(self, s, default=None):
        """Look up the value corresponding to 
        the string `s`. Expand the trie to cache the search."""
        head, tail = s[0], s[1:]
        node = self.root[head]
        if tail:
            return node.lookup(tail)
        return node.value or default
    def prefix(self, s):
        """Check whether the string `s` is a prefix 
        of some member. Don't expand the trie on negatives (cf.lookup)"""
        if not s:
            return True
        head, tail = s[0], s[1:]
        if head not in self.root:
            return False  # Not contained
        node = self.root[head]
        return node.prefix(tail)



def triecount(cand, db):
    #build a tree from the candidate set
    candTrie = Trie()
    for c in cand:
        tstring = string.join( map(str, c) )
        candTrie.add(tstring, c)
    txprune = list()
   # for t in db:
    #    for itm in t:
    
    return txprune


def main():
    min_sup = int( sys.argv[2] ) 
    #read file to get itemsets
    with open(sys.argv[1]) as ifile:
        #get transaction DB as a list of itemsets
        txdb = [[int(i) for i in line.split()] for line in ifile ]
    print "Finished reading DB file"
    #generate all 1-itemsets
    #kdic: dictionary of {candidate:support} for freq k-itemsets
    starttime = time()
    kcand, hash2 = gen1_set(txdb, min_sup)  #C1

    for bkt in hash2:
        if len(bkt) < min_sup:
            for itm in set(bkt):
                if itm in kcand.keys():
                    del kcand[itm]

    kset = prune_sup(kcand, min_sup)
    freq_set = kset


    k = 2
    print "Beginning main loop..."
    while( len(freq_set) > 0 ):
        #generate candidate set from kset L^(k-1)
        kcand = genk_set(freq_set.keys())

        freq_set = {}
        #count supports for new candidate set
        #naive counting
        print str(k) + "...counting"
        for cand in kcand:
            cnt = 0
            for t in txdb:
                if set(cand).issubset(t):
                    cnt += 1
            freq_set[cand] = cnt
        freq_set = prune_sup(freq_set, min_sup)
        kset.update(freq_set)
        print "Finished pass " + str((k-1))
        k += 1

    #print kset
    print "done, writing output"
    endtime = time()
    print "Total time: "
    print str(endtime-starttime) + " seconds"
    foutput(kset, sys.argv[3])
    


if __name__ == "__main__":
    main()
