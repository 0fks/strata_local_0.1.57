"""Fetch pinned SC117 files and generate pack/MTP; no pre-existing installation."""
import argparse, hashlib, json, os, shutil, subprocess, sys, tarfile, time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import strata_local as deploy
REV='eec4e10a2c29b440a2ae85591fa11569ce752963'
MODEL_REPO='SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF'
def model_url(host,group,name):return host.rstrip('/')+'/'+MODEL_REPO+'/resolve/'+REV+'/'+('IQ3_S/' if group=='models' else '')+quote(name)
def fetch(url,target,size,sha):
 target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():
  if target.stat().st_size==size and deploy.digest(target)==sha:print('Verified: '+target.name,flush=True);return
  raise ValueError('Existing file has wrong size/hash; review or rename it: '+str(target))
 part=target.with_name(target.name+'.part')
 for attempt in range(3):
  offset=part.stat().st_size if part.exists() else 0
  if offset>size:raise ValueError('Oversized partial download: '+str(part))
  if offset==size:break
  headers={'User-Agent':'strata_local/1','Accept-Encoding':'identity'}
  if offset:headers['Range']='bytes='+str(offset)+'-'
  try:
   with urlopen(Request(url,headers=headers),timeout=90) as response:
    if offset and response.status!=206:print('Range not supported; restarting '+target.name,flush=True);offset=0
    if response.status==206 and not response.headers.get('Content-Range','').startswith('bytes '+str(offset)+'-'):raise ValueError('Incorrect Content-Range')
    done=offset;last=time.monotonic()
    with part.open('ab' if offset else 'wb') as out:
     while True:
      chunk=response.read(8*1024*1024)
      if not chunk:break
      done+=len(chunk)
      if done>size:raise ValueError('Server returned more data than the pinned file size')
      out.write(chunk)
      if time.monotonic()-last>5:print(f'{target.name}: {done/size:.1%}',flush=True);last=time.monotonic()
   if part.stat().st_size==size:break
  except (OSError,TimeoutError) as exc:
   if attempt==2:raise
   print('Download interrupted; retrying: '+str(exc),flush=True);time.sleep(1+attempt)
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
 for item in manifest:
  if item['group']!=group:continue
  p=deploy.inside(assets/group,item['path'])
  if not p.is_file() or p.stat().st_size!=item['bytes'] or deploy.digest(p)!=item['sha256']:return False
 return True
def probe(url,size=None,range_probe=False):
 headers={'User-Agent':'strata_local/1'}
 if range_probe:headers['Range']='bytes=0-7'
 with urlopen(Request(url,method='GET' if range_probe else 'HEAD',headers=headers),timeout=40) as r:
  length=r.headers.get('Content-Length')
  if range_probe:
   if r.status!=206:raise ValueError('MTP source must support HTTP range requests')
   r.read(8)
  if size is not None and length and int(length)!=size:raise ValueError('Remote size differs from pinned manifest')
  print(json.dumps({'url':url,'status':r.status,'bytes':length}),flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--assets',default='../strata-assets');ap.add_argument('--no-images',action='store_true');ap.add_argument('--mirror',default='https://hf-mirror.com');ap.add_argument('--modelscope',default='https://www.modelscope.cn');ap.add_argument('--probe',action='store_true');a=ap.parse_args()
 assets=Path(a.assets).resolve()
 if assets==ROOT or any(assets.is_relative_to(ROOT/n) for n in ('vendor','scripts','docs','tests','manifests','.git','prereqs')):raise ValueError('Choose a separate assets folder, such as ./assets')
 images=not a.no_images;manifest=deploy.read(ROOT/'manifests/assets.json')['files'];version=deploy.read(ROOT/'manifests/versions.json')
 downloads=[(model_url(a.mirror,x['group'],x['path']),x) for x in manifest if x['group']=='models' or (images and x['group']=='vision')]
 index_url=a.modelscope.rstrip('/')+'/models/Qwen/Qwen3.8-Flash-Next/resolve/master/model.safetensors.index.json'
 if a.probe:
  for u,x in downloads:probe(u,x['bytes'])
  probe(version['engine_url'])
  with urlopen(Request(index_url,headers={'User-Agent':'strata_local/1'}),timeout=40) as r:index=json.load(r)
  weight=next(v for k,v in index['weight_map'].items() if k.startswith('mtp.'))
  probe(a.modelscope.rstrip('/')+'/models/Qwen/Qwen3.8-Flash-Next/resolve/master/'+weight,range_probe=True)
  print('Source probe passed. Model weights were not downloaded.');return
 if sys.version_info[:2]!=(3,11):raise ValueError('Python 3.11 required')
 assets.mkdir(parents=True,exist_ok=True);(assets/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
 need=6*1024**3
 for item in manifest:
  if item['group']=='vision' and not images:continue
  f=assets/item['group']/item['path'];part=f.with_name(f.name+'.part');have=f.stat().st_size if f.is_file() else (part.stat().st_size if part.is_file() else 0);need+=max(0,item['bytes']-have)
 if shutil.disk_usage(assets).free<need:raise ValueError('Insufficient free space for downloads and preparation; need about '+str(round(need/1024**3,1))+' GiB more')
 for u,x in downloads:fetch(u,assets/x['group']/x['path'],x['bytes'],x['sha256'])
 work=assets/'_work';work.mkdir(exist_ok=True)
 if not group_ok('engine',assets,manifest):
  archive=work/'engine.tar.gz';fetch(version['engine_url'],archive,627812560,version['engine_archive_sha256']);safe_unpack(archive,assets/'engine',970245089)
  if not group_ok('engine',assets,manifest):raise ValueError('Engine file verification failed')
 env=dict(os.environ,HF_ENDPOINT=a.mirror,STRATA_SOURCE='modelscope',MODELSCOPE_ENDPOINT=a.modelscope,STRATA_GGUF_PY=str(ROOT/'vendor/llama.cpp/gguf-py'))
 def run(tool,*args):subprocess.run([sys.executable,str(ROOT/'vendor/strata/tools'/tool),*map(str,args)],check=True,env=env)
 if not group_ok('pack',assets,manifest):
  shard=next(x['path'] for x in manifest if x['group']=='models' and '00001-of' in x['path']);run('iq_pack.py','--gguf',assets/'models'/shard,'--out',assets/'pack','--compat-bf16')
 if not group_ok('mtp',assets,manifest):
  mtp=work/'mtp';run('mtp_fetch.py','fetch','--out',mtp);run('mtp_fetch.py','verify','--out',mtp);run('mtp_pack.py','--src',mtp,'--experts','q2_0','--out',mtp/'mtp-q2_0.gguf');run('mtp_rt.py','--gguf',mtp/'mtp-q2_0.gguf','--out',assets/'mtp');shutil.copy2(ROOT/'vendor/strata/data/draft_vocab.bin',assets/'mtp/draft_vocab.bin')
 for g in ['models','pack','mtp','engine']+(['vision'] if images else []):
  if not group_ok(g,assets,manifest):raise ValueError('Final prepared asset verification failed: '+g)
 deploy.save(assets/'prepared.json',{'profile':'SC117-IQ3_S','images':images,'engine':'0.1.57'})
 # Remove only this tool's fixed work directory after complete validation.
 if work.parent==assets and work.name=='_work':shutil.rmtree(work)
 print('Files ready. Run Install.cmd and choose: '+str(assets))
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERROR: '+str(e),file=sys.stderr);sys.exit(1)