"""Build and validate the exact public review tree; no network or package dependencies."""
from pathlib import Path,PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,zipfile
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=Path('release-manifest.json').read_bytes()
assert sha(raw)=='f7e268126fa5e32cd54b7b9424c7992e2dfeac2f44b4a400d40517a0880abd19','Manifest hash mismatch'
m=json.loads(raw);root=Path('site')
assert not root.exists(),'Refuse to merge with an existing build'
assert m['recordings']==635 and m['coveredExerciseRoutes']==29
assert not any(m[k]for k in ['clinicalAcceptance','listeningAcceptance','browserAcceptance'])
expected=m['files'];seen={};archives=[]
for archive in m['archives']:
 p=Path(archive['path']);b=p.read_bytes()
 assert len(b)==archive['bytes']and sha(b)==archive['sha256'],p
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None and len(z.infolist())==len(archive['files']) and set(z.namelist())==set(archive['files']),p
  for e in z.infolist():
   q=PurePosixPath(e.filename)
   assert not q.is_absolute()and '..'not in q.parts and '\\'not in e.filename,e.filename
   assert not any(v.startswith('.')and v!='.nojekyll'for v in q.parts),e.filename
   assert(e.external_attr>>16)&0o170000==0o100000,e.filename
   assert e.filename not in seen and e.filename in expected,e.filename
   d=z.read(e);assert {'sha256':sha(d),'bytes':len(d)}==expected[e.filename],e.filename
   if q.suffix=='.flac':assert q.parts[:3]==('assets','narration','audio')and d.startswith(b'fLaC'),e.filename
   else:assert q.suffix.lower()not in {'.mp3','.mp4','.wav','.ogg','.webm','.pdf','.map'},e.filename
   seen[e.filename]=expected[e.filename]
 archives.append(p)
assert seen==expected,'Archive tree does not match manifest'
assert sum(v['bytes']for v in seen.values())+len(seen)*2048+8*1024*1024<1000000000,'Pages size limit exceeded'
# Verification is complete before writing any output.
for p in archives:
 with zipfile.ZipFile(p)as z:
  for e in z.infolist():
   dst=root/e.filename;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read(e))
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for attr in ['href','src','poster']:
   if attr in a:self.links.append((tag,attr,a[attr]))
count=0
for p in root.rglob('*.html'):
 text=p.read_text();parser=Links();parser.feed(text)
 assert '<base 'not in text.lower()and 'public-review-paths.js'in text,p
 for tag,attr,value in parser.links:
  if not value or value.startswith('#'):continue
  u=urlsplit(value)
  if u.scheme or u.netloc:
   assert tag=='a'and attr=='href'and u.scheme in {'http','https','mailto','tel'},(p,value)
   continue
  assert not value.startswith('/'),(p,value)
  dest=(p.parent/unquote(u.path)).resolve()
  assert dest==root.resolve()or root.resolve()in dest.parents,(p,value)
  if dest.is_dir():dest=dest/'index.html'
  assert dest.is_file(),(p,value)
  count+=1
print(json.dumps({'status':'PASS','files':len(seen),'localHtmlLinks':count,'staticBytes':sum(v['bytes']for v in seen.values()),'recordings':635,'coveredExerciseRoutes':29,'integratedNarration':True,'clinicalAcceptance':False,'listeningAcceptance':False,'browserAcceptance':False}))
