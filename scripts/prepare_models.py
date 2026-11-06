"""Fetch pinned Unsloth files and generate pack/MTP; no pre-existing installation."""
import argparse, hashlib, json, os, shutil, subprocess, sys, tarfile, time
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler,ProxyHandler
from urllib.parse import quote,urlsplit,urlunsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import strata_local as deploy
REV='d96201194f103c906994f283f504209dc8d2a10c'
MODEL_REPO='unsloth/Qwen3.8-Flash-Next-GGUF'
CONNECT_TIMEOUT=25
PROXY=None
LAST_HOST=''
def safe_url(url):
 u=urlsplit(url);host=u.hostname or '';host=('['+host+']') if ':' in host else host;netloc=host+(':'+str(u.port) if u.port else '');return urlunsplit((u.scheme,netloc,u.path,'',''))
class NetworkRedirects(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  global LAST_HOST
  LAST_HOST=urlsplit(newurl).hostname or ''
  print('Redirect -> '+LAST_HOST,flush=True)
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def open_url(req,timeout=None):
 global LAST_HOST
 LAST_HOST=urlsplit(req.full_url).hostname or ''
 handlers=[NetworkRedirects()]
 if PROXY:handlers.append(ProxyHandler({'http':PROXY,'https':PROXY}))
 return build_opener(*handlers).open(req,timeout=CONNECT_TIMEOUT)
def network_error(exc):
 if getattr(exc,'code',None):return 'HTTP '+str(exc.code)
 reason=getattr(exc,'reason',exc)
 return type(reason).__name__+' (code '+str(getattr(reason,'winerror',None) or getattr(reason,'errno',None) or 'unknown')+')'

def model_url(host,group,name):return host.rstrip('/')+'/models/'+MODEL_REPO+'/resolve/master/'+('UD-IQ3_XXS/' if group=='models' else '')+quote(name)
def fetch(url,target,size,sha):
 target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():
  if target.stat().st_size==size and deploy.digest(target)==sha:print('Verified: '+target.name,flush=True);return
  raise ValueError('Existing file has wrong size/hash; review or rename it: '+str(target))
 print('File: '+target.name,flush=True)
 print('Source: '+safe_url(url),flush=True)
 part=target.with_name(target.name+'.part')
 for attempt in range(3):
  print('Connecting (attempt '+str(attempt+1)+'/3, timeout '+str(CONNECT_TIMEOUT)+'s)...',flush=True)
  offset=part.stat().st_size if part.exists() else 0
  if offset>size:raise ValueError('Oversized partial download: '+str(part))
  if offset==size:break
  headers={'User-Agent':'strata_local/1','Accept-Encoding':'identity'}
  if offset:headers['Range']='bytes='+str(offset)+'-'
  try:
   with open_url(Request(url,headers=headers),timeout=90) as response:
    if offset and response.status!=206:print('Range not supported; restarting '+target.name,flush=True);offset=0
    if response.status==206 and not response.headers.get('Content-Range','').startswith('bytes '+str(offset)+'-'):raise ValueError('Incorrect Content-Range')
    done=offset;last=time.monotonic()
    with part.open('ab' if offset else 'wb') as out:
     while True:
      chunk=response.read(1024*1024)
      if not chunk:break
      done+=len(chunk)
      if done>size:raise ValueError('Server returned more data than the pinned file size')
      out.write(chunk)
      if time.monotonic()-last>5:print(f'{target.name}: {done/size:.1%}',flush=True);last=time.monotonic()
   if part.stat().st_size==size:break
  except (OSError,TimeoutError) as exc:
   print('Network failure at '+LAST_HOST+': '+network_error(exc),flush=True)
   if attempt==2:raise RuntimeError('Cannot reach '+LAST_HOST+'. Check firewall/proxy or use Prepare-Models.ps1 -Probe. Any partial file is kept; use the same download folder to resume.') from exc
   print('Download interrupted; retrying...',flush=True);time.sleep(1+attempt)
 if not part.exists() or part.stat().st_size!=size or deploy.digest(part)!=sha:raise ValueError('Downloaded file SHA256/size mismatch: '+str(part))
 os.replace(part,target)
def safe_unpack(archive,destination,max_bytes):
 destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
 with tarfile.open(archive,'r:gz') as tf:
  members=tf.getmembers()
  if sum(m.size for m in members)>max_bytes:raise ValueError('Archive exceeds pinned installed size')
  for m in members:
   p=deploy.inside(destination,m.name)
   if m.isdir():p.mkdir(parents=True,exist_ok=True);continue
   if not m.isfile():raise ValueError('Links/devices are not accepted in engine archive')
   p.parent.mkdir(parents=True,exist_ok=True)
   with tf.extractfile(m) as src,p.open('wb') as out:shutil.copyfileobj(src,out)
def group_ok(group,assets,manifest):
 if group=='pack':
  try:manifest=deploy.pack_items(assets/'pack')
  except (OSError,ValueError,KeyError,TypeError):return False
 for item in manifest:
  if item['group']!=group:continue
  p=deploy.inside(assets/group,item['path'])
  if not p.is_file() or p.stat().st_size!=item['bytes'] or deploy.digest(p)!=item['sha256']:return False
 return True
def probe(url,size=None,range_probe=False):
 print('Checking: '+safe_url(url),flush=True)
 headers={'User-Agent':'strata_local/1'}
 if range_probe:headers['Range']='bytes=0-7'
 with open_url(Request(url,method='GET' if range_probe else 'HEAD',headers=headers),timeout=40) as r:
  length=r.headers.get('Content-Length')
  if range_probe:
   if r.status!=206:raise ValueError('MTP source must support HTTP range requests')
   data=r.read(8)
   if '.gguf' in url and data[:4]!=b'GGUF':raise ValueError('Remote file is not GGUF')
  actual=int(r.headers.get('Content-Range','/0').rsplit('/',1)[1]) if range_probe else (int(length) if length else None)
  if size is not None and actual!=size:raise ValueError('Remote size differs from pinned manifest')
  print(json.dumps({'url':safe_url(url),'status':r.status,'bytes':length}),flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--assets',default='../strata-assets');ap.add_argument('--no-images',action='store_true');ap.add_argument('--modelscope',default='https://www.modelscope.cn');ap.add_argument('--probe',action='store_true');ap.add_argument('--proxy');ap.add_argument('--timeout',type=int,default=25);a=ap.parse_args()
 global CONNECT_TIMEOUT,PROXY
 if not 5<=a.timeout<=600:raise ValueError('timeout must be 5..600 seconds')
 CONNECT_TIMEOUT=a.timeout;PROXY=a.proxy
 if PROXY and urlsplit(PROXY).scheme not in ('http','https'):raise ValueError('Proxy must be an HTTP/HTTPS proxy URL')
 assets=Path(a.assets).resolve()
 if assets==ROOT or any(assets.is_relative_to(ROOT/n) for n in ('vendor','scripts','docs','tests','manifests','.git','prereqs')):raise ValueError('Choose a separate assets folder, such as ./assets')
 images=not a.no_images;manifest=deploy.read(ROOT/'manifests/assets.json')['files'];version=deploy.read(ROOT/'manifests/versions.json')
 downloads=[(model_url(a.modelscope,x['group'],x['path']),x) for x in manifest if x['group']=='models' or (images and x['group']=='vision')]
 index_url=a.modelscope.rstrip('/')+'/models/Qwen/Qwen3.8-Flash-Next/resolve/master/model.safetensors.index.json'
 if a.probe:
  for u,x in downloads:probe(u,x['bytes'],range_probe=True)
  probe(version['engine_url'])
  with open_url(Request(index_url,headers={'User-Agent':'strata_local/1'}),timeout=40) as r:index=json.load(r)
  weight=next(v for k,v in index['weight_map'].items() if k.startswith('mtp.'))
  probe(a.modelscope.rstrip('/')+'/models/Qwen/Qwen3.8-Flash-Next/resolve/master/'+weight,range_probe=True)
  print('Source probe passed. Model weights were not downloaded.');return
 if sys.version_info[:2]!=(3,11):raise ValueError('Python 3.11 required')
 assets.mkdir(parents=True,exist_ok=True);(assets/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
 need=9*1024**3
 for item in manifest:
  if item['group']=='vision' and not images:continue
  f=assets/item['group']/item['path'];part=f.with_name(f.name+'.part');have=f.stat().st_size if f.is_file() else (part.stat().st_size if part.is_file() else 0);need+=max(0,item['bytes']-have)
 if shutil.disk_usage(assets).free<need:raise ValueError('Insufficient free space for downloads and preparation; need about '+str(round(need/1024**3,1))+' GiB more')
 print('STEP 1/4: GGUF model files'+(' and image encoder' if images else ''),flush=True)
 for u,x in downloads:fetch(u,assets/x['group']/x['path'],x['bytes'],x['sha256'])
 work=assets/'_work';work.mkdir(exist_ok=True)
 print('STEP 2/4: Engine',flush=True)
 if not group_ok('engine',assets,manifest):
  archive=work/'engine.tar.gz';fetch(version['engine_url'],archive,627812560,version['engine_archive_sha256']);safe_unpack(archive,assets/'engine',970245089)
  print('STEP 2/4: Engine',flush=True)
 if not group_ok('engine',assets,manifest):raise ValueError('Engine file verification failed')
 env=dict(os.environ,STRATA_SOURCE='modelscope',MODELSCOPE_ENDPOINT=a.modelscope,STRATA_GGUF_PY=str(ROOT/'vendor/llama.cpp/gguf-py'))
 if a.proxy:env.update(HTTPS_PROXY=a.proxy,HTTP_PROXY=a.proxy)
 def run(tool,*args):subprocess.run([sys.executable,str(ROOT/'vendor/strata/tools'/tool),*map(str,args)],check=True,env=env)
 print('STEP 3/4: Prepare model pack',flush=True)
 if not group_ok('pack',assets,manifest):
  # Discard only known generated files so an old tokenizer cannot survive a profile change.
  for name in deploy.read(ROOT/'manifests/assets.json')['generated_pack_files']+['pack-manifest.json']:
   deploy.inside(assets/'pack',name).unlink(missing_ok=True)
  shard=next(x['path'] for x in manifest if x['group']=='models' and '00001-of' in x['path']);run('iq_pack.py','--gguf',assets/'models'/shard,'--out',assets/'pack','--compat-bf16')
  catalog=deploy.read(ROOT/'manifests/assets.json');files=[]
  for name in catalog['generated_pack_files']:
   f=deploy.inside(assets/'pack',name)
   if not f.is_file() or not f.stat().st_size:raise ValueError('Missing generated pack file: '+name)
   files.append({'group':'pack','path':name,'bytes':f.stat().st_size,'sha256':deploy.digest(f)})
  deploy.save(assets/'pack/pack-manifest.json',{'profile':catalog['profile'],'sources':[x for x in manifest if x['group']=='models'],'files':files})
 if not group_ok('pack',assets,manifest):raise ValueError('Generated pack verification failed')
 print('STEP 4/4: Prepare MTP from ModelScope',flush=True)
 if not group_ok('mtp',assets,manifest):
  mtp=work/'mtp';run('mtp_fetch.py','fetch','--out',mtp);run('mtp_fetch.py','verify','--out',mtp);run('mtp_pack.py','--src',mtp,'--experts','q2_0','--out',mtp/'mtp-q2_0.gguf');run('mtp_rt.py','--gguf',mtp/'mtp-q2_0.gguf','--out',assets/'mtp');shutil.copy2(ROOT/'vendor/strata/data/draft_vocab.bin',assets/'mtp/draft_vocab.bin')
 for g in ['models','pack','mtp','engine']+(['vision'] if images else []):
  if not group_ok(g,assets,manifest):raise ValueError('Final prepared asset verification failed: '+g)
 deploy.save(assets/'prepared.json',{'profile':'Unsloth-UD-IQ3_XXS-v3.1','images':images,'engine':'0.1.57'})
 # Remove only this tool's fixed work directory after complete validation.
 if work.parent==assets and work.name=='_work':shutil.rmtree(work)
 print('Files ready. Run Install.cmd and choose: '+str(assets))
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERROR: '+str(e),file=sys.stderr);sys.exit(1)