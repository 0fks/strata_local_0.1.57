import importlib.util,json,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('bundle_prepare',Path(__file__).resolve().parents[1]/'scripts/prepare_models.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class BundleIntegrationTests(unittest.TestCase):
 def test_prepare_all_quants_resume_and_install_metadata(self):
  with tempfile.TemporaryDirectory() as temp:
   repo=Path(temp)/'repo';assets=Path(temp)/'assets';(repo/'manifests').mkdir(parents=True)
   original=p.deploy.read(p.ROOT/'manifests/assets.json');qmanifest=p.deploy.read(p.ROOT/'manifests/sc117-quants.json')
   payload=b'verified-fixture';import hashlib;sha=hashlib.sha256(payload).hexdigest()
   for x in original['files']:x.update(bytes=len(payload),sha256=sha)
   for models in qmanifest['models'].values():
    for x in models:x.update(bytes=len(payload),sha256=sha)
   qmanifest['estimated_pack_bytes']=len(payload)*len(qmanifest['generated_pack_files'])
   p.deploy.save(repo/'manifests/assets.json',original);p.deploy.save(repo/'manifests/sc117-quants.json',qmanifest)
   p.deploy.save(repo/'manifests/versions.json',{'engine_url':'https://example.test/engine.tar.gz','engine_archive_sha256':'0'*64})
   for x in original['files']:
    if x['group']=='engine':
     f=assets/'engine'/x['path'];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(payload)
   downloaded=[];built=[]
   def fake_fetch(url,target,size,sha):
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload);downloaded.append(str(target))
   def fake_build(args,**kwargs):
    folder=Path(args[args.index('--out')+1]);built.append(str(folder))
    for name in qmanifest['generated_pack_files']:
     f=folder/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(payload)
   args=['prepare_models.py','--assets',str(assets),'--quants','IQ3_S','IQ3_XXS','IQ2_XS']
   with patch.object(p,'ROOT',repo),patch.object(p.deploy,'REPO',repo),patch.object(p,'fetch',side_effect=fake_fetch),patch.object(p.subprocess,'run',side_effect=fake_build),patch.object(sys,'argv',args):p.main()
   self.assertEqual(len(built),3);self.assertEqual(len(downloaded),11)
   receipt=p.deploy.read(assets/'prepared.json');self.assertEqual(receipt['available_quants'],list(p.deploy.QUANTS))
   with patch.object(p.deploy,'REPO',repo):
    for quant in p.deploy.QUANTS:
     settings={'quant':quant,'images':True,'paths':p.deploy.asset_paths(assets,quant)}
     for item in p.deploy.items(settings):
      f=Path(settings['paths'][item['group']])/item['path'];self.assertEqual(p.deploy.digest(f),item['sha256'])
    # Moving an NVMe changes the prefix, while model-specific paths remain distinct.
    self.assertEqual(Path(p.deploy.asset_paths(Path(temp)/'moved', 'IQ3_XXS')['models']).parts[-2:],('models','IQ3_XXS'))
   # A fully prepared rerun must skip every pack conversion.
   with patch.object(p,'ROOT',repo),patch.object(p.deploy,'REPO',repo),patch.object(p,'fetch',side_effect=fake_fetch),patch.object(p.subprocess,'run') as build,patch.object(sys,'argv',args):p.main();build.assert_not_called()
