from pathlib import Path, PurePosixPath
import hashlib,json,zipfile
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=Path('release-manifest.json').read_bytes()
assert sha(raw)=='72729517cd641e173bef01a19292be030d69d81fc0b0310a63cbc98282d3e584','Release manifest hash mismatch'
m=json.loads(raw);b=Path('site-runtime.zip').read_bytes()
assert len(b)==m['archiveBytes'] and sha(b)==m['archiveSHA256']=='878f82f901418af93745352ef665e2cb001fc68a430363fc8e81413aa9f8bf1d','Static runtime archive mismatch'
assert not Path('site').exists(),'Refuse to merge with an existing build'
assert sum(x['bytes'] for x in m['files'].values())+len(m['files'])*2048+8*1024*1024<1000000000
with zipfile.ZipFile('site-runtime.zip') as z:
 assert z.testzip() is None and len(z.infolist())==len(m['files'])==297 and set(z.namelist())==set(m['files'])
 for e in z.infolist():
  p=PurePosixPath(e.filename)
  assert not p.is_absolute() and '..' not in p.parts and '\\' not in e.filename
  assert (e.external_attr>>16)&0o170000==0o100000,'Only regular files are allowed'
  assert p.suffix.lower() not in {'.mp3','.mp4','.flac','.wav','.ogg','.webm','.pdf','.map'}
  d=z.read(e);assert len(d)==m['files'][e.filename]['bytes'] and sha(d)==m['files'][e.filename]['sha256']
 for e in z.infolist():
  p=Path('site')/e.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(e))

"""Verify the exact static review files before deployment."""
from pathlib import Path, PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib,json,re,sys

root=Path('site')
manifest=json.loads(Path('release-manifest.json').read_text())
expected=manifest['files']
actual={}
for p in root.rglob('*'):
    assert not p.is_symlink(),f'Symbolic link is not permitted: {p}'
    if p.is_file():
        name=p.relative_to(root).as_posix()
        assert not any(q.startswith('.') and q!='.nojekyll' for q in PurePosixPath(name).parts),name
        b=p.read_bytes();actual[name]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
        assert p.suffix.lower() not in {'.mp3','.mp4','.wav','.flac','.ogg','.webm','.pdf','.map'},name
assert actual==expected,'The static tree differs from the recorded release.'
assert 'index.html' in actual and '.nojekyll' in actual
assert sum(v['bytes']for v in actual.values())+len(actual)*2048+8*1024*1024<1000000000,'Published size limit exceeded.'

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        for name in ['href','src','poster']:
            if name in a:self.links.append((tag,name,a[name]))

checked=0
for p in root.rglob('*.html'):
    text=p.read_text();parser=Links();parser.feed(text)
    assert not re.search(r'<base\b',text,re.I),str(p)
    assert 'public-review-paths.js' in text,str(p)
    for tag,attr,value in parser.links:
        if not value or value.startswith('#'):continue
        u=urlsplit(value)
        if u.scheme or u.netloc:
            assert tag=='a' and attr=='href' and u.scheme in {'https','http','mailto','tel'},(p,value)
            continue
        assert not value.startswith('/'),(p,'Origin-root URL would escape the project',value)
        target=(p.parent/unquote(u.path)).resolve()
        assert target==root.resolve()or root.resolve()in target.parents,(p,value)
        if target.is_dir():target=target/'index.html'
        assert target.is_file(),(p,'Missing local dependency',value)
        checked+=1
print(json.dumps({'status':'PASS','files':len(actual),'localHtmlLinks':checked,'staticBytes':sum(v['bytes']for v in actual.values()),'clinicalAcceptance':False,'browserAcceptance':False,'integratedNarration':False}))
