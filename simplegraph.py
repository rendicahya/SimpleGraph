class SimpleGraph:
  def __init__(self):
    self._spo = {}
    self._pos = {}
    self._osp = {}

  def add(self, sub, pred, obj):
    self._addToIndex(self._spo, sub, pred, obj)
    self._addToIndex(self._pos, pred, obj, sub)
    self._addToIndex(self._osp, obj, sub, pred)

  def _addToIndex(self, index, a, b, c):
    if a not in index:
      index[a] = {b:set([c])}
    else:
      if b not in index[a]:
        index[a][b] = set([c])
      else: index[a][b].add(c)

  def triples(self, sub, pred, obj):
    try:
      if sub != None:
        if pred != None:
          if obj != None:
            if obj in self._spo[sub][pred]:
              yield (sub, pred, obj)
          else:
            for retObj in self._spo[sub][pred]:
              yield (sub, pred, retObj)
        else:
          if obj != None:
            for retPred in self._osp[obj][sub]:
              yield (sub, retPred, obj)
          else:
            for retPred, objSet in self._spo[sub].items():
              for retObj in objSet:
                yield (sub, retPred, retObj)
      else:
        if pred != None:
          if obj != None:
            for retSub in self._pos[pred][obj]:
              yield (retSub, pred, obj)
          else:
            for retObj, subSet in self._pos[pred].items():
              for retSub in subSet:
                yield (retSub, pred, retObj)
        else:
          if obj != None:
            for retSub, predSet in self._osp[obj].items():
              for retPred in predSet:
                yield (retSub, retPred, obj)
          else:
            for retSub, predSet in self._spo.items():
              for retPred, objSet in predSet.items():
                for retObj in objSet:
                  yield (retSub, retPred, retObj)
    except KeyError:
      pass 

  def query(self,clauses):
    bindings = None

    for clause in clauses:
      bpos = {}
      qc = []

      for pos, x in enumerate(clause):
        if x.startswith('?'):
          qc.append(None)
          bpos[x] = pos
        else:
          qc.append(x)

      rows = list(self.triples((qc[0], qc[1], qc[2])))

      if bindings == None:
        bindings = []

        for row in rows:
          binding = {}

          for var, pos in bpos.items():
            binding[var] = row[pos]
          bindings.append(binding)
      else:
        newb = []

        for binding in bindings:
          for row in rows:
            validmatch = True
            tempbinding = binding.copy()

            for var, pos in bpos.items():
              if var in tempbinding:
                if tempbinding[var] != row[pos]:
                  validmatch = False
              else:
                tempbinding[var] = row[pos]

            if validmatch:
              newb.append(tempbinding)

        bindings = newb
    return bindings

  def value(self, sub=None, pred=None, obj=None):
    for retSub, retPred, retObj in self.triples(sub, pred, obj):
      if sub is None: return retSub
      if pred is None: return retPred
      if obj is None: return retObj
      break

    return None

  def remove(self, sub, pred, obj):
    triples = list(self.triples((sub, pred, obj)))

    for (delSub, delPred, delObj) in triples:
      self._removeFromIndex(self._spo, delSub, delPred, delObj)
      self._removeFromIndex(self._pos, delPred, delObj, delSub)
      self._removeFromIndex(self._osp, delObj, delSub, delPred)

  def _removeFromIndex(self, index, a, b, c):
    try:
      bs = index[a]
      cset = bs[b]
      cset.remove(c)
      
      if len(cset) == 0:
        del bs[b]
      if len(bs) == 0:
        del index[a]
    except KeyError:
      pass
  
  def merge(self, graph):
    for s, p, o in graph.triples(None, None, None):
      self.add(s, p, o)

  def print(self):
    for t in self.triples(None, None, None):
      print('<' + str(t[0]) + '> <' + str(t[1]) + '> ' + str(t[2]))

  def load(self, filename):
    f = open(filename, "rb")
    reader = csv.reader(f)

    for sub, pred, obj in reader:
      sub = unicode(sub, "UTF-8")
      pred = unicode(pred, "UTF-8")
      obj = unicode(obj, "UTF-8")
      self.add((sub, pred, obj))

    f.close()

  def save(self, filename):
    f = open(filename, "wb")
    writer = csv.writer(f)

    for sub, pred, obj in self.triples((None, None, None)):
      writer.writerow([sub.encode("UTF-8"), pred.encode("UTF-8"), obj.encode("UTF-8")])

    f.close()