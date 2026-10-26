import re,json,html as H,shutil
from videos import V,BLOGS
e=H.escape
slug=lambda i,v:"%02d-%s.html"%(i+1,re.sub(r'[^a-z0-9]+','-',v['s'].lower()).strip('-'))
files=[slug(i,v) for i,v in enumerate(V)]
T=open('_template/topic.html',encoding='utf-8').read()
head=T[:T.find('</head>')+7]
scripts=[m.group(0) for m in re.finditer(r'<script>.*?</script>',T,flags=re.S)]
nav=json.dumps([dict(num="%02d"%(i+1),title=v['s'],href=files[i]) for i,v in enumerate(V)])
keep=[scripts[0].replace(re.search(r'__NAV_TOPICS__ = .*?;\n',scripts[0],re.S).group(0),'__NAV_TOPICS__ = %s;\n'%nav)]+[s for k,s in enumerate(scripts) if k in(1,2,4,5,6)]
tail_btn=T[T.find('<button type="button" class="to-top"'):T.find('</button>',T.find('class="to-top"'))+9]
EYE="Kaye's AI Video Tutorials — Video-by-Video Guide"
def page(i,v):
    f=files[i];yt=v.get('link') or "https://www.youtube.com/watch?v="+v['id'];bl=v['blog'] or BLOGS
    h=re.sub(r'<title>.*?</title>','<title>%02d — %s</title>'%(i+1,e(v['s'])),head)
    pv=('<a class="path-btn prev" href="%s"><span class="p-arrow">←</span><span class="p-text"><span class="p-kicker">Previous</span><span class="p-title">%02d. %s</span></span></a>'%(files[i-1],i,e(V[i-1]['s']))) if i else '<span class="path-spacer"></span>'
    nx=('<a class="path-btn next" href="%s"><span class="p-text"><span class="p-kicker">Next</span><span class="p-title">%02d. %s</span></span><span class="p-arrow">→</span></a>'%(files[i+1],i+2,e(V[i+1]['s']))) if i<len(V)-1 else '<span class="path-spacer"></span>'
    idx='<a class="path-btn index" href="index.html"><span class="p-text"><span class="p-kicker">All Videos</span><span class="p-title">🏠 Main Index</span></span></a>'
    nv=pv+idx+nx
    secs=[("overview","Overview"),("workflow","Workflow"),("fixes","Mistakes and fixes"),("prompts","Prompts and blog"),("takeaways","Key takeaways")]
    if not v['fix']:secs.remove(("fixes","Mistakes and fixes"))
    toc=''.join('<a href="#%s">%d. %s</a>'%(a,n+1,b) for n,(a,b) in enumerate(secs))
    cols=['var(--blue)','var(--green)','var(--red)','var(--yellow)','var(--purple)']
    def sec(n,key,title,body):
        return '<section class="section" id="%s"><div class="kicker"><div class="kicker-left"><div class="num-badge" style="background:%s">%d</div><h2>%s</h2></div></div>%s</section>'%(key,cols[n%5],n+1,title,body)
    S={}
    S['overview']='<p class="lede">%s</p><div class="chip-row">%s</div><div class="callout tip"><b>Sources:</b> <a href="%s" target="_blank" rel="noopener">▶ Source</a> · <a href="%s" target="_blank" rel="noopener">📝 Blog post with prompts and images ↗</a></div>'%(e(v['l']),''.join('<span class="chip">%s</span>'%e(x) for x in v['tools']),yt,bl)
    S['workflow']='<div class="slide"><div class="slide-title">Step by step</div><ol>%s</ol></div>'%''.join('<li>%s</li>'%e(x) for x in v['steps'])
    S['fixes']='<div class="table-wrap"><table class="vtable"><thead><tr><th>Problem</th><th>Fix</th></tr></thead><tbody>%s</tbody></table></div>'%''.join('<tr><td class="term">%s</td><td>%s</td></tr>'%(e(a),e(b)) for a,b in v['fix'])
    S['prompts']='<div class="callout warn"><b>Prompts:</b> %s Open the blog above for the full prompts and images. Paste the post URL into <code>videos.py</code> (field <code>blog</code>) and rebuild to link it directly.</div>'%('Linked blog post:' if v['blog'] else 'Post link not added yet.')
    S['takeaways']='<ul class="exam-list">%s</ul>'%''.join('<li><span class="chk"></span><span>%s</span></li>'%e(x) for x in v['take'])
    if v.get('custom'):
        secs=[(a,b) for a,b,_ in v['custom']];S={a:h for a,b,h in v['custom']};toc=''.join('<a href="#%s">%d. %s</a>'%(a,n+1,b) for n,(a,b) in enumerate(secs))
    main=''.join(sec(n,a,b,S[a]) for n,(a,b) in enumerate(secs))
    body='''<body>
<div class="mobile-bar" id="mobileBar"><span class="m-title">%02d. %s</span><button type="button" class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="toc" aria-label="Open section menu"><span></span></button></div>
<div class="toc-backdrop" id="tocBackdrop"></div>
<div class="hero"><div class="hero-inner"><span class="eyebrow">%s</span><h1>%02d. %s</h1><p class="lead">%s</p>
<div class="hero-meta"><span><span class="dot"></span>%s</span><span><span class="dot"></span>%d sections</span></div>
<div class="hero-search-row"><div class="site-search" id="siteSearch"><span class="s-icon">🔍</span><input type="text" id="topicJump" placeholder="Jump to a video…" autocomplete="off"><button type="button" class="s-clear" id="jumpClear" aria-label="Clear search">✕</button><div class="s-dropdown" id="jumpDropdown"></div></div>
<div class="hero-find-col"><div class="site-search find-page-search" id="heroFindWrap"><span class="s-icon">📍</span><input type="text" id="heroFindInput" placeholder="Find on this page…" autocomplete="off"><button type="button" class="s-clear" id="heroFindClear" aria-label="Clear search">✕</button></div>
<div class="find-page-nav" id="heroFindNav"><span id="heroSearchCount">0 / 0</span><div class="snav-btns"><button type="button" id="heroSearchPrev" aria-label="Previous match">↑</button><button type="button" id="heroSearchNext" aria-label="Next match">↓</button></div></div></div></div></div>
<div class="path-nav">%s</div></div>
<div class="layout"><nav class="toc" id="toc"><div class="toc-head">On this page <button type="button" class="drawer-close" id="drawerClose" aria-label="Close menu">✕</button></div>
<div class="toc-search"><div class="toc-search-box"><span class="s-icon">🔍</span><input type="text" id="pageSearchInput" placeholder="Find on this page…" autocomplete="off"><button type="button" class="s-clear" id="pageSearchClear" aria-label="Clear search">✕</button></div><div class="toc-search-nav" id="searchNav"><span id="searchCount">0 / 0</span><div class="snav-btns"><button type="button" id="searchPrev" aria-label="Previous match">↑</button><button type="button" id="searchNext" aria-label="Next match">↓</button></div></div></div>
%s</nav><main>%s<footer>%s<br><a class="back-top" href="#top">Back to top ↑</a></footer></main></div>
<div class="bottom-nav">%s</div>
%s%s</body></html>'''%(i+1,e(v['s']),EYE,i+1,e(v['s']),e(v['t']),v['d']+', 2026',len(secs),nv,toc,main,EYE,nv,'\n'.join(keep),tail_btn)
    # scripts must come after buttons: tail_btn placed before last script originally; fine
    open(f,'w',encoding='utf-8').write(h+body)
for i,v in enumerate(V):page(i,v)
# index
X=open('_template/index.html',encoding='utf-8').read()
groups=[("🎬 Foundations",range(0,5),"Prompting, assets and drafts"),("🎨 Creative craft",range(5,7),"Mindset and live-action"),("📺 Commercials",range(7,10),"Brand-style ads"),("💰 Realism and cost",range(10,12),"Keyframes, Soul ID, drafts"),("📈 Growth study",range(12,15),"Her Instagram journey, your plan, briefs and pricing"),("📚 Playbook",range(15,16),"Rules, models, fixes and templates")]
cols=['#4285F4','#34A853','#EA4335','#FBBC04','#A142F4','#FF6D01']
g='';t=''
for n,(name,rg,sub) in enumerate(groups):
    cards=''.join('<div class="module-card"><div class="module-head"><h3><a class="module-title-link" href="%s">%02d. %s</a></h3><a class="descriptor-link" href="%s" target="_blank" rel="noopener">Source ↗</a></div><a class="has-notes-tag" href="%s">📘 Read guide →</a><div class="assess-label">%s, 2026</div><ul class="assess-list">%s</ul></div>'%(files[i],i+1,e(V[i]['s']),(V[i].get('link') or 'https://www.youtube.com/watch?v='+V[i]['id']),files[i],V[i]['d'],''.join('<li>%s</li>'%e(x) for x in V[i]['tools'][:3])) for i in rg)
    g+='<div class="group" id="group-%d"><div class="group-head"><div class="num-badge" style="background:%s">%d</div><h2>%s</h2><span class="g-range">%d videos</span><span class="g-sub">%s</span></div><div class="module-grid">%s</div></div>'%(n+1,cols[n],n+1,name,len(rg),sub,cards)
    t+='<a href="#group-%d">%d. %s</a>'%(n+1,n+1,name)
a=X.find('<div class="hero">');f=X.find('<footer>');b=X.find('<script>')
top=X[a:X.find('<div class="idx-layout">')]
top=re.sub(r'<h1>.*?</h1>','<h1>AI Video Guide — Main Index</h1>',top,flags=re.S)
top=re.sub(r'<span class="eyebrow">.*?</span>','<span class="eyebrow">%s</span>'%EYE,top)
top=re.sub(r'(</h1>\s*<p>).*?(</p>)',r'\1One page per video from the @Kaye.creates channel: workflow, models, fixes and a link to the blog post with full prompts. Add a video in videos.py and rebuild.\2',top,flags=re.S)
top=re.sub(r'placeholder="[^"]*"','placeholder="Search videos… e.g. Seedance, credits, Blender"',top)
top=top.replace('Study Notes — Main Index','AI Video Guide')
lay='<div class="idx-layout"><nav class="toc" id="toc"><div class="toc-head">On this page <button type="button" class="drawer-close" id="drawerClose" aria-label="Close menu">✕</button></div>'+t+'</nav><main><div class="wrap-idx" style="padding-bottom:60px;"><div class="no-results" id="noResults"><div class="nr-title">No videos match your search</div><div>Clear the search to see all %d videos.</div></div>'%len(V)+g+'</div></main></div>\n'
foot='<footer>%s<br>%d videos<br><a class="back-top" href="#top">Back to top ↑</a></footer>\n'%(EYE,len(V))
out=re.sub(r'<title>.*?</title>','<title>AI Video Guide — Main Index</title>',X[:a],flags=re.S)+top+lay+foot+X[b:]
open('index.html','w',encoding='utf-8').write(out)
