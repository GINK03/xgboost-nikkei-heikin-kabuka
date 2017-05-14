import os
import sys
import math
import glob
import MeCab
import pickle

m = MeCab.Tagger("-Ochasen")

noun_freq = {}
for name in glob.glob("./download/*"):
  with open(name, "r") as f :
   for da in m.parse(f.read()).strip().split("\n"):
     if "名詞" in da and \
        "名詞-数" not in da and \
        "日" not in da and \
        "年" not in da and \
        "月" not in da and \
        "時" not in da and \
        "分" not in da:
       ts = da.split("\t")
       ... # print(ts[0])
       noun = ts[0]
       if noun_freq.get(noun) is None:
         noun_freq[noun] = 0.
       noun_freq[noun] += 1.

open("noun_freq.pkl", "wb").write( pickle.dumps(noun_freq) )
