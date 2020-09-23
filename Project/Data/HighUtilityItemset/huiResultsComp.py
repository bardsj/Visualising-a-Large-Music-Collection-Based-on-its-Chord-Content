import matplotlib.pyplot as plt
from pymongo import MongoClient
import os
import numpy as np

uri = os.environ['MSC_MONGO_PERSONAL_URI']
col = MongoClient(uri).jamendo.itemsetData

fi = []
fi_length = []
hui = []
hui_length = []

for d in col.find({"fi_type":"frequent"}):
    fi_length.append(len(d['itemsets']['items']))
    fi += [x[1] for x in d['itemsets']['supportPc'].items()]

for d in col.find({"fi_type":"hui"}):
    hui_length.append(len(d['itemsets']))
    hui += [x['minUtil'] for x in d['itemsets']]


w = 0.0033
bins = np.linspace(0,np.mean(fi+hui)+(3*np.std(fi+hui)),40)
plt.hist(fi,bins=bins,width=w,label='Conventional')
plt.hist(hui,bins=bins,width=w,label='High Utility')
plt.legend()
plt.xlim((0,np.mean(fi+hui)+(3*np.std(fi+hui))))
plt.xlabel("Utiltiy/Support Value")
plt.ylabel("Frequency")
plt.show()