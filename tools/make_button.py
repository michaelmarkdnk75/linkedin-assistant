#!/usr/bin/env python3
"""Approval buttons WITHOUT Make (Michael 20/11-2026 'helt uden make'; outreach_rules.md section 52).
Ja/Nej = one-tap link to the Google Apps Script web app (logs a row in Sheet personligtklik, tab klik: tid,afst,fra,v,a,id,tekst,status,dato).
Ret = mailto with the full draft text prefilled (the only way to edit text without a form).
Function names kept for old callers: jn_button(label,color,v,id), ret_button(id,text,label), button(...). Make hooks are NOT used any more."""
import sys, urllib.parse as u
APPS="https://script.google.com/macros/s/AKfycbxWXJs0qyBTyBhHeTfhgKhBSzJ_V5t723MQgc9juzZvAo8LzZlf6pcodY0CYehXHIxw/exec"
FRA="michaelmarkdnk@gmail.com"
COL={"green":"#0a7d3b","grey":"#666666","red":"#cf222e"}
def _td(url,label,color):
    c=COL[color]
    return (f'<table cellpadding=0 cellspacing=0 border=0 style="display:inline-table;margin:4px 6px 4px 0"><tr><td bgcolor="{c}" style="background-color:{c};border-radius:6px">'
            f'<a href="{url}" style="display:block;padding:10px 16px;color:#ffffff;font-weight:bold;text-decoration:none">{label}</a></td></tr></table>')
def klik_url(v,i,tekst=""):
    q={"afst":"li-svar","fra":FRA,"v":v,"id":i}
    if tekst: q["tekst"]=tekst
    return APPS+"?"+u.urlencode(q,quote_via=u.quote).replace("&","&amp;")
def jn_button(label,color,v,i,tekst=""):
    """v: 'JA' or 'NEJ' (stored lower-case in sheet). One tap."""
    return _td(klik_url(v.lower(),i,tekst),label,color)
button=lambda label,color,v,i,tekst="": jn_button(label,color,v,i,tekst)
def ret_button(i,text,label="Ret"):
    """mailto, subject 'LI RET <id>', body = draft text (never empty)."""
    t=text[len('Ny tekst: '):] if text.startswith('Ny tekst: ') else text
    url=f"mailto:{FRA}?"+u.urlencode({"subject":f"LI RET {i}","body":t},quote_via=u.quote).replace("&","&amp;")
    return _td(url,label,"grey")
def triple(i,text,name=""):
    return jn_button("Ja","green","JA",i,name)+jn_button("Nej","red","NEJ",i,name)+ret_button(i,text)
if __name__=="__main__": print(triple(sys.argv[1],sys.argv[2]))
