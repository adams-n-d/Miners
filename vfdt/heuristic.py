import pandas as pd
from math import *


def Info(S, cls):
    ent = 0
    for i in S[cls].unique():
        grp = S[cls][ S[cls] == i ]
        denom = len(S)
        num = len( grp )
        p = float(num)/denom
        ent -= p*log(p,2)
    return ent



#S is a pd.DataFrame
def InfoA(S, attr, cls):
    ent = 0
    for i in S[attr].unique(): #each poss. value of attr
        Sj = S[ S[attr] == i ]
        p = float(len(Sj)) / len(S)
        ent += p*Info(Sj, cls)
    return ent

def IG(S, attr, cls):
    return Info(S, cls) - InfoA(S, attr, cls)
