from random import normalvariate as nv

SIM_SPEED_MULT = 100
BASE_CHANCE = 1000

RESOURCE_MEAN = 1
RESOURCE_STDEV = 1

def nvcl(mean, std):
    mn = (mean - std) if (mean - std) >= .75 else .75
    v = nv(mean, std)
    if v < mn:
        return mn
    elif v > mean + 2*std:
        return mean + 2*std
    return v
