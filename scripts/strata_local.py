"""Personal Strata deployment. Python 3.11 standard library only."""
import argparse, ctypes, datetime, hashlib, json, os, platform, secrets, shutil, socket, subprocess, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
REPO=Path(__file__).resolve().parent.parent
MODEL='qwen3.8-flash-next-unsloth-ud-iq3_xxs-v31'
CONTEXTS=(65536,131072,196608,262144)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,p)
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for c in iter(lambda:f.read(8*1024*1024),b''):h.update(c)
    return h.hexdigest()
def inside(root,relative):
    root=Path(root).resolve();p=(root/relative).resolve()
    if not p.is_relative_to(root):raise ValueError('Path escapes asset root: '+relative)
    return p
def validate(s):
    if type(s.get('context')) is not int or s['context'] not in CONTEXTS:raise ValueError('Choose context 65536/131072/196608/262144')
    if type(s.get('port')) is not int or not 1024<=s['port']<=65535:raise ValueError('Port must be 1024..65535')
    for k in ('images','lan','copy_assets','merge_opencode','shortcuts','startup'):
        if type(s.get(k)) is not bool:raise ValueError('Boolean required: '+k)
    if s['lan']:
        h=s.get('advertise_host','')
        if not h or any(x in h for x in ' /\\:@') or h in ('0.0.0.0','127.0.0.1','localhost'):raise ValueError('Enter the actual LAN IPv4 address or hostname')
    for k in ('models','pack','mtp','engine')+ (('vision',) if s['images'] else ()):
        if not Path(s['paths'][k]).is_absolute():raise ValueError('Absolute asset path required: '+k)
    for k in ('install_root','python_exe','cuda_dir'):
        if not Path(s[k]).is_absolute():raise ValueError('Absolute path required: '+k)
    target=Path(s['install_root']).resolve()
    if target==REPO or any(target.is_relative_to(REPO/n) for n in ('vendor','scripts','docs','tests','manifests','.git')):raise ValueError('Choose a separate runtime folder, not source/documentation folders')
    return s
def base_items(s):return [x for x in read(REPO/'manifests/assets.json')['files'] if s['images'] or x['group']!='vision']

def pack_items(folder):
    manifest=read(REPO/'manifests/assets.json');receipt=read(Path(folder)/'pack-manifest.json')
    pins=[x for x in manifest['files'] if x['group']=='models']
    if receipt.get('profile')!=manifest['profile'] or receipt.get('sources')!=pins:raise ValueError('Pack was not prepared for the pinned Unsloth model; run Prepare-Models.cmd')
    files=receipt.get('files',[]);expected=set(manifest['generated_pack_files'])
    if len(files)!=len(expected) or {x['path'] for x in files}!=expected:raise ValueError('Incomplete generated pack manifest')
    for x in files:
        if x.get('group')!='pack' or type(x.get('bytes')) is not int or x['bytes']<=0 or len(x.get('sha256',''))!=64 or any(c not in '0123456789abcdef' for c in x['sha256']):raise ValueError('Invalid generated pack manifest')
    return files

def items(s):return base_items(s)+pack_items(s['paths']['pack'])
def verify_assets(s,full=True):
    errors=[]
    try:checked=items(s)
    except (OSError,ValueError,KeyError,TypeError) as exc:errors.append('Pack not ready: '+str(exc));checked=base_items(s)
    for x in checked:
        p=inside(s['paths'][x['group']],x['path'])
        if not p.is_file():errors.append('Missing: '+str(p));continue
        if p.stat().st_size!=x['bytes']:errors.append('Size mismatch: '+str(p));continue
        if full:
            print('SHA-256 check: '+p.name,flush=True)
            if digest(p)!=x['sha256']:errors.append('SHA256 mismatch: '+str(p))
    cuda=Path(s['cuda_dir'])
    if not (cuda/'cudart64_13.dll').is_file():errors.append('CUDA 13 runtime cudart64_13.dll missing from cuda_dir')
    # Manifest hash pins the separately distributed, originally signed engine package.
    ep=Path(s['paths']['engine'])/'engine-component.json'
    if ep.is_file() and digest(ep)!=read(REPO/'manifests/versions.json')['engine_manifest_sha256']:errors.append('Engine manifest does not match pinned 0.1.57')
    if errors:raise ValueError('\n'.join(errors))
    return sum(x['bytes'] for x in items(s))
def load_settings(path):
    path=Path(path).resolve();s=read(path)
    for k in ('install_root','python_exe','cuda_dir'):
        q=Path(s[k]);s[k]=str((path.parent/q).resolve()) if not q.is_absolute() else str(q.resolve())
    s['paths']={k:str((path.parent/Path(v)).resolve()) if not Path(v).is_absolute() else str(Path(v).resolve()) for k,v in s['paths'].items()}
    return s
def model_id(s):return MODEL+('-cpu-vision-' if s['images'] else '-text-')+str(s['context']//1024)+'k'
def server_config(s,paths,keys,root):
    model1=next(x['path'] for x in base_items(s) if x['group']=='models' and '00001-of' in x['path'])
    # Four-shard Unsloth: engine 0.1.57 discovers the PLE shard, matching upstream setup.
    a=['--pack',paths['pack'],'--native',str(Path(paths['models'])/model1),'--expert-profile',str(root/'source/data/expert-profile.bin'),'--expert-cache','auto','--prefill','auto:8192','--spec','4','--spec-min-p','0.5','--mtp',paths['mtp'],'--max-context',str(s['context']),'--kv','int8','--kv-resident','16384','--resident-budget-gib','48','--vram-reserve-mib','1800','--pool-workers','7']
    c={'exe':str(Path(paths['engine'])/'strata.exe'),'args':a,'cwd':str(root/'source'),'tokenizer':str(Path(paths['pack'])/'tokenizer'),'model_name':model_id(s),'log':str(root/'logs/engine.log'),'lib_dirs':[paths['engine'],s['cuda_dir']],'host':'0.0.0.0' if s['lan'] else '127.0.0.1','port':s['port'],'gpu':0,'gpus_asked':True,'fit_max_tokens':True,'api_key':keys,'drafting':'mtp','env':{'STRATA_PLE_AUTO_RAM':'0'},'sampling':{'temperature':0,'top_p':1.0,'top_k':64,'min_p':0,'repetition_penalty':1.0,'presence_penalty':0,'frequency_penalty':0}}
    if s['images']:
        a+=['--vision'];mm=next(x['path'] for x in base_items(s) if x['group']=='vision');c['vision']={'exe':str(Path(paths['engine'])/'strata-vision.exe'),'mmproj':str(Path(paths['vision'])/mm),'model':str(Path(paths['models'])/model1),'gpu':False,'threads':8,'max_tokens':1024}
    return c
def opencode(s,url,key):
    mid=model_id(s)
    return {'$schema':'https://opencode.ai/config.json','model':'strata/'+mid,'providers':{'strata':{'package':'@opencode/ai/providers/openai-compatible','name':'Strata Local '+str(s['context']//1024)+'K','settings':{'baseURL':url+'/v1','apiKey':key},'models':{mid:{'name':'Unsloth UD-IQ3_XXS v3.1 '+('CPU Vision ' if s['images'] else 'Text ')+str(s['context']//1024)+'K','capabilities':{'input':['text','image'] if s['images'] else ['text'],'output':['text'],'tools':True},'compatibility':{'reasoningField':'reasoning_content'},'limit':{'context':s['context'],'output':16384}}}}},'compaction':{'auto':True,'buffer':24576,'keep':{'tokens':8000}}}
def merge_opencode(path,new):
    path=Path(path);old=read(path) if path.exists() else {}
    if path.exists():shutil.copy2(path,path.with_name(path.name+'.strata-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')))
    old.setdefault('providers',{})['strata']=new['providers']['strata'];old['model']=new['model'];old['compaction']=new['compaction'];save(path,old)
def invoke(args,**kw):subprocess.run([str(x) for x in args],check=True,**kw)
def protect(root):
    if os.name=='nt':
        user=os.environ.get('USERDOMAIN','')+'\\'+os.environ['USERNAME']
        invoke(['icacls',root,'/inheritance:r','/grant:r',user+':(OI)(CI)F','*S-1-5-18:(OI)(CI)F','*S-1-5-32-544:(OI)(CI)F'],stdout=subprocess.DEVNULL)
def prerequisites(s):
    if os.name!='nt' or platform.machine().lower() not in ('amd64','x86_64'):raise ValueError('Windows x64 required')
    version=subprocess.check_output([s['python_exe'],'-c','import sys,struct;print("%s.%s %s"%(sys.version_info.major,sys.version_info.minor,struct.calcsize("P")*8))'],text=True).strip()
    if version!='3.11 64':raise ValueError('Manually install Python 3.11 x64; found '+version)
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=driver_version,memory.total','--format=csv,noheader,nounits'],text=True).splitlines()[0].split(',')
    driver=gpu[0].strip()
    if int(gpu[1].strip())<15*1024:raise ValueError('This profile requires a 16GB-class NVIDIA GPU; tune smaller cards separately')
    if tuple(int(x) for x in driver.split('.')[:2])<(580,65):raise ValueError('NVIDIA driver 580.65+ required')
    total=int(subprocess.check_output(['powershell.exe','-NoProfile','-Command','(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory'],text=True).strip())
    if total<90*1024**3:raise ValueError('This Unsloth UD-IQ3_XXS profile requires about 96GB RAM; tune separately on smaller PCs')
def install(s,quick=False):
    validate(s);prerequisites(s);size=verify_assets(s,not quick);root=Path(s['install_root']).resolve()
    if (root/'installed.json').exists():raise ValueError('Installation already exists; use a new install_root. Existing configuration was preserved.')
    if root.exists() and any(root.iterdir()):raise ValueError('Choose an empty install_root')
    needed=(size if s['copy_assets'] else 0)+2*1024**3
    drive=root
    while not drive.exists():drive=drive.parent
    if shutil.disk_usage(drive).free<needed:raise ValueError('Insufficient free disk space')
    root.mkdir(parents=True,exist_ok=True);(root/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8');protect(root);(root/'logs').mkdir()
    shutil.copytree(REPO/'vendor/strata',root/'source',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copy2(Path(__file__),root/'manager.py')
    paths=dict(s['paths'])
    if s['copy_assets']:
        paths={g:str(root/'assets'/g) for g in s['paths']}
        for x in items(s):
            dest=inside(paths[x['group']],x['path']);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(inside(s['paths'][x['group']],x['path']),dest)
        shutil.copy2(Path(s['paths']['pack'])/'pack-manifest.json',Path(paths['pack'])/'pack-manifest.json')
        copied=dict(s,paths=paths);verify_assets(copied,not quick)
    invoke([s['python_exe'],'-m','venv',root/'.venv']);py=root/'.venv/Scripts/python.exe'
    pip=[py,'-m','pip','install','-r',root/'source/requirements.txt']
    invoke(pip);invoke([py,'-m','pip','check'])
    keys=[secrets.token_urlsafe(36) for _ in range(5)];save(root/'server.json',server_config(s,paths,keys,root));save(root/'api-keys.private.json',{'local':keys[0],'lan':keys[1],'reserved':keys[2:]})
    local=opencode(s,'http://127.0.0.1:'+str(s['port']),keys[0]);save(root/'clients/Local/opencode.json',local)
    if s['lan']:save(root/'clients/LAN/opencode.json',opencode(s,'http://'+s['advertise_host']+':'+str(s['port']),keys[1]))
    for verb in ('start','stop','check'):
        (root/(verb.capitalize()+'-Strata.cmd')).write_text('@echo off\r\n"%~dp0.venv\\Scripts\\python.exe" "%~dp0manager.py" '+verb+' --root "%~dp0."\r\nif errorlevel 1 pause\r\n',encoding='ascii')
    if s['merge_opencode']:merge_opencode(Path.home()/'.config/opencode/opencode.json',local)
    save(root/'installed.json',{'settings':s,'version':read(REPO/'manifests/versions.json'),'full_asset_hash_check':not quick})
    if s['shortcuts'] or s['startup']:shortcuts(root,s)
    print('Installed. OpenCode JSON: '+str(root/'clients')+' (contains private keys)')
    return root
def shortcuts(root,s):
    # Use an env variable, not interpolation, to safely pass a path containing quotes or spaces.
    code="$w=New-Object -ComObject WScript.Shell;$r=$env:STRATA_LOCAL_SHORTCUT_ROOT;"
    if s['shortcuts']:
        for name,target in [('Strata Local Start','Start-Strata.cmd'),('Strata Local Stop','Stop-Strata.cmd')]:
            code+="$l=$w.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) '"+name+".lnk'));$l.TargetPath=Join-Path $r '"+target+"';$l.WorkingDirectory=$r;$l.IconLocation=\"$env:SystemRoot\\System32\\shell32.dll,0\";$l.Save();"
    if s['startup']:code+="$l=$w.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Startup')) 'Strata Local Start.lnk'));$l.TargetPath=Join-Path $r 'Start-Strata.cmd';$l.WorkingDirectory=$r;$l.Save();"
    invoke(['powershell.exe','-NoProfile','-Command',code],env=dict(os.environ,STRATA_LOCAL_SHORTCUT_ROOT=str(root)))
def stamp(pid):
    if os.name!='nt':return None
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE;k.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4;k.CloseHandle.argtypes=[wintypes.HANDLE]
    h=k.OpenProcess(0x1000,False,pid)
    if not h:return None
    t=[wintypes.FILETIME() for _ in range(4)]
    try:
        if not k.GetProcessTimes(h,*[ctypes.byref(x) for x in t]):return None
        return (t[0].dwHighDateTime<<32)|t[0].dwLowDateTime
    finally:k.CloseHandle(h)
def health(root):
    c=read(root/'server.json');req=Request('http://127.0.0.1:'+str(c['port'])+'/health',headers={'Authorization':'Bearer '+c['api_key'][0]})
    with urlopen(req,timeout=3) as r:return json.load(r)
def start(root):
    c=read(root/'server.json');state=root/'server-process.private.json'
    try:
        h=health(root)
        if h.get('loaded') and h.get('model')==c['model_name']:print('Already running.');return
    except (OSError,URLError):pass
    if state.exists():
        st=read(state)
        if stamp(st['pid'])==st['creation']:raise ValueError('Owned server is already starting; use check')
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1',c['port']))==0:raise ValueError('Port occupied. No process was stopped.')
    log=(root/'logs/server.log').open('ab')
    try:p=subprocess.Popen([str(root/'.venv/Scripts/python.exe'),str(root/'source/serve/server.py'),'--engine','strata','--config',str(root/'server.json'),'--host',c['host'],'--port',str(c['port'])],cwd=root/'source',stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP)
    finally:log.close()
    created=stamp(p.pid)
    if created is None:raise RuntimeError('Server exited early; inspect logs/server.log')
    save(state,{'pid':p.pid,'creation':created,'root':str(root)})
    for _ in range(100):
        if p.poll() is not None or stamp(p.pid)!=created:raise RuntimeError('Server exited; inspect logs/server.log')
        try:
            h=health(root)
            if h.get('loaded') and h.get('model')==c['model_name']:print('Ready: http://127.0.0.1:'+str(c['port']));return
        except (OSError,URLError):pass
        time.sleep(2)
    raise RuntimeError('Still loading. Inspect logs and run Check-Strata.cmd. No process was killed.')
def stop(root):
    state=root/'server-process.private.json'
    if not state.exists():print('No owned server record; nothing stopped.');return
    st=read(state)
    if st.get('root')!=str(root):raise ValueError('Ownership path mismatch; nothing stopped')
    if stamp(st['pid'])!=st['creation']:print('Stale record; nothing stopped.');return
    invoke(['taskkill','/PID',str(st['pid']),'/T','/F']);state.unlink();print('Owned server stopped.')
def rebind(root,assets,full=True):
    root=Path(root).resolve();assets=Path(assets)
    if not assets.is_absolute():assets=REPO/assets
    assets=assets.resolve();record=root/'installed.json';old=read(root/'server.json');meta=read(record)
    if not old.get('model_name','').startswith(MODEL+'-'):raise ValueError('This runtime uses a different model profile; use its original installer to change paths')
    state=root/'server-process.private.json'
    if state.exists():
        st=read(state)
        if st.get('creation') is not None and stamp(st['pid'])==st['creation']:raise ValueError('Stop Strata before changing asset paths')
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1',old['port']))==0:raise ValueError('API port is active. Stop the service first; nothing changed.')
    settings=dict(meta['settings']);paths={g:str(assets/g) for g in settings['paths']};settings['paths']=paths
    verify_assets(settings,full)
    replacement=server_config(settings,paths,old['api_key'],root)
    new=dict(old);args=list(old['args'])
    # Change only file locations; preserve user tuning, keys, model identity and network settings.
    for flag in ('--pack','--native','--mtp'):
        if flag not in args:raise ValueError('Cannot identify required path flag: '+flag)
        pos=args.index(flag)+1;args[pos]=replacement['args'][replacement['args'].index(flag)+1]
    new['args']=args;new['tokenizer']=replacement['tokenizer'];new['exe']=replacement['exe']
    old_engine=str(Path(old['exe']).parent);new['lib_dirs']=[paths['engine']]+[x for x in old.get('lib_dirs',[]) if x!=old_engine and x!=paths['engine']]
    if 'vision' in old:
        new['vision']=dict(old['vision'])
        for key in ('exe','model','mmproj'):new['vision'][key]=replacement['vision'][key]
    local=REPO/'settings.local.json';local_new=None
    if local.exists():
        current=load_settings(local)
        if Path(current['install_root']).resolve()==root:
            local_new=read(local);local_new['paths']=paths;local_new['copy_assets']=False
    suffix='.before-path-change-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    shutil.copy2(root/'server.json',root/('server.json'+suffix));shutil.copy2(record,root/('installed.json'+suffix))
    local_backup=root/('settings.local.json'+suffix)
    if local_new is not None:shutil.copy2(local,local_backup)
    try:
        save(root/'server.json',new);meta['settings']=settings;meta['settings']['copy_assets']=False;save(record,meta)
        if local_new is not None:save(local,local_new)
    except Exception:
        shutil.copy2(root/('server.json'+suffix),root/'server.json');shutil.copy2(root/('installed.json'+suffix),record)
        if local_new is not None:shutil.copy2(local_backup,local)
        raise
    print('Asset paths updated: '+str(assets)+'. OpenCode settings and API keys are unchanged.')

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['plan','verify-assets','install','start','stop','check','rebind']);parser.add_argument('--settings',default=str(REPO/'settings.local.json'));parser.add_argument('--root');parser.add_argument('--assets');parser.add_argument('--skip-full-hash',action='store_true');parser.add_argument('--start',action='store_true');args=parser.parse_args(argv)
    if args.command in ('start','stop','check','rebind'):
        if not args.root:parser.error('--root is required')
        root=Path(args.root).resolve()
        if args.command=='rebind':
            if not args.assets:parser.error('--assets is required')
            rebind(root,args.assets,not args.skip_full_hash)
        elif args.command=='start':start(root)
        elif args.command=='stop':stop(root)
        else:print(json.dumps(health(root),indent=2))
        return
    s=validate(load_settings(args.settings))
    if args.command=='plan':
        size=verify_assets(s,False);print(json.dumps({'settings':s,'asset_bytes':size,'will_copy_assets':s['copy_assets'],'hashes_checked':False,'starts_service':False},ensure_ascii=True,indent=2))
    elif args.command=='verify-assets':verify_assets(s,True);print('All asset hashes match.')
    else:
        root=install(s,args.skip_full_hash)
        if args.start:start(root)
if __name__=='__main__':
    try:main()
    except Exception as e:print('ERROR: '+str(e),file=sys.stderr);sys.exit(1)