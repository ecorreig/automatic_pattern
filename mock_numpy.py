__author__ = 'dracks'

import math

def mean(list):
    return reduce(lambda ac, e: e+ac, list, 0.0)/len(list)

def std(list):
    avg=mean(list)
    return math.sqrt(reduce (lambda ac, e: pow(e-avg,2)+ac, list, 0.0)/len(list))