"""Fetch pinned SC117 files and generate pack/MTP; no pre-existing installation."""
import argparse, hashlib, json, os, shutil, subprocess, sys, tarfile, time, ssl
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler,ProxyHandler,HTTPSHandler
from urllib.parse import quote,urlsplit,urlunsplit
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import strata_local as deploy
REV='eec4e10a2c29b440a2ae85591fa11569ce752963'
MODEL_REPO='SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF'
CONNECT_TIMEOUT=25
PROXY=None
LAST_HOST=''
CA_FILE=None
TLS_CONTEXT=None
def safe_url(url):
 u=urlsplit(url);host=u.hostname or '';host=('['+host+']') if ':' in host else host;netloc=host+(':'+str(u.port) if u.port else '');return urlunsplit((u.scheme,netloc,u.path,'',''))
class NetworkRedirects(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  global LAST_HOST
  LAST_HOST=urlsplit(newurl).hostname or ''
  print('Redirect -> '+LAST_HOST,flush=True)
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def make_tls_context():
 # Keep system roots (including Windows enterprise roots) and add public roots.
 context=ssl.create_default_context()
 try:import certifi
 except ImportError:certifi=None
 if certifi is not None:context.load_verify_locations(cafile=certifi.where())
 if CA_FILE:context.load_verify_locations(cafile=CA_FILE)
 return context

def open_url(req,timeout=None):
 global LAST_HOST,TLS_CONTEXT
 LAST_HOST=urlsplit(req.full_url).hostname or ''
 handlers=[NetworkRedirects()]
 if urlsplit(req.full_url).scheme=='https':
  if TLS_CONTEXT is None:TLS_CONTEXT=make_tls_context()
  handlers.append(HTTPSHandler(context=TLS_CONTEXT))
 if PROXY:handlers.append(ProxyHandler({'http':PROXY,'https':PROXY}))
 return build_opener(*handlers).open(req,timeout=CONNECT_TIMEOUT)

def network_error(exc):
 if getattr(exc,'code',None):return 'HTTP '+str(exc.code)
 reason=getattr(exc,'reason',exc)
 if isinstance(reason,ssl.SSLCertVerificationError):
  message=getattr(reason,'verify_message',None) or str(reason)
  code=getattr(reason,'verify_code',None)
  return 'SSLCertVerificationError: '+message+' (verify_code '+str(code)+')'
 return type(reason).__name__+' (code '+str(getattr(reason,'winerror',None) or getattr(reason,'errno',None) or 'unknown')+')'

def model_url(host,group,name,quant='IQ3_S'):
 prefix=quant+'/' if group=='models' else ('strata/rt/' if group=='mtp' else '')
 return host.rstrip('/')+'/'+MODEL_REPO+'/resolve/'+REV+'/'+prefix+quote(name)
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
   if isinstance(getattr(exc,'reason',exc),ssl.SSLCertVerificationError):raise RuntimeError('TLS certificate verification failed at '+LAST_HOST+': '+network_error(exc)+'. Update with git pull and rerun Prepare-Models.cmd to refresh public CA certificates. If this persists, share this exact verification message. A trusted custom CA can be added with Prepare-Models.ps1 -CAFile <certificate.pem>.') from exc
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
def group_ok(group,assets,manifest,quant='IQ3_S'):
 paths=deploy.asset_paths(assets,quant)
 if group=='pack' and quant!='IQ3_S':
  try:manifest=deploy.pack_items(paths['pack'],quant)
  except (OSError,ValueError,KeyError,TypeError):return False
 for item in manifest:
  if item['group']!=group:continue
  p=deploy.inside(paths[group],item['path'])
  if not p.is_file() or p.stat().st_size!=item['bytes'] or deploy.digest(p)!=item['sha256']:return False
 return True

def download_entries(assets,quants,images,host):
 entries=[];seen=set()
 for quant in quants:
  paths=deploy.asset_paths(assets,quant)
  for item in deploy.catalog(quant)['files']:
   if item['group'] not in ('models','vision','mtp') or (item['group']=='vision' and not images):continue
   target=deploy.inside(paths[item['group']],item['path'])
   if target in seen:continue
   seen.add(target);entries.append((model_url(host,item['group'],item['path'],quant),item,target))
 return entries

def bundle_size(quants,images=True):
 shared=sum(x['bytes'] for x in deploy.catalog('IQ3_S')['files'] if x['group'] in ('mtp','engine','vision') and (images or x['group']!='vision'))
 pack=deploy.read(ROOT/'manifests/sc117-quants.json')['estimated_pack_bytes']
 return shared+sum(sum(x['bytes'] for x in deploy.catalog(q)['files'] if x['group']=='models')+pack for q in quants)

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
 ap=argparse.ArgumentParser()
 ap.add_argument('--assets',default='../strata-assets');ap.add_argument('--quants',nargs='+',choices=deploy.QUANTS,default=['IQ3_S','IQ3_XXS']);ap.add_argument('--no-images',action='store_true');ap.add_argument('--mirror',default='https://huggingface.co');ap.add_argument('--probe',action='store_true');ap.add_argument('--plan',action='store_true');ap.add_argument('--proxy');ap.add_argument('--ca-file');ap.add_argument('--timeout',type=int,default=25);a=ap.parse_args()
 global CONNECT_TIMEOUT,PROXY,CA_FILE,TLS_CONTEXT
 if not 5<=a.timeout<=600:raise ValueError('timeout must be 5..600 seconds')
 CONNECT_TIMEOUT=a.timeout;PROXY=a.proxy;CA_FILE=str(Path(a.ca_file).resolve()) if a.ca_file else None;TLS_CONTEXT=None
 if CA_FILE and not Path(CA_FILE).is_file():raise ValueError('CA file not found: '+CA_FILE)
 if PROXY and urlsplit(PROXY).scheme not in ('http','https'):raise ValueError('Proxy must be an HTTP/HTTPS proxy URL')
 assets=Path(a.assets).resolve();quants=list(dict.fromkeys(a.quants));images=not a.no_images
 if assets==ROOT or any(assets.is_relative_to(ROOT/n) for n in ('vendor','scripts','docs','tests','manifests','.git','prereqs')):raise ValueError('Choose a separate assets folder')
 version=deploy.read(ROOT/'manifests/versions.json');manifest=deploy.catalog('IQ3_S')['files'];downloads=download_entries(assets,quants,images,a.mirror)
 estimate=bundle_size(quants,images)
 print('SC117 models: '+', '.join(quants),flush=True)
 print('Estimated prepared assets: %.2f GB / %.2f GiB (pack size estimated); preparation environment needs extra space.'%(estimate/1e9,estimate/1024**3),flush=True)
 if a.plan:
  print(json.dumps({'quants':quants,'estimated_asset_bytes':estimate,'shared_groups':['mtp','vision','engine'],'paths':{q:deploy.asset_paths(assets,q) for q in quants}},indent=2));return
 if a.probe:
  failures=[]
  def check(label,fn):
   try:fn();print('PASS: '+label,flush=True)
   except Exception as exc:
    detail=network_error(exc) if isinstance(exc,(OSError,TimeoutError)) else str(exc)
    failures.append(label);print('FAIL: '+label+' | host='+LAST_HOST+' | '+detail,flush=True)
  for u,x,target in downloads:check(x['path'],lambda u=u,x=x:probe(u,x['bytes'],range_probe=True))
  check('GitHub engine',lambda:probe(version['engine_url']))
  if failures:raise RuntimeError('Connection checks failed: '+', '.join(failures)+'. No model weights were downloaded.')
  print('Source probe passed. Model weights were not downloaded.');return
 if sys.version_info[:2]!=(3,11):raise ValueError('Python 3.11 required')
 assets.mkdir(parents=True,exist_ok=True);(assets/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
 need=8*1024**3
 for u,x,f in downloads:
  part=f.with_name(f.name+'.part');have=f.stat().st_size if f.is_file() else (part.stat().st_size if part.is_file() else 0);need+=max(0,x['bytes']-have)
 if not group_ok('engine',assets,manifest):need+=970245089
 for q in quants:
  if not group_ok('pack',assets,deploy.catalog(q)['files'],q):need+=deploy.read(ROOT/'manifests/sc117-quants.json')['estimated_pack_bytes']
 if shutil.disk_usage(assets).free<need:raise ValueError('Insufficient free space; need about %.1f GiB more'%(need/1024**3))
 print('STEP 1/3: GGUF files, shared image encoder and ready-to-use MTP',flush=True)
 for u,x,target in downloads:fetch(u,target,x['bytes'],x['sha256'])
 work=assets/'_work';work.mkdir(exist_ok=True)
 print('STEP 2/3: Shared engine',flush=True)
 if not group_ok('engine',assets,manifest):
  archive=work/'engine.tar.gz';fetch(version['engine_url'],archive,627812560,version['engine_archive_sha256']);safe_unpack(archive,assets/'engine',970245089)
 if not group_ok('engine',assets,manifest):raise ValueError('Engine file verification failed')
 env=dict(os.environ,STRATA_GGUF_PY=str(ROOT/'vendor/llama.cpp/gguf-py'))
 if a.proxy:env.update(HTTPS_PROXY=a.proxy,HTTP_PROXY=a.proxy)
 for q in quants:
  print('STEP 3/3: Prepare pack - '+q,flush=True);catalog=deploy.catalog(q);files=catalog['files'];paths=deploy.asset_paths(assets,q)
  if not group_ok('pack',assets,files,q):
   # Recreate known outputs to avoid retaining another quant's tokenizer.
   names=deploy.read(ROOT/'manifests/sc117-quants.json')['generated_pack_files']
   for name in names+['pack-manifest.json']:deploy.inside(paths['pack'],name).unlink(missing_ok=True)
   shard=next(x['path'] for x in files if x['group']=='models' and '00001-of' in x['path'])
   subprocess.run([sys.executable,str(ROOT/'vendor/strata/tools/iq_pack.py'),'--gguf',str(Path(paths['models'])/shard),'--out',paths['pack'],'--compat-bf16'],check=True,env=env)
   if q!='IQ3_S':
    generated=[]
    for name in names:
     f=deploy.inside(paths['pack'],name)
     if not f.is_file() or not f.stat().st_size:raise ValueError('Missing generated pack file: '+name)
     generated.append({'group':'pack','path':name,'bytes':f.stat().st_size,'sha256':deploy.digest(f)})
    deploy.save(Path(paths['pack'])/'pack-manifest.json',{'profile':'SC117-'+q,'sources':[x for x in files if x['group']=='models'],'files':generated})
  for g in ['models','pack','mtp','engine']+(['vision'] if images else []):
   if not group_ok(g,assets,files,q):raise ValueError('Final prepared asset verification failed: '+q+'/'+g)
  deploy.save(Path(paths['pack'])/'prepared.json',{'profile':'SC117-'+q,'quant':q,'images':images,'engine':'0.1.57'})
 old=deploy.read(assets/'prepared.json') if (assets/'prepared.json').is_file() else {}
 available=set(old.get('available_quants',[]))|set(quants)
 # Do not claim a previously prepared profile is still valid after files were removed.
 available=[q for q in deploy.QUANTS if q in available and group_ok('models',assets,deploy.catalog(q)['files'],q) and group_ok('pack',assets,deploy.catalog(q)['files'],q)]
 deploy.save(assets/'prepared.json',{'profile':'SC117-bundle','available_quants':available,'images':images,'engine':'0.1.57'})
 if work.parent==assets and work.name=='_work':shutil.rmtree(work)
 print('Files ready. Run Install.cmd, choose this folder and a quant: '+str(assets))
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERROR: '+str(e),file=sys.stderr);sys.exit(1)
