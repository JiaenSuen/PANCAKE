from __future__ import annotations
import json, math, random, statistics, csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'meta_results'
DATA=ROOT/'meta_datasets'

@dataclass
class Problem:
    name:str
    family:str
    coords:List[Tuple[float,float]]
    candidates:List[List[Tuple[int,float]]]
    unit_cost:float=0.25

@dataclass
class Sol:
    order:List[int]
    src:List[int]
    score:float=math.inf
    dist:float=math.inf
    purchase:float=math.inf
    def clone(self): return Sol(self.order.copy(),self.src.copy(),self.score,self.dist,self.purchase)

@dataclass
class RR:
    alg:str; inst:str; family:str; seed:int; score:float; evals:int; trace:List[Tuple[int,float]]

# ---------- common representation / objective ----------
def evaluate(p:Problem,s:Sol):
    x0=y0=0.0; d=0.0; buy=0.0
    for item in s.order:
        node,price=p.candidates[item][s.src[item]]; x,y=p.coords[node]
        d+=math.hypot(x-x0,y-y0); buy+=price; x0,y0=x,y
    s.dist=d;s.purchase=buy;s.score=buy+p.unit_cost*d
    return s.score

def random_sol(p,rng):
    o=list(range(len(p.candidates)));rng.shuffle(o)
    return Sol(o,[rng.randrange(len(c)) for c in p.candidates])

def greedy_sol(p:Problem,rng:random.Random,mode='incremental'):
    rem=set(range(len(p.candidates))); order=[]; src=[0]*len(p.candidates); x0=y0=0.0
    while rem:
        opts=[]
        for d in rem:
            best=None
            for si,(node,price) in enumerate(p.candidates[d]):
                x,y=p.coords[node]
                if mode=='price': key=price+0.05*p.unit_cost*math.hypot(x-x0,y-y0)
                elif mode=='nearest': key=p.unit_cost*math.hypot(x-x0,y-y0)+0.05*price
                else: key=price+p.unit_cost*math.hypot(x-x0,y-y0)
                if best is None or key<best[0]: best=(key,si,x,y)
            opts.append((best[0]*(1+rng.uniform(-0.03,0.03)),d,best[1],best[2],best[3]))
        _,d,si,x0,y0=min(opts)
        order.append(d);src[d]=si;rem.remove(d)
    return Sol(order,src)

def swap(s,rng):
    if len(s.order)>1:
        i,j=rng.sample(range(len(s.order)),2);s.order[i],s.order[j]=s.order[j],s.order[i]

def reverse(s,rng):
    if len(s.order)>1:
        i,j=sorted(rng.sample(range(len(s.order)),2));s.order[i:j+1]=reversed(s.order[i:j+1])

def insert(s,rng):
    if len(s.order)>2:
        i,j=rng.sample(range(len(s.order)),2);v=s.order.pop(i);s.order.insert(j,v)

def block_reloc(s,rng):
    n=len(s.order)
    if n<4:return
    i,j=sorted(rng.sample(range(n),2)); seg=s.order[i:j+1]; rem=s.order[:i]+s.order[j+1:]; pos=rng.randrange(len(rem)+1);s.order=rem[:pos]+seg+rem[pos:]

def change_source(p,s,rng,count=1):
    n=len(s.src)
    for _ in range(count):
        d=rng.randrange(n);m=len(p.candidates[d])
        if m>1:
            old=s.src[d];z=rng.randrange(m-1);s.src[d]=z+(z>=old)

def joint_move(p,s,rng):
    # Coupled order/source move: relocate an item and simultaneously choose its best source
    if len(s.order)<2:return
    d=rng.choice(s.order); oldpos=s.order.index(d); s.order.pop(oldpos); newpos=rng.randrange(len(s.order)+1);s.order.insert(newpos,d)
    # evaluate local predecessor/successor proxy for all sources
    pos=s.order.index(d); prev=(0.0,0.0) if pos==0 else p.coords[p.candidates[s.order[pos-1]][s.src[s.order[pos-1]]][0]]
    nxt=None if pos==len(s.order)-1 else p.coords[p.candidates[s.order[pos+1]][s.src[s.order[pos+1]]][0]]
    best=(math.inf,s.src[d])
    for si,(node,price) in enumerate(p.candidates[d]):
        x,y=p.coords[node]; val=price+p.unit_cost*math.hypot(x-prev[0],y-prev[1])
        if nxt is not None: val+=p.unit_cost*math.hypot(nxt[0]-x,nxt[1]-y)
        if val<best[0]:best=(val,si)
    s.src[d]=best[1]

def ox(a,b,rng):
    n=len(a); i,j=sorted(rng.sample(range(n),2)); c=[None]*n;c[i:j+1]=a[i:j+1];used=set(c[i:j+1]);fill=[x for x in b if x not in used];k=0
    for t in list(range(i))+list(range(j+1,n)):c[t]=fill[k];k+=1
    return c

def cross(a:Sol,b:Sol,rng):
    return Sol(ox(a.order,b.order,rng),[a.src[i] if rng.random()<.5 else b.src[i] for i in range(len(a.src))])

def align(child,target,rng,fraction):
    n=len(child.order);k=max(1,min(n,int(round(n*fraction)))); loc={d:i for i,d in enumerate(child.order)}
    for pos in rng.sample(range(n),k):
        want=target.order[pos];here=loc[want]
        if here!=pos:
            displaced=child.order[pos];child.order[pos],child.order[here]=child.order[here],child.order[pos];loc[want]=pos;loc[displaced]=here
        if rng.random()<.7:child.src[want]=target.src[want]

def op_apply(p,s,rng,op):
    if op=='swap':swap(s,rng)
    elif op=='reverse':reverse(s,rng)
    elif op=='insert':insert(s,rng)
    elif op=='source':change_source(p,s,rng,1)
    elif op=='joint':joint_move(p,s,rng)
    elif op=='block':block_reloc(s,rng)

# ---------- datasets: multiple landscapes, not one solver-friendly distribution ----------
def add_node(coords,x,y):coords.append((float(x),float(y)));return len(coords)-1

def generate_problem(family:str,idx:int,n=18,seed=20260922)->Problem:
    rng=random.Random(seed+idx*1009+sum(map(ord,family))*17);coords=[];cands=[];u=.25
    if family=='uniform':
        pool=[add_node(coords,rng.uniform(-450,450),rng.uniform(-450,450)) for _ in range(max(80,n*6))]
        for i in range(n):
            base=rng.uniform(35,110); nodes=rng.sample(pool,rng.randint(6,12)); cands.append([(v,max(5,base*rng.uniform(.65,1.4))) for v in nodes])
    elif family=='clustered':
        centers=[(-320,-180),(300,-210),(-120,310),(330,250)]
        pool=[];cl=[]
        for ci,(cx,cy) in enumerate(centers):
            for _ in range(max(20,n*2)):
                pool.append(add_node(coords,rng.gauss(cx,55),rng.gauss(cy,55)));cl.append(ci)
        for i in range(n):
            home=i%len(centers); ids=[v for v,c in zip(pool,cl) if c==home]; alt=[v for v,c in zip(pool,cl) if c!=home]
            nodes=rng.sample(ids,min(5,len(ids)))+rng.sample(alt,min(3,len(alt)))
            base=rng.uniform(40,100);cands.append([(v,max(5,base*rng.uniform(.75,1.25))) for v in nodes])
    elif family=='price_distance_conflict':
        # near sources expensive, far sources cheap => source and route order must be co-optimized
        for i in range(n):
            arr=[]
            for radius,prmul in [(90,1.45),(230,1.0),(430,.58)]:
                for _ in range(2):
                    ang=rng.random()*2*math.pi;node=add_node(coords,radius*math.cos(ang)+rng.gauss(0,25),radius*math.sin(ang)+rng.gauss(0,25));arr.append((node,rng.uniform(55,95)*prmul))
            cands.append(arr)
    elif family=='shared_hubs':
        hubs=[add_node(coords,-280,-40),add_node(coords,250,-30),add_node(coords,10,300)]
        locals=[add_node(coords,rng.uniform(-360,360),rng.uniform(-360,360)) for _ in range(n*3)]
        for i in range(n):
            arr=[]
            # shared hubs create strong cross-item coupling
            base=rng.uniform(48,90)
            for h in hubs:arr.append((h,base*rng.uniform(.90,1.15)))
            for v in rng.sample(locals,3):arr.append((v,base*rng.uniform(.60,.95)))
            cands.append(arr)
    elif family=='deceptive_groups':
        # individually switching to a remote cheap cluster can hurt; coordinated group moves pay off.
        A=(-330,0);B=(330,0)
        for i in range(n):
            arr=[]; grp=0 if i<n//2 else 1; target=A if grp==0 else B; other=B if grp==0 else A
            # local expensive near origin
            for _ in range(2):
                node=add_node(coords,rng.gauss(0,65),rng.gauss(0,65));arr.append((node,rng.uniform(85,115)))
            # cheap sources concentrated by item group in remote cluster
            for _ in range(3):
                node=add_node(coords,rng.gauss(target[0],35),rng.gauss(target[1],35));arr.append((node,rng.uniform(18,42)))
            # distractor mid-price in opposite cluster
            node=add_node(coords,rng.gauss(other[0],45),rng.gauss(other[1],45));arr.append((node,rng.uniform(48,70)))
            cands.append(arr)
        u=.30
    else:raise ValueError(family)
    return Problem(f'{family}_{idx:02d}',family,coords,cands,u)

def generate_suite(instances_per_family=4,n=18):
    DATA.mkdir(exist_ok=True); probs=[]
    for fam in ['uniform','clustered','price_distance_conflict','shared_hubs','deceptive_groups']:
        for i in range(1,instances_per_family+1):
            p=generate_problem(fam,i,n=n);probs.append(p)
            payload={'name':p.name,'family':p.family,'unit_cost':p.unit_cost,'coords':p.coords,'candidates':p.candidates}
            (DATA/f'{p.name}.json').write_text(json.dumps(payload),encoding='utf-8')
    return probs

# ---------- baselines faithful to the user's C# designs ----------
def run_ga(p,seed,budget,popn=30):
    rng=random.Random(seed);ev=0;pop=[];tr=[]
    for _ in range(min(popn,budget)):
        s=random_sol(p,rng);evaluate(p,s);ev+=1;pop.append(s)
    best=min(pop,key=lambda s:s.score).clone();tr.append((ev,best.score))
    while ev<budget:
        new=[best.clone()]
        def tour():
            a,b=rng.sample(pop,2);return a if a.score<b.score else b
        while len(new)<popn and ev<budget:
            a,b=tour(),tour();c=cross(a,b,rng) if rng.random()<.8 else a.clone()
            if rng.random()<.2: (swap if rng.random()<.5 else (lambda s,r: change_source(p,s,r,1)))(c,rng)
            evaluate(p,c);ev+=1;new.append(c)
            if c.score<best.score:best=c.clone();tr.append((ev,best.score))
        while len(new)<popn:new.append(best.clone())
        pop=new
    return RR('GA',p.name,p.family,seed,best.score,ev,tr)

def tabu_core(p,rng,budget,initial=None,ev0=0,best0=None,trace=None,neigh=24):
    ev=ev0;tr=trace if trace is not None else []
    cur=initial.clone() if initial else random_sol(p,rng)
    if initial is None:evaluate(p,cur);ev+=1
    best=(best0.clone() if best0 else cur.clone());tenure=max(7,len(p.candidates)//2);tabu={};it=0
    if not tr:tr.append((ev,best.score))
    while ev<budget:
        it+=1;cands=[]
        for _ in range(min(neigh,budget-ev)):
            s=cur.clone();typ=rng.randrange(3)
            if typ==0:
                i,j=sorted(rng.sample(range(len(s.order)),2));s.order[i],s.order[j]=s.order[j],s.order[i];mv=('sw',i,j)
            elif typ==1:
                i,j=sorted(rng.sample(range(len(s.order)),2));s.order[i:j+1]=reversed(s.order[i:j+1]);mv=('rv',i,j)
            else:
                d=rng.randrange(len(s.src));old=s.src[d];m=len(p.candidates[d]);z=rng.randrange(m-1);ns=z+(z>=old);s.src[d]=ns;mv=('so',d,ns)
            evaluate(p,s);ev+=1
            if tabu.get(mv,-1)<=it or s.score<best.score:cands.append((s,mv))
        if not cands:continue
        cur,mv=min(cands,key=lambda q:q[0].score);tabu[mv]=it+tenure
        if cur.score<best.score:best=cur.clone();tr.append((ev,best.score))
    return best,ev,tr

def run_tabu(p,seed,budget):
    rng=random.Random(seed);b,e,t=tabu_core(p,rng,budget);return RR('Tabu',p.name,p.family,seed,b.score,e,t)

def run_ga_tabu(p,seed,budget):
    # Memetic interpretation of user's GA + Tabu mutation: GA exploration then TS intensification under common FE budget.
    rng=random.Random(seed);cut=max(40,int(.65*budget));ev=0;pop=[];tr=[];popn=24
    for _ in range(min(popn,cut)):
        s=random_sol(p,rng);evaluate(p,s);ev+=1;pop.append(s)
    best=min(pop,key=lambda s:s.score).clone();tr.append((ev,best.score))
    while ev<cut:
        new=[best.clone()]
        while len(new)<popn and ev<cut:
            a,b=rng.sample(pop,2);a=a if a.score<b.score else b;c,d=rng.sample(pop,2);b=c if c.score<d.score else d
            z=cross(a,b,rng); 
            if rng.random()<.25:swap(z,rng)
            if rng.random()<.30:change_source(p,z,rng,1)
            evaluate(p,z);ev+=1;new.append(z)
            if z.score<best.score:best=z.clone();tr.append((ev,best.score))
        while len(new)<popn:new.append(best.clone())
        pop=new
    best,ev,tr=tabu_core(p,rng,budget,initial=best,ev0=ev,best0=best,trace=tr,neigh=20)
    return RR('GA+Tabu',p.name,p.family,seed,best.score,ev,tr)

def run_aco(p,seed,budget,ants=25):
    rng=random.Random(seed);ev=0;tr=[];n=len(p.candidates)
    # pheromone is item/source transition keyed by actual node ids; dictionary avoids dense matrices
    tau:Dict[Tuple[int,int],float]={};best=None
    origin=-1;rho=.10;alpha=1.;beta=2.;Q=1.
    while ev<budget:
        colony=[]
        for _ in range(min(ants,budget-ev)):
            rem=set(range(n));order=[];src=[0]*n;cur_node=origin
            while rem:
                moves=[];total=0.
                cx=cy=0.0 if cur_node==-1 else None
                if cur_node!=-1:cx,cy=p.coords[cur_node]
                else:cx=cy=0.0
                for d in rem:
                    for si,(node,price) in enumerate(p.candidates[d]):
                        x,y=p.coords[node];eta=1.0/(price+p.unit_cost*math.hypot(x-cx,y-cy)+1e-9);ph=tau.get((cur_node,node),1.0);w=(ph**alpha)*(eta**beta);moves.append((d,si,node,w));total+=w
                r=rng.random()*total;acc=0.;pick=moves[-1]
                for m in moves:
                    acc+=m[3]
                    if acc>=r:pick=m;break
                d,si,node,_=pick;order.append(d);src[d]=si;rem.remove(d);cur_node=node
            s=Sol(order,src);evaluate(p,s);ev+=1;colony.append(s)
            if best is None or s.score<best.score:best=s.clone();tr.append((ev,best.score))
        # evaporate only instantiated edges
        for k in list(tau):tau[k]*=(1-rho)
        for s in colony:
            delta=Q/max(s.score,1e-9);prev=origin
            for d in s.order:
                node=p.candidates[d][s.src[d]][0];tau[(prev,node)]=tau.get((prev,node),1.0)+delta;prev=node
    return RR('ACO',p.name,p.family,seed,best.score,ev,tr)

def move_toward(s,target,rng,fraction):align(s,target,rng,fraction)

def run_pso(p,seed,budget,npop=30):
    rng=random.Random(seed);ev=0;tr=[];particles=[]
    for _ in range(min(npop,budget)):
        s=random_sol(p,rng);evaluate(p,s);ev+=1;particles.append([s,s.clone()])
    g=min((q[1] for q in particles),key=lambda s:s.score).clone();tr.append((ev,g.score));iters=0;maxiters=max(1,(budget-ev)//max(1,npop))
    while ev<budget:
        iters+=1;comm=min(1.,iters/maxiters)
        for q in particles:
            if ev>=budget:break
            pos,pbest=q; info=g if rng.random()<comm else rng.choice(particles)[1]
            if rng.random()<.5:reverse(pos,rng)
            if rng.random()<1.0:move_toward(pos,pbest,rng,rng.random())
            if rng.random()<1.0:move_toward(pos,info,rng,rng.random())
            if rng.random()<.5:change_source(p,pos,rng,1)
            evaluate(p,pos);ev+=1
            if pos.score<pbest.score:q[1]=pos.clone()
            if q[1].score<g.score:g=q[1].clone();tr.append((ev,g.score))
    return RR('DPSO',p.name,p.family,seed,g.score,ev,tr)

def run_dwoa_original(p,seed,budget,npop=20):
    rng=random.Random(seed);ev=0;tr=[];pop=[]
    for _ in range(min(npop,budget)):
        s=random_sol(p,rng);evaluate(p,s);ev+=1;pop.append(s)
    best=min(pop,key=lambda s:s.score).clone();tr.append((ev,best.score));iter_i=0;maxit=max(1,(budget-ev)//max(1,npop))
    while ev<budget:
        iter_i+=1;a=2*(1-min(1,iter_i/maxit))
        for i,cur in enumerate(pop):
            if ev>=budget:break
            A=2*a*rng.random()-a;pcoin=rng.random();child=cur.clone()
            if pcoin<.5:
                if abs(A)<1:align(child,best,rng,min(1,abs(A)/2+1/len(child.order)))
                else:child=rng.choice(pop).clone();block_reloc(child,rng)
                change_source(p,child,rng,1)
            else:reverse(child,rng);change_source(p,child,rng,1)
            evaluate(p,child);ev+=1
            if child.score<cur.score:pop[i]=child
            if child.score<best.score:best=child.clone();tr.append((ev,best.score))
    return RR('DWOA-original',p.name,p.family,seed,best.score,ev,tr)

def run_dwoa_tabu(p,seed,budget,npop=20):
    # Corrected version of the intended C# WOA+TS hybrid: the Tabu-refined solution is retained.
    rng=random.Random(seed);cut=max(npop,int(.70*budget));ev=0;tr=[];pop=[]
    for _ in range(min(npop,cut)):
        z=random_sol(p,rng);evaluate(p,z);ev+=1;pop.append(z)
    best=min(pop,key=lambda z:z.score).clone();tr.append((ev,best.score));iter_i=0;maxit=max(1,(cut-ev)//max(1,npop))
    while ev<cut:
        iter_i+=1;a=2*(1-min(1,iter_i/maxit))
        for i,cur in enumerate(pop):
            if ev>=cut:break
            A=2*a*rng.random()-a;pc=rng.random();child=cur.clone()
            if pc<.5:
                if abs(A)<1:align(child,best,rng,min(1,abs(A)/2+1/len(child.order)))
                else:child=rng.choice(pop).clone();block_reloc(child,rng)
                change_source(p,child,rng,1)
            else:reverse(child,rng);change_source(p,child,rng,1)
            evaluate(p,child);ev+=1
            if child.score<cur.score:pop[i]=child
            if child.score<best.score:best=child.clone();tr.append((ev,best.score))
    # Use all remaining objective evaluations for Tabu intensification from the WOA best.
    best,ev,tr=tabu_core(p,rng,budget,initial=best,ev0=ev,best0=best,trace=tr,neigh=20)
    return RR('DWOA+Tabu-fixed',p.name,p.family,seed,best.score,ev,tr)

# ---------- literature-informed research variants ----------
def pop_diversity(pop):
    if len(pop)<2:return 0.0
    n=len(pop[0].order);pairs=0;acc=0.0
    for i in range(min(len(pop),12)):
        for j in range(i+1,min(len(pop),12)):
            pos={d:k for k,d in enumerate(pop[j].order)};acc+=sum(abs(k-pos[d]) for k,d in enumerate(pop[i].order))/(n*n);pairs+=1
    return acc/max(1,pairs)

def local_best_of(p,base,rng,ops,remaining,tries=4):
    best=base.clone();used=0
    for _ in range(min(tries,remaining)):
        z=base.clone();op_apply(p,z,rng,rng.choice(ops));evaluate(p,z);used+=1
        if z.score<best.score:best=z
    return best,used

def run_dwoa_research(p,seed,budget,npop=20):
    # Literature-informed adaptation: double-layer discrete encoding + genetic leader update,
    # stagnation/diversity-triggered VNS and elite restart.
    rng=random.Random(seed);ev=0;tr=[];pop=[]
    # Common random initialization: literature-inspired gains below come from search operators, not privileged warm starts.
    init=[random_sol(p,rng) for _ in range(npop)]
    for s in init[:min(npop,budget)]:evaluate(p,s);ev+=1;pop.append(s)
    best=min(pop,key=lambda s:s.score).clone();tr.append((ev,best.score));stagn=0
    while ev<budget:
        progress=ev/budget;a=2*(1-progress);improved=False
        for i in range(len(pop)):
            if ev>=budget:break
            cur=pop[i];A=2*a*rng.random()-a;pc=rng.random()
            if pc<.5 and abs(A)<1:
                child=cross(cur,best,rng);align(child,best,rng,.18+.52*(1-abs(A)))
            elif pc<.5:
                ref=rng.choice(pop);child=cross(cur,ref,rng);block_reloc(child,rng)
            else:
                child=cross(cur,best,rng); (insert if rng.random()<.5 else reverse)(child,rng)
            if rng.random()<.72:change_source(p,child,rng,1)
            if rng.random()<.28:joint_move(p,child,rng)
            evaluate(p,child);ev+=1
            # small VNS around competitive offspring
            local=child
            if ev<budget and child.score <= cur.score*1.08:
                local,u=local_best_of(p,child,rng,['swap','insert','reverse','source','joint'],budget-ev,tries=2);ev+=u
            if local.score<cur.score:pop[i]=local
            if local.score<best.score:best=local.clone();tr.append((ev,best.score));improved=True
        stagn=0 if improved else stagn+1
        # Stagnation / low-diversity trigger, analogous to VNS/entropy-triggered local search in recent discrete WOA work.
        if ev<budget and (stagn>=3 or pop_diversity(pop)<.10):
            refined,u=local_best_of(p,best,rng,['insert','reverse','joint','source','block'],budget-ev,tries=min(8,budget-ev));ev+=u
            if refined.score<best.score:best=refined.clone();tr.append((ev,best.score));stagn=0
            # partial elite-diversity restart
            worst=sorted(range(len(pop)),key=lambda k:pop[k].score,reverse=True)[:max(1,len(pop)//5)]
            for wi in worst:
                if ev>=budget:break
                z=best.clone();op_apply(p,z,rng,rng.choice(['block','insert','source','joint']));op_apply(p,z,rng,rng.choice(['swap','source']))
                evaluate(p,z);ev+=1;pop[wi]=z
                if z.score<best.score:best=z.clone();tr.append((ev,best.score))
    return RR('DWOA-AVNS',p.name,p.family,seed,best.score,ev,tr)

from algorithms import run_dwoa_avns, run_dfox_base, run_dfox_apns

ALGS=[run_ga,run_tabu,run_ga_tabu,run_aco,run_pso,run_dwoa_original,run_dwoa_tabu,run_dwoa_avns,run_dfox_base,run_dfox_apns]

# ---------- metrics ----------
def hit_eval(trace,target):
    for e,v in trace:
        if v<=target:return e
    return None

def auc_norm(trace,budget,bks):
    # area under best-so-far RPD curve over normalized evaluation axis (lower is better)
    tr=sorted(trace);prev=0;last=tr[0][1] if tr else math.inf;area=0.0
    for e,v in tr:
        e=min(e,budget);area+=(e-prev)/budget*100*(last-bks)/bks;prev=e;last=min(last,v)
    if prev<budget:area+=(budget-prev)/budget*100*(last-bks)/bks
    return area

def exact_score(p:Problem):
    n=len(p.candidates);dp={}
    for d in range(n):
        for si,(node,price) in enumerate(p.candidates[d]):
            x,y=p.coords[node];dp[(1<<d,d,si)]=price+p.unit_cost*math.hypot(x,y)
    for size in range(1,n):
        nxt={}
        for (mask,last,si),val in dp.items():
            if mask.bit_count()!=size:continue
            ln=p.candidates[last][si][0];lx,ly=p.coords[ln]
            for d in range(n):
                if mask>>d&1:continue
                nm=mask|1<<d
                for sj,(node,price) in enumerate(p.candidates[d]):
                    x,y=p.coords[node];nv=val+price+p.unit_cost*math.hypot(x-lx,y-ly);k=(nm,d,sj)
                    if nv<nxt.get(k,math.inf):nxt[k]=nv
        dp=nxt
    return min(dp.values())

def main(seeds=3,instances_per_family=2,n=16,budget=1200):
    OUT.mkdir(exist_ok=True);probs=generate_suite(instances_per_family,n);rows=[]
    for pi,p in enumerate(probs,1):
        print(f'[{pi}/{len(probs)}] {p.name}',flush=True)
        for sd in range(seeds):
            seed=10007*sd+77
            for fn in ALGS:
                rr=fn(p,seed,budget);rows.append(rr)
    bks={p.name:min(r.score for r in rows if r.inst==p.name) for p in probs}
    detail=[]
    for r in rows:
        rpd=100*(r.score-bks[r.inst])/bks[r.inst];h5=hit_eval(r.trace,bks[r.inst]*1.05);h1=hit_eval(r.trace,bks[r.inst]*1.01);auc=auc_norm(r.trace,budget,bks[r.inst])
        detail.append(dict(algorithm=r.alg,instance=r.inst,family=r.family,seed=r.seed,score=r.score,rpd_pct=rpd,hit5=0 if h5 is None else 1,hit_eval_5='' if h5 is None else h5,hit1=0 if h1 is None else 1,hit_eval_1='' if h1 is None else h1,conv_auc_rpd=auc))
    with (OUT/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=detail[0].keys());w.writeheader();w.writerows(detail)
    algnames=sorted(set(r.alg for r in rows)); summary=[]
    for alg in algnames:
        sub=[x for x in detail if x['algorithm']==alg]; succ=[x for x in sub if x['hit5']]
        ert=sum((x['hit_eval_5'] if x['hit5'] else budget) for x in sub)/max(1,len(succ))
        summary.append(dict(algorithm=alg,runs=len(sub),median_rpd_pct=statistics.median(x['rpd_pct'] for x in sub),mean_rpd_pct=statistics.fmean(x['rpd_pct'] for x in sub),iqr_rpd_pct=(statistics.quantiles([x['rpd_pct'] for x in sub],n=4)[2]-statistics.quantiles([x['rpd_pct'] for x in sub],n=4)[0]),success_5pct_pct=100*len(succ)/len(sub),ert_eval_5pct=ert,median_conv_auc=statistics.median(x['conv_auc_rpd'] for x in sub)))
    ga=next(x for x in summary if x['algorithm']=='GA');
    for x in summary:x['eval_efficiency_vs_GA_x']=ga['ert_eval_5pct']/x['ert_eval_5pct'] if x['ert_eval_5pct']>0 else math.inf
    # mean paired rank per instance/seed (lower better)
    ranks={a:[] for a in algnames}
    for p in probs:
        for sd in [10007*s+77 for s in range(seeds)]:
            vals=[x for x in detail if x['instance']==p.name and x['seed']==sd];vals.sort(key=lambda x:x['score'])
            # ordinal rank; sufficient for compact study
            for rank,x in enumerate(vals,1):ranks[x['algorithm']].append(rank)
    for x in summary:x['mean_rank']=statistics.fmean(ranks[x['algorithm']])
    summary.sort(key=lambda x:x['mean_rank'])
    with (OUT/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=summary[0].keys());w.writeheader();w.writerows(summary)
    # per-family medians and ranks
    famrows=[]
    for fam in sorted(set(p.family for p in probs)):
        for alg in algnames:
            sub=[x for x in detail if x['family']==fam and x['algorithm']==alg];famrows.append(dict(family=fam,algorithm=alg,median_rpd_pct=statistics.median(x['rpd_pct'] for x in sub),success_5pct_pct=100*sum(x['hit5'] for x in sub)/len(sub),median_auc=statistics.median(x['conv_auc_rpd'] for x in sub)))
    with (OUT/'family_summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=famrows[0].keys());w.writeheader();w.writerows(famrows)
    # exact-verification mini suite (7 demands, one instance/family, 3 seeds)
    exrows=[]
    for fi,fam in enumerate(['uniform','clustered','price_distance_conflict','shared_hubs','deceptive_groups'],1):
        p=generate_problem(fam,90+fi,n=7);opt=exact_score(p)
        for fn in ALGS:
            gaps=[]
            for sd in range(3):
                rr=fn(p,900+sd,1600);gaps.append(100*(rr.score-opt)/opt)
            exrows.append(dict(family=fam,algorithm=fn(p,999,40).alg,median_exact_gap_pct=statistics.median(gaps)))
    with (OUT/'exact_small.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=exrows[0].keys());w.writeheader();w.writerows(exrows)
    # nonparametric Friedman over paired runs
    try:
        from scipy.stats import friedmanchisquare
        maps={a:[] for a in algnames}
        for p in probs:
            for sd in [10007*s+77 for s in range(seeds)]:
                for a in algnames:
                    maps[a].append(next(x['score'] for x in detail if x['instance']==p.name and x['seed']==sd and x['algorithm']==a))
        stat,pv=friedmanchisquare(*[maps[a] for a in algnames]);(OUT/'stats.json').write_text(json.dumps({'friedman_stat':float(stat),'friedman_p':float(pv),'paired_cases':len(next(iter(maps.values())))},indent=2))
    except Exception as e:(OUT/'stats.json').write_text(json.dumps({'error':str(e)}))
    # Focused paired tests for the redesigned FOX method.
    try:
        from scipy.stats import wilcoxon
        pairs=[]
        anchor='DFOX-APNS'
        a=sorted([x for x in detail if x['algorithm']==anchor], key=lambda x:(x['instance'],x['seed']))
        for other in ['DFOX-Base','GA','GA+Tabu','DWOA-AVNS']:
            b=sorted([x for x in detail if x['algorithm']==other], key=lambda x:(x['instance'],x['seed']))
            av=[x['score'] for x in a]; bv=[x['score'] for x in b]
            stat,pv=wilcoxon(av,bv,alternative='two-sided')
            paired_improvement=statistics.median(100*(y-x)/y for x,y in zip(av,bv))
            pairs.append(dict(method_a=anchor,method_b=other,wilcoxon_stat=float(stat),p_value=float(pv),median_paired_cost_improvement_pct=paired_improvement))
        with (OUT/'paired_wilcoxon.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=pairs[0].keys());w.writeheader();w.writerows(pairs)
    except Exception as e:
        (OUT/'paired_wilcoxon_error.txt').write_text(str(e),encoding='utf-8')
    print('DONE',OUT)

if __name__=='__main__':main()
