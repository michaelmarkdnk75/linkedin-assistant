#!/usr/bin/env python3
"""Quota tracker. Usage: quota_tracker.py <limits.json> [--final]
limits.json = saved search_linkedin_account_smart_limits response (live).
Prints used/cap/gap per bucket + drafts still pending per type, appends quota/quota_log.csv,
and with --final writes the day score to quota/score.csv. Exit 0 = all full, 1 = gap."""
import json,sys,glob,csv,os,datetime
B='/mnt/project-files/linkedin-stats/'
BUCK={'send_connection_requests':('invite',20),'send_messages':('message',25),'send_inmails':('inmail',24),
 'comment_posts':('comment',24),'networking_general':('follow',25),'react_posts':('like',24),
 'endorse_skills':('endorse',24),'visit_profiles':('visit',40)}
TYPEMAP={'invite':'invite','liker_invite':'invite','message':'message','dm':'message','cv':'message','inmail':'inmail',
 'comment':'comment','reply':'comment','follow':'follow','like':'like','react':'like','endorse':'endorse','visit':'visit'}
lim=json.load(open(sys.argv[1])); final='--final' in sys.argv
rows={}
for it in lim.get('items',[]):
    i=it['item']
    if i['limit_type'] in BUCK:
        # live daily_limit wins, but never above Michael's cap
        rows[i['limit_type']]=(i['done_today_count'],i['daily_limit'])  # live limit wins (Michael raised 19/11)
now=datetime.datetime.utcnow(); today=(now+datetime.timedelta(hours=1)).strftime('%Y-%m-%d')
pend={}
for f in glob.glob(B+'drafts/*%s*.json'%today)+glob.glob(B+'replies/drafts_%s.json'%today):
    try: d=json.load(open(f))
    except Exception: continue
    items=d if isinstance(d,list) else d.get('items',d.get('drafts',[]))
    for x in items if isinstance(items,list) else []:
        if not isinstance(x,dict): continue
        st=str(x.get('status','')).lower(); t=TYPEMAP.get(str(x.get('type','')).lower())
        if t and (st.startswith('proposed') or st.startswith('approved')) and 'blocked' not in st or (t and st.startswith('approved - blocked')):
            k='approved' if st.startswith('approved') else 'proposed'
            pend.setdefault(t,{'approved':0,'proposed':0})[k]+=1
print('bucket                     used/cap  gap  approved-unsent  proposed(open)  NEED-TO-DRAFT(+25%% backup)')
tot_u=tot_c=0; out=[]
for b,(u,c) in rows.items():
    t=BUCK[b][0]; p=pend.get(t,{'approved':0,'proposed':0}); gap=max(0,c-u)
    need=max(0,gap-p['approved']-p['proposed']); need=need+(need+3)//4 if need else 0
    print('%-26s %3d/%-3d  %3d  %8d  %14d  %8d'%(b,u,c,gap,p['approved'],p['proposed'],need))
    tot_u+=min(u,c); tot_c+=c; out.append((b,u,c))
score=round(100*tot_u/max(1,tot_c)); print('SCORE %d%% (%d/%d) %s UTC'%(score,tot_u,tot_c,now.strftime('%H:%M')))
os.makedirs(B+'quota',exist_ok=True)
with open(B+'quota/quota_log.csv','a',newline='') as fh:
    w=csv.writer(fh)
    for b,u,c in out: w.writerow([today,now.strftime('%H:%M'),b,u,c])
if final:
    new=not os.path.exists(B+'quota/score.csv')
    with open(B+'quota/score.csv','a',newline='') as fh:
        w=csv.writer(fh)
        if new: w.writerow(['date','score_pct','used','cap']+[o[0] for o in out])
        w.writerow([today,score,tot_u,tot_c]+['%d/%d'%(o[1],o[2]) for o in out])
sys.exit(0 if all(u>=c for _,u,c in out) else 1)
