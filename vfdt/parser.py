from txtCls import *
NCLASSES = 2
#lenvals = 

def parse4ftrs(recDict):
    #current features:
    #review length, rating/sentiment agreement, rating, product type
    ftr = dict()
    #word length of review
    ftr["length"] = len( recDict["text"] ) / 30
    if ftr["length"] > 25:
        ftr["length"] = 25
    ftr["rating"] = round( float( recDict["score"][0] ))
    divs = recDict["helpfulness"][0].split('/')
    if divs[1] == '0':
        ftr["class"] = (float('NaN'))
    else:
        ftr["class"] = int(100*(float(divs[0]) / float(divs[1]))) / (100/(NCLASSES-1))
    if ftr["class"] == NCLASSES:
        ftr["class"] = NCLASSES-1

    #need to bin numeric attributes
    return ftr


def readRec(fil):
    parse = dict()
    line = fil.readline()
    if len(line)==0:
        return list()
    while line != '\n':
        while ':' not in line:
            while '/' not in line:
                line = fil.readline()
        line = line.strip('\n')
        #print line
        names = line.split()
        if (len(names) <2):
            print ('/' in line)
            print names
        attr = names[0].split('/')[1].strip(':')
        #print attr
        parse[attr] = names[1:]
        line = fil.readline()
        
        
    #ignore missing data
    if parse["helpfulness"] == ['0/0']:
        parse = readRec(fil)
    return parse


