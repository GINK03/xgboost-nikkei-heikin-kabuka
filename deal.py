import sys
import glob
import math
import os
import MeCab
import re
import pickle
from collections import Counter
""" 分かち書きに変換する """
def step1():
  m = MeCab.Tagger("-Owakati") 
  date_contexts = {}
  allfiles   = glob.glob("download/*")
  for ni, name in enumerate(allfiles):
    print(ni, "/", len(allfiles), name)
    date = re.sub(r"(年|月|日)", "-", name.split("/")[-1].split(" ")[0])[:-1]
    with open(name, "r") as f:
      context = m.parse(f.read()).strip()
      if date_contexts.get(date) is None: 
        date_contexts[date] = ""
      date_contexts[date] += " " + context
  # """ contextsが50000語になるように調整 """
  # date_contexts = { date: contexts[:50000] for date, contexts in date_contexts.items() }
  date_contexts = { date: contexts for date, contexts in date_contexts.items() }
  open("var/date_contexts.pkl", "wb").write(pickle.dumps(date_contexts)) 

""" 単語をindex化する """
def step2():
  m = MeCab.Tagger("-Owakati") 
  term_index = {}
  allfiles   = glob.glob("download/*")
  for ni, name in enumerate(allfiles):
    print(ni, "/", len(allfiles), name)
    with open(name, "r") as f:
      terms = set(m.parse(f.read()).strip().split())
      for term in terms:
        if term_index.get(term) is None:
          term_index[term] = len(term_index)
  open("var/term_index.pkl", "wb").write(pickle.dumps(term_index)) 

""" 日経平均を読み取って 平均値を計算して目的関数を出す """
def step3():
  date_kpi = {}
  with open("var/nikkei_mean.csv") as f:
    for line in f:
      es = iter(re.split(r"\t{1,}", line.strip().replace(" ", "")) )
      date  = next(es)
      start = next(es)
      maxx  = float(next(es))
      minn  = float(next(es))
      date_kpi[date] = (maxx + minn)/2

    open("var/date_kpi.pkl", "wb").write(pickle.dumps(date_kpi))
  print("正常に終了しました")


""" xgboostの形式に変換する, 予想も目的地も同一を使う """
def step4():
  date_kpi      = pickle.loads(open("var/date_kpi.pkl", "rb").read())
  date_contexts = pickle.loads(open("var/date_contexts.pkl", "rb").read())
  term_index    = pickle.loads(open("var/term_index.pkl", "rb").read())

  with open("var/xgboost.svm", "w") as f:
    for date, kpi in sorted(date_kpi.items(), key=lambda x:x[0]):
      print(date, kpi)
      id_freq = {}
      try:
        for term, freq in Counter(date_contexts[date].split()).items():
          id_freq[ term_index[term] ] = math.log(freq + 1) # adhoc
      except KeyError as e:
        print(e)
        continue
      
      feats  = " ".join( ["%d:%04f"%(index, freq) for index, freq in id_freq.items()] )
      tosave = "%d %s\n"%(kpi, feats)
      f.write(tosave)

""" xgboostの形式に変換する, 予想も目的地も同一を使う """
def step4alt():
  date_kpi      = pickle.loads(open("var/date_kpi.pkl", "rb").read())
  date_contexts = pickle.loads(open("var/date_contexts.pkl", "rb").read())
  term_index    = pickle.loads(open("var/term_index.pkl", "rb").read())

  with open("var/xgboost.svm", "w") as f:
    for date, kpi in sorted(date_kpi.items(), key=lambda x:x[0]):
      ts        = date.split("-")
      prev_date = "%s-%s-%02d"%( ts[0], ts[1], int(ts[-1]) - 1 )
      """ 日付づらしは面倒なので対応しない """
      if prev_date == "00":
        continue
      
      print(date, prev_date ,kpi)
      #continue
      id_freq = {}
      try:
        for term, freq in Counter(date_contexts[prev_date].split()).items():
          id_freq[ term_index[term] ] = math.log(freq + 1) # adhoc
      except KeyError as e:
        print(e)
        continue
      
      feats  = " ".join( ["%d:%04f"%(index, freq) for index, freq in id_freq.items()] )
      tosave = "%d %s\n"%(kpi, feats)
      f.write(tosave)

""" xgboostの形式に変換する, 予想に使う素性はnoun（名詞）に限定する """
def step4noun():
  date_kpi      = pickle.loads(open("var/date_kpi.pkl", "rb").read())
  date_contexts = pickle.loads(open("var/date_contexts.pkl", "rb").read())
  term_index    = pickle.loads(open("var/term_index.pkl", "rb").read())
  noun_freq     = pickle.loads(open("noun_freq.pkl", "rb").read())
  with open("var/xgboost.svm", "w") as f:
    for date, kpi in sorted(date_kpi.items(), key=lambda x:x[0]):
      ts        = date.split("-")
      prev_date = "%s-%s-%02d"%( ts[0], ts[1], int(ts[-1]) - 1 )
      """ 日付づらしは面倒なので対応しない """
      if prev_date == "00":
        continue
      
      print(date, prev_date ,kpi)
      id_freq = {}
      try:
        for term, freq in Counter(date_contexts[prev_date].split()).items():
          if noun_freq.get(term) is None:
            continue
          id_freq[ term_index[term] ] = math.log(freq + 1) # adhoc
      except KeyError as e:
        print(e)
        continue
      
      feats  = " ".join( ["%d:%04f"%(index, freq) for index, freq in id_freq.items()] )
      tosave = "%d %s\n"%(kpi, feats)
      f.write(tosave)

""" トレインとテストに分割する """
def step5():
   sets = open("var/xgboost.svm", "r").read().split("\n")
   import random
   random.shuffle(sets)
   train = sets[:int(len(sets)*0.8)]
   test  = sets[int(len(sets)*0.8):]
   open("var/xgboost.svm.train", "w").write("\n".join(train))
   open("var/xgboost.svm.test", "w").write("\n".join(test))

""" トレインする """
def step6():
  os.system("./xgboost.bin var/reg.conf")

""" モデルをダンプする """
def step7():
  os.system("./xgboost.bin var/reg.conf task=dump model_in=0300.model name_dump=dump.txt")

""" f値を計算する """
def step8():
  term_index = pickle.loads( open("var/term_index.pkl", "rb").read() )
  index_term = { index:term for term, index in term_index.items() } 
  fmap = { }
  for term in open("dump.txt", "r").read().split("\n"):
    try:
      f = re.search("\[f(.*?)<", term).group(1)
      term = index_term[int(f)]
      if fmap.get(term) is None:
        fmap[term] = 0.
      fmap[term] += 1.
    except Exception as e:
      #print(e)
      #print(term)
      continue

  for term, imp in sorted(fmap.items(), key=lambda x:x[1]*-1):
    print(term, imp)

if __name__ == '__main__':
  if '--step1' in sys.argv:
    step1()

  if '--step2' in sys.argv:
    step2()

  if '--step3' in sys.argv:
    step3()
  
  if '--step4' in sys.argv:
    step4()

  if '--step4alt' in sys.argv:
    step4alt()

  if '--step4noun' in sys.argv:
    step4noun()
  
  if '--step5' in sys.argv:
    step5()

  if '--step6' in sys.argv:
    step6()

  if '--step7' in sys.argv:
    step7()

  if '--step8' in sys.argv:
    step8()
