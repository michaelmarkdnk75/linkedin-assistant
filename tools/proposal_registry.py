#!/usr/bin/env python3
"""Shared pending-proposal registry (outreach_rules.md section 51).
File: plans/pending_proposals.json  {"items":[{id,person_key,person,channel,target,text_hash,status,created,answered,note}]}
channel: comment|message|inmail|invite|follow|cv ; target: post urn or conversation (comment = per post).
status: open|approved|sent|rejected|cancelled
Usage:
  check <person_key> <channel> [target]   exit 0 = free to propose, exit 1 = blocked (prints blocking items)
  add <id> <person_key> "<Person>" <channel> [target]   (runs check first; refuses on conflict)
  set <id> <status> [note]                 (approved/sent/rejected/cancelled)
  is_cancelled <id>                        exit 0 = cancelled/superseded: a later JA/RET for this id must NOT be sent
  open                                     list open+approved-not-sent
person_key = lowercase linkedin slug or ln_id; fall back to lowercase full name."""
import json,sys,os,datetime
F=os.path.join(os.path.dirname(__file__),'..','plans','pending_proposals.json')
def load():
    return json.load(open(F)) if os.path.exists(F) else {"items":[]}
def save(d): json.dump(d,open(F,'w'),ensure_ascii=False,indent=1)
LIVE=('open','approved')
def blocking(d,pk,ch,tg=None):
    return [i for i in d['items'] if i['person_key']==pk and i['status'] in LIVE and i['channel']==ch and (tg is None or i.get('target') in (None,tg))]
def main(a):
    d=load();c=a[0]
    if c=='check':
        b=blocking(d,a[1],a[2],a[3] if len(a)>3 else None)
        for i in b: print('BLOCKED by',i['id'],i['status'],i['person'])
        return 1 if b else 0
    if c=='add':
        i,pk,p,ch=a[1:5];tg=a[5] if len(a)>5 else None
        if blocking(d,pk,ch,tg): print('REFUSED: open item exists for',p,ch);return 1
        d['items'].append(dict(id=i,person_key=pk,person=p,channel=ch,target=tg,status='open',created=datetime.datetime.utcnow().isoformat()+'Z'));save(d);return 0
    if c=='set':
        for i in d['items']:
            if i['id']==a[1]:
                i['status']=a[2];i['answered']=datetime.datetime.utcnow().isoformat()+'Z'
                if len(a)>3:i['note']=a[3]
                if a[2] in ('approved','sent'):  # first answer wins: cancel other live items for same person+channel+target
                    for o in d['items']:
                        if o is not i and o['person_key']==i['person_key'] and o['channel']==i['channel'] and o.get('target')==i.get('target') and o['status']=='open':
                            o['status']='cancelled';o['note']='superseded by '+i['id']+' (first answer wins)'
        save(d);return 0
    if c=='is_cancelled':
        return 0 if any(i['id']==a[1] and i['status']=='cancelled' for i in d['items']) else 1
    if c=='open':
        for i in d['items']:
            if i['status'] in LIVE: print(i['id'],i['person'],i['channel'],i['status'])
        return 0
sys.exit(main(sys.argv[1:]))
