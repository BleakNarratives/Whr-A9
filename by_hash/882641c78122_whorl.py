#!/usr/bin/env python3
"""Whorl v0.1 | AUTHOR: Bleak/Claude | FILENAME: whorl.py | PATH: ~/whorl.py"""
import re, math, sys
TOKEN_RE = re.compile(r'\s*(?:(#[^\n]*)|([A-Z_][A-Z0-9_]*)|([a-z_][a-zA-Z0-9_]*)|([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)|([{}:]))', re.MULTILINE)
def tokenize(s):
    t=[]
    for m in TOKEN_RE.finditer(s):
        if m.group(1): continue
        elif m.group(2): t.append(('KW',m.group(2)))
        elif m.group(3): t.append(('ID',m.group(3)))
        elif m.group(4): t.append(('NUM',float(m.group(4))))
        elif m.group(5): t.append(('SYM',m.group(5)))
    return t
class P:
    def __init__(s,t): s.t=t; s.p=0
    def peek(s): return s.t[s.p] if s.p<len(s.t) else ('EOF',None)
    def eat(s,ty=None,v=None):
        tok=s.t[s.p]
        if ty and tok[0]!=ty: raise SyntaxError(f"want {ty} got {tok}")
        if v and tok[1]!=v: raise SyntaxError(f"want {v} got {tok[1]}")
        s.p+=1; return tok
    def parse(s):
        n=[]
        while s.peek()[0]!='EOF': n.append(s.stmt())
        return n
    def stmt(s):
        k=s.peek()[1]
        if k in('WAVE','HELIX'): return s.blk(k)
        if k=='EVOLVE': s.eat(); w=s.eat()[1]; s.eat('KW','ALONG'); return('EVOLVE',w,s.eat()[1])
        if k in('ROTATE','MEASURE','EMIT'): s.eat(); return(k,s.eat()[1])
        raise SyntaxError(f"unknown {k}")
    def blk(s,k):
        s.eat(); nm=s.eat()[1]; s.eat('SYM','{'); a={}
        while s.peek()!=('SYM','}'): key=s.eat()[1]; s.eat('SYM',':'); a[key]=s.eat()[1]
        s.eat('SYM','}'); return(k,nm,a)
def D_L(k,p=1.0): return p*k
def D_Q(k,p=0.5): return p*k*k
def D_R(k,p=1.0): return math.sqrt(k*k+p*p)
DISP={'LINEAR':D_L,'QUADRATIC':D_Q,'RELATIVISTIC':D_R}
class I:
    def __init__(s): s.W={}; s.H={}; s.R={}; s.th=0.0
    def run(s,ast):
        for n in ast: s.ex(n)
    def ex(s,n):
        k=n[0]
        if k=='WAVE': s.W[n[1]]={a:(float(v) if isinstance(v,float) else v) for a,v in n[2].items()}
        elif k=='HELIX': s.H[n[1]]={a:(float(v) if isinstance(v,float) else v) for a,v in n[2].items()}
        elif k=='EVOLVE': s.ev(n[1],n[2])
        elif k=='EMIT': print(f"{n[1].upper()}: {s.R.get(n[1].lower(),0.0):.4f}")
    def ev(s,wn,hn):
        w=s.W.get(wn,{}); h=s.H.get(hn,{})
        A0=float(w.get('AMPLITUDE',1.0)); k=float(w.get('WAVENUMBER',1.0))
        sg=float(w.get('SIGMA_X',1.0)); al=float(w.get('ALPHA',0.5))
        ms=float(w.get('MASS',1.0)); vc=float(w.get('VELOCITY',1.0))
        dk=str(w.get('DISPERSION','LINEAR')).upper(); rot=float(h.get('ROTATIONS',1.0))
        t=rot*2*math.pi; df=DISP.get(dk,D_L)
        if dk=='QUADRATIC': amp=A0/math.sqrt(1.0+(al*t/sg**2)**2)
        elif dk=='LINEAR': amp=A0*abs(math.cos(df(k,vc)*t))
        else: om=df(k,ms); amp=A0/math.sqrt(1.0+((k/om)*t/sg)**2)
        s.R['amplitude']=amp
S5="""
WAVE gaussian_packet { AMPLITUDE: 1.0 WAVENUMBER: 1.0 SIGMA_X: 1.0 DISPERSION: QUADRATIC ALPHA: 0.5 }
HELIX h_primary { ROTATIONS: 6.47 }
EVOLVE gaussian_packet ALONG h_primary
MEASURE AMPLITUDE
EMIT AMPLITUDE
"""
def run(src): I().run(P(tokenize(src)).parse())
if __name__=='__main__':
    if len(sys.argv)>1:
        with open(sys.argv[1]) as f: run(f.read())
    else:
        print("Whorl v0.1 — Section 5"); print("="*25); run(S5)
