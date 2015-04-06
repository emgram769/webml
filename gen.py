from html.parser import HTMLParser
import csv
from os import walk
from os.path import join
import sys
import re

alphanumeric = re.compile('[\W_]+')

# create a subclass and override the handler methods
class HTMLProcessor(HTMLParser):
  def __init__(self):
    self.html_dict = {}
    self.word_dict = {}
    self.doc = -1
    self.docs = []
    super().__init__()

  def handle_starttag(self, tag, attrs):
    if tag in self.html_dict:
      self.html_dict[tag] += 1
    else:
      self.html_dict[tag] = 1

  def handle_endtag(self, tag):
    pass

  def handle_data(self, data):
    word_dict = self.docs[self.doc]
    word_data = data.split()
    for word in word_data:
      x = alphanumeric.sub('', word).lower()
      if x in word_dict:
        word_dict[x] += 1
      else:
        word_dict[x] = 1
  
  def new_doc(self, type):
    if type == -1:
      if self.doc > 0:
        d2 = self.docs[self.doc]
        for key in d2:
          if self.doc > 1:
            for pd in self.docs[0:self.doc-1]:
              if key not in pd:
                pd[key] = 0
              else:
                break
        d = self.docs[self.doc-1]
        for key in d:
          if key not in self.docs[self.doc]:
            self.docs[self.doc][key] = 0
        return
    self.docs += [{}]
    if self.doc > 0:
      d = self.docs[self.doc-1]
      for key in d:
        if self.doc > 1:
          for pd in self.docs[0:self.doc-2]:
            if key not in pd:
              pd[key] = 0
            else:
              break
        self.docs[self.doc][key] = 0
    self.docs[self.doc]['<type>'] = type
    self.doc += 1

  def get_data_list(self):
    return self.word_data

def getHeaders(data):
  i = data.index('<')
  head = data[0:i].strip()
  l = filter(lambda x: x != '', head.split('\n'))
  t = [i.split(':') for i in l]
  d = dict((i[0].strip(), i[1].strip()) for i in t if len(i) > 1)
  return d

def getHTML(data):
  i = data.index('<')
  return data[i:-1]

def to_csv(data):
  keys = data[0].keys()
  with open('output.csv', 'w') as f:
    out = csv.DictWriter(f,fieldnames=keys)
    out.writeheader()
    out.writerows(data)

if len(sys.argv) < 2:
  print("Usage python gen.py directory")
  exit()

p = HTMLProcessor()

def digest(processor, c, type):
  with open(c) as f:
    try:
      data = f.read()
    except:
      return
    headers = getHeaders(data)
    html = getHTML(data)
    p.new_doc(type)
    p.feed(html)
    

for (dirpath, dirnames, files) in walk(sys.argv[1]):
  type = 0
  for d in dirnames:
    print(d, type)
    for (dirp, dirn, filenames) in walk(join(dirpath,d)):
      for c in filenames:
        digest(p, join(dirp, c), type)
    type += 1
  p.new_doc(-1)

to_csv(p.docs)
