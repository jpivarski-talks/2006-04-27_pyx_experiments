from pyx import *
import os

text.defaulttexrunner = text.texrunner("latex")
text.defaulttexrunner.preamble("\AtBeginDocument{\sffamily}")
unit.set(1., 1., 1., 1., "cm")
slidepaper = document.paperformat(11. * unit.cm, 8.25 * unit.cm, "slide")

## class slide #############################################################

class slide:
  def __init__(self, title="", ops=None, test=True):
    if ops == None: self.ops = []
    self.number = True
    self.outline = False
    self.title = title
    self.left = 0.5 * unit.cm
    self.bottom = 0.375 * unit.cm
    self.width = 10. * unit.cm
    self.height = 7.5 * unit.cm
    self.right = self.left + self.width
    self.top = self.bottom + self.height
    self.center = self.left + 0.5*self.width
    self.middle = self.bottom + 0.5*self.height
    self.test = test

  def addop(self, op):
    if self.test: op.test()
    self.ops.append(op)
  def draw(self, *args):
    self.addop(operation("draw", *args))
  def fill(self, *args):
    self.addop(operation("fill", *args))
  def insert(self, *args):
    self.addop(operation("insert", *args))
  def set(self, *args):
    self.addop(operation("set", *args))
  def stroke(self, *args):
    self.addop(operation("stroke", *args))
  def text(self, *args):
    self.addop(operation("text", *args))
  def text_pt(self, *args):
    self.addop(operation("text_pt", *args))

  def __repr__(self):
    s = ""
    n = 0
    for op in self.ops:
      s += str(n)+"\t"+str(op)+"\n"
      n += 1
    return s[0:-1] # remove the last carriage return

  def draw(self, pagenumberthis, pagenumbermax):
    c = canvas.canvas([canvas.clip(path.rect(0.5, 0.375, 10., 7.5))])
    if self.outline:
      c.stroke(path.rect(self.left, self.bottom, self.width, self.height))
    else:
      c.insert(path.rect(self.left, self.bottom, self.width, self.height))
    if self.number:
      c.text(self.right, self.top, str(pagenumberthis)+"/"+str(pagenumbermax), [text.halign.boxright, text.valign.top])
    c.text(self.left, self.top, "\large "+self.title, [text.halign.boxleft, text.valign.top])
    for op in self.ops:
      exec "c."+op.execstr() in {"theop": op, "c": c}
    return c

## class operation #########################################################

class operation:
  def __init__(self, *args):
    self.args = args

  def __str__(self):
    s = self.args[0]+"("
    for a in self.args[1:]:
      if isinstance(a, str): s += "\""+str(a)+"\", "
      else: s += str(a)+", "
    s = s[0:-2] # remove the last comma
    s += ")"
    return s

  def __repr__(self):
    return str(self)

  def execstr(self):
    self.data = []
    i = 0
    s = self.args[0]+"("
    for a in self.args[1:]:
      self.data.append(a)
      s += "theop.data["+str(i)+"],"
      i += 1
    s += ")"
    return s

  def test(self):
    exec "c."+self.execstr() in {"theop": self, "c": canvas.canvas([canvas.clip(path.rect(0.5, 0.375, 10., 7.5))])}

## function render #########################################################

tmp_filename = "/tmp/tmp.eps"
plotter_running = False

def render(s):
  global tmp_filename, plotter_running

  if not isinstance(s, slide): raise TypeError, "render(slide)"
  s.draw("*", "*").writeEPSfile(tmp_filename)
  if not plotter_running:
    os.system("/usr/bin/gv --watch "+tmp_filename+" &")
    plotter_running = True

## function write ##########################################################

def write(slidelist, filename="talk"):
  if isinstance(slidelist, slide): slidelist = [slidelist]
  pages = []
  pagenumber = 1
  for s in slidelist:
    if not isinstance(s, slide): raise TypeError, "write([list, of, slides], \"optional filename\")"
    pagenumber += 1
    pages.append(document.page(s.draw(pagenumber, len(slidelist)), paperformat=slidepaper, centered=0))
  document.document(pages).writePSfile(filename+".ps")

  # Need to explicitly add BoundingBox to pdf copy
  ps = open(filename+".ps")
  pdf = os.popen("/usr/bin/epstopdf --filter > "+filename+".pdf", "w")
  line = ps.readline()
  pdf.write(line)
  pdf.write("%%BoundingBox: 0 0 310 235")
  for line in ps.readlines():
    pdf.write(line)

############################################################################

slides = []

s = slide("oingy")
s.text(5., 5., "hey")
s.text(0, 3, "Looooooong liiiiiiine!", [text.halign.center, text.valign.middle])
s.insert(epsfile.epsfile(s.center, s.middle, "tmp.eps", align="cc"))
s.outline = True
slides.append(s)

s = slide("boingy")
s.text(0, 3, "hey")
s.text(5, 5, "Looooooong liiiiiiine!", [text.halign.center, text.valign.middle])
s.insert(epsfile.epsfile(s.center, s.middle, "tmp.eps", align="cc"))
slides.append(s)

write()
render(s)
