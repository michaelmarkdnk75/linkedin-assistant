import json,html,sys
sys.path.insert(0,'/mnt/project-files/linkedin-stats/tools')
import make_button as mb, urllib.parse as u
def _c(url,label,c): return f'<a href="{url}" style="border:2px solid {c};color:{c};padding:6px 12px;margin:4px 5px 4px 0;border-radius:6px;font-weight:bold;text-decoration:none;display:inline-block">{label}</a>'
def _t(*x): return ''.join(x)
def jn_button(label,color,v,i,tekst=""): return _c(mb.klik_url(v.lower(),i,tekst),label,mb.COL[color])
def triple(i,text,name=""):
    ret=f"mailto:{mb.FRA}?"+u.urlencode({"subject":f"LI RET {i}","body":text},quote_via=u.quote).replace("&","&amp;")
    return _c(mb.klik_url('ja',i),'Ja',mb.COL['green'])+_c(mb.klik_url('nej',i),'Nej',mb.COL['red'])+_c(ret,'Ret',mb.COL['grey'])
D='/mnt/project-files/linkedin-stats/drafts/'
def load(f):
    d=json.load(open(D+f)); return d if isinstance(d,list) else d['items']
def by(f): return {x['id']:x for x in load(f)}
cv23=by('cvflow_2026-11-23_0913.json'); fq22=by('fill_quota_2026-11-22.json'); fq23=by('fill_quota_2026-11-23.json')
c23=by('comments_2026-11-23.json'); fw=load('follows_2026-11-23.json')
e=html.escape
def nl(t): return e(t).replace('\n','<br>')
def box(i,name,lines,text,retText=None):
    h=f'<div style="border:1px solid #ccc;border-radius:6px;padding:10px;margin:10px 0"><b>{e(i)} {e(name)}</b>'
    for l in lines: h+=f'<div style="font-size:13px;color:#444;margin-top:3px">{e(l)}</div>'
    h+=f'<p style="border-left:3px solid #999;padding:6px 10px;margin:8px 0;background:#f6f6f6">{nl(text)}</p>'
    return h+triple(i,retText or text,name)+'</div>'
def jaall(a,b,label): return jn_button(label,'green','JA',f'{a}-{b}')
parts=[];ids=[]
def sec(t,sub=''): parts.append(f'<h3 style="margin:22px 0 4px;border-bottom:2px solid #0a7d3b">{e(t)}</h3><div style="font-size:13px;color:#555">{e(sub)}</div>')
# posts
sec('1. Nyt opslag (KJ-AI-system, billede følger med ved Ja)','Hvorfor: opslaget fra 22/11 har 0 kommentarer og lavt reach. Kun tal fra casen. Vælg ét; tid sættes ved Ja (max ét opslag pr. dag).')
PO={'PO2311A':('Option A: skills som jobbeskrivelse',"En ny kollega får en jobbeskrivelse. Det fik min AI også.\n\nI Køge Jernmand har jeg skrevet fem skills til systemet: planlægning og status, to til opslag, deltagerguiden og mailstil. Dertil 16 scripts. Det tog omkring 60 timer over seks uger, og jeg godkender stadig alt selv.\n\nHos jer: hvem skriver jobbeskrivelsen til jeres AI-agent?\n\n#AI #Projektledelse #Frivilligledelse"),
'PO2311B':('Option B: ugens flow',"En stafet vinder ikke på hurtige ben alene, men på at pinden bliver afleveret rigtigt.\n\nI Køge Jernmand er ugen sat i fast flow: fredag giver systemet overblik pr. område, sporlederne svarer og opdaterer, mandag går ugerapporten til udvalget, og jeg beslutter med ét klik. AI'en holder rytmen, mennesker tager beslutningen.\n\nHos jer: hvem holder rytmen i en travl uge?\n\n#AI #Projektledelse #Frivilligledelse"),
'PO2311C':('Option C: dig med AI-systemet',"Speakeren på målstregen løber ikke selv, men sørger for, at alle ved, hvad der sker.\n\nSådan bruger jeg AI i Køge Jernmand. Systemet holder planen, rykker og svarer, så sporlederne kan nøjes med at udføre. Mit job er at godkende, ikke at jagte.\n\nHos jer: hvad ville I helst slippe for at jagte?\n\n#AI #Projektledelse #Frivilligledelse")}
for i,(n,t) in PO.items():
    parts.append(box(i,n,[],t)); ids.append(i)
# comments
sec('2. Kommentarer (like sendes først)')
for i in('C23-1','C23-2'):
    x=c23[i]; parts.append(box(i,x['name'],['Hvorfor: '+x['hv']+'. Grundlag: '+x['summary']+' '+x['rel']+'. '+x['dia']+'.'],x['draft'])); ids.append(i)
x=fq23['QC23-1']; parts.append(box('QC23-1',x['name'],['Hvorfor: prioritet 1 headhunter, ny forbindelse (19/11), opslag i dag om IT-lederrolle. Grundlag: '+x['title']+'. '+x['summary']+' '+x['dialog']],x['text'])); ids.append('QC23-1')
# messages
sec('3. Beskeder','CV23-2 sender CV. Ja = CV sendes (outreach_rules.md §61).')
for i in('CV23-2','V23-1','V23-2'):
    x=cv23[i]; parts.append(box(i,x['name'],['Hvorfor: '+x['why'],'Grundlag: '+x['head']+'. '+x['grund']+' '+x['dlg']],x['text'])); ids.append(i)
# invites
sec('4. Invitationer (backups, 2 dage gamle, live forbindelsestjek før afsendelse)')
parts.append(jaall('IN22-6','QI22-5','Ja til alle 8 invites'))
lst=[]
for i in('IN22-6','IN22-7','IN22-8'):
    x=fq22[i]; lst.append(f"{i} {x['name']}: {x['intro'].split('. ')[0]}")
for i in('QI22-1','QI22-2','QI22-3','QI22-4','QI22-5'):
    x=fq22[i]; lst.append(f"{i} {x['name']}: {x['title']}")
parts.append('<p style="font-size:13px;line-height:1.5">'+'<br>'.join(e(l) for l in lst)+'</p><p style="font-size:12px;color:#555">Tekst: standardnote (IT er til for forretningen, head of/direktør i IT, 75+ medarbejdere globalt). Ingen kontakt tjekket 22/11. Ret: svar på mailen med ønsket tekst.</p>')
parts.append(jn_button('Nej til alle 8 invites','red','NEJ','IN22-6-QI22-5'))
sec('5. InMail (kræver credit)')
x=fq22['QN22-1']; parts.append(box('QN22-1',x['name'],[x['grp']+': '+x['title'],'Emne: '+x['subject']],x['text'])); ids.append('QN22-1')
# follows
sec('6. Follows (Ja/Nej, 30 stk)','Ja til alle følger hele listen, Nej til alle springer den over. Skal enkelte fravælges, så sig det i et svar.')
fids=[x['id'] for x in fw]
parts.append(jaall(fids[0],fids[-1],'Ja til alle 30 follows'))
parts.append(jn_button('Nej til alle 30','red','NEJ',f'{fids[0]}-{fids[-1]}'))
parts.append('<p style="font-size:12px;color:#444;line-height:1.5">'+'; '.join(f"{x['id']} {x['name']} ({x['title'].split(',')[-1].strip()})" for x in fw)+'</p>')
head='<div style="font-family:Arial,sans-serif;max-width:640px;font-size:14px"><h2 style="margin:0">Alt der venter på dit svar, 24/11</h2><p>Samlet fra Gmail, Gmail-label og klik-arket kl. 08:00. Allerede besvaret (Ja/Nej i går og i dag) er udeladt. Ja/Nej er ét tryk, Ret åbner en mail med teksten udfyldt, og Ret er ikke en godkendelse før du sender den nye tekst.</p>'
html_=head+''.join(parts)+'<p style="font-size:12px;color:#777">Udeladt som besvaret: QM23-12..28b, QI23-1..22b, QW23-1..10b, END1-5, CV24-1/2, OC2311B.</p></div>'
open(D+'email_samlet_svar_2026-11-24.html','w').write(html_)
open('/tmp/claude-0/s/ids.txt','w').write(' '.join(ids))
print(len(html_),len(ids))
