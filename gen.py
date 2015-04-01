from html.parser import HTMLParser
import csv
from os import walk
from os.path import join
c = "webkb/course/cornell/http:^^www.tc.cornell.edu^Visualization^Education^cs718^"
c2 = "webkb/course/cornell/http\:\^\^www.cs.cornell.edu\^Info\^Courses\^Current\^CS211\^home.html"

# create a subclass and override the handler methods
class HTMLProcessor(HTMLParser):
  def __init__(self, type):
    self.html_dict = {}
    self.word_dict = {}
    self.doc = 0
    self.docs = [{'type':type}]
    self.type = type
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
    for x in word_data:
      if x in word_dict:
        word_dict[x] += 1
      else:
        word_dict[x] = 1
  
  def new_doc(self):
    self.docs += [{'type':self.type}]
    if self.doc > 0:
      d = self.docs[self.doc]
      for key in d:
        for pd in self.docs[0:self.doc-1]:
          if key not in pd:
            pd[key] = 0
        self.docs[self.doc+1][key] = 0
    self.doc += 1

  def get_data_list(self):
    return self.word_data

def getHeaders(data):
  i = data.index('<')
  head = data[0:i]
  l =  filter(lambda x: x != '', head.split('\n'))
  t = [i.split(':') for i in l]
  d = dict((i[0], i[1].strip()) for i in t)
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

p = HTMLProcessor('class')

def digest(processor, c):
  with open(join("webkb/course/cornell", c)) as f:
    try:
      data = f.read()
    except:
      return
    headers = getHeaders(data)
    html = getHTML(data)
    p.feed(html)
    p.new_doc()
    

for (dirpath, dirnames, filenames) in walk("webkb/course/cornell"):
  for c in filenames:
    digest(p, c)

to_csv(p.docs)
