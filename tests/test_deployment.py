import importlib.util,json,tempfile,unittest
from unittest.mock import patch,MagicMock
from pathlib import Path
spec=importlib.util.spec_from_file_location('deploy',Path(__file__).resolve().parents[1]/'scripts/strata_local.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class DeploymentTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name);self.s=d.read(d.REPO/'settings.example.json');self.s['install_root']=str(self.root/'runtime');self.s['python_exe']=str(self.root/'python.exe');self.s['cuda_dir']=str(self.root/'cuda');self.s['paths']={k:str(self.root/k) for k in self.s['paths']};self.keys=['test_'+str(i) for i in range(5)]
 def test_generated_text_mode_excludes_vision(self):
  self.s['images']=False;self.s['context']=131072;c=d.server_config(self.s,self.s['paths'],self.keys,self.root/'runtime');self.assertNotIn('vision',c);self.assertNotIn('--vision',c['args']);self.assertIn('131072',c['args']);self.assertEqual(c['env']['STRATA_PLE_AUTO_RAM'],'0');self.assertEqual(c['drafting'],'mtp');self.assertEqual(c['host'],'127.0.0.1')
 def test_lan_image_and_context_agree(self):
  self.s.update(lan=True,advertise_host='192.168.1.10',images=True,context=196608);d.validate(self.s);c=d.server_config(self.s,self.s['paths'],self.keys,self.root/'runtime');client=d.opencode(self.s,'http://192.168.1.10:18765',self.keys[1]);self.assertEqual(c['host'],'0.0.0.0');self.assertFalse(c['vision']['gpu']);self.assertEqual(c['vision']['threads'],8);self.assertEqual(client['model'],'strata/'+c['model_name']);model=client['providers']['strata']['models'][c['model_name']];self.assertIn('image',model['capabilities']['input']);self.assertEqual(model['limit']['context'],196608)
 def test_merge_preserves_mcp_and_other_provider_and_backup(self):
  p=self.root/'opencode.json';original={'mcp':{'servers':{'rea':{'type':'local','command':['node','rea.mjs']}}},'providers':{'other':{'package':'other-package'}},'permissions':[{'action':'websearch','effect':'deny','resource':'*'}]};d.save(p,original);d.merge_opencode(p,d.opencode(self.s,'http://127.0.0.1:18765',self.keys[0]));merged=d.read(p);self.assertEqual(merged['mcp'],original['mcp']);self.assertEqual(merged['providers']['other'],original['providers']['other']);self.assertEqual(merged['permissions'],original['permissions']);backups=list(self.root.glob('opencode.json.strata-backup-*'));self.assertEqual(len(backups),1);self.assertEqual(d.read(backups[0]),original)
 def test_four_shard_model_uses_upstream_auto_discovery(self):
  c=d.server_config(self.s,self.s['paths'],self.keys,self.root/'runtime')
  self.assertIn('00001-of-00004.gguf',c['args'][c['args'].index('--native')+1]);self.assertNotIn('--ple-gguf',c['args']);self.assertIn('unsloth',c['model_name']);self.assertEqual(c['port'],18765)
 def test_pack_receipt_rejects_another_model_and_changed_files(self):
  manifest=d.read(d.REPO/'manifests/assets.json');folder=self.root/'pack';files=[]
  for name in manifest['generated_pack_files']:
   f=folder/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'generated-pack');files.append({'group':'pack','path':name,'bytes':f.stat().st_size,'sha256':d.digest(f)})
  receipt={'profile':manifest['profile'],'sources':[x for x in manifest['files'] if x['group']=='models'],'files':files};d.save(folder/'pack-manifest.json',receipt)
  self.assertEqual(len(d.pack_items(folder)),len(files))
  receipt['sources'][0]['sha256']='0'*64;d.save(folder/'pack-manifest.json',receipt)
  with self.assertRaises(ValueError):d.pack_items(folder)
 def test_invalid_context_rejected(self):
  self.s['context']=192
  with self.assertRaises(ValueError):d.validate(self.s)
 def test_lan_wildcard_not_client_address(self):
  self.s.update(lan=True,advertise_host='0.0.0.0')
  with self.assertRaises(ValueError):d.validate(self.s)
 def test_traversal_rejected(self):
  with self.assertRaises(ValueError):d.inside(self.root,'../escape')
 def test_missing_assets_report_paths(self):
  with self.assertRaises(ValueError) as e:d.verify_assets(self.s,False)
  self.assertIn('Missing:',str(e.exception));self.assertIn('cudart64_13.dll',str(e.exception))
 def test_stop_has_no_authority_without_record(self):
  d.stop(self.root)
 def test_server_config_never_uses_live_installation(self):
  c=d.server_config(self.s,self.s['paths'],self.keys,self.root/'runtime');self.assertNotIn('D:\\Git\\Strata',json.dumps(c));self.assertEqual(c['api_key'],self.keys)
 def test_relative_paths_resolve_from_settings_not_cwd(self):
  s=d.read(d.REPO/'settings.example.json');p=self.root/'config'/'settings.json';d.save(p,s);resolved=d.load_settings(p);self.assertEqual(resolved['install_root'],str((p.parent/'runtime').resolve()));self.assertEqual(resolved['paths']['models'],str((p.parent/'../strata-assets/models').resolve()))
 def test_runtime_inside_clone_allowed_but_source_protected(self):
  self.s['install_root']=str(d.REPO/'custom-runtime');d.validate(self.s)
  self.s['install_root']=str(d.REPO/'vendor/strata')
  with self.assertRaises(ValueError):d.validate(self.s)
 def rebind_fixture(self):
  root=self.root/'runtime';root.mkdir();old=d.server_config(self.s,self.s['paths'],self.keys,root);old['sampling']['temperature']=0.25;old['args']+=['--custom-flag','keep'];d.save(root/'server.json',old);d.save(root/'installed.json',{'settings':self.s});d.save(root/'clients/Local/opencode.json',{'private':'untouched'});return root,old
 def test_rebind_preserves_keys_client_and_custom_settings(self):
  root,old=self.rebind_fixture();client=(root/'clients/Local/opencode.json').read_bytes();sock=MagicMock();sock.__enter__.return_value.connect_ex.return_value=1
  with patch.object(d,'verify_assets',return_value=0),patch.object(d.socket,'socket',return_value=sock):d.rebind(root,self.root/'new assets',False)
  new=d.read(root/'server.json');self.assertEqual(new['api_key'],old['api_key']);self.assertEqual(new['model_name'],old['model_name']);self.assertEqual(new['sampling'],old['sampling']);self.assertEqual(new['args'][-2:],old['args'][-2:]);self.assertEqual(client,(root/'clients/Local/opencode.json').read_bytes());self.assertTrue(Path(new['exe']).is_relative_to((self.root/'new assets').resolve()));self.assertEqual(len(list(root.glob('server.json.before-path-change-*'))),1)
 def test_rebind_rejects_running_owned_server(self):
  root,old=self.rebind_fixture();d.save(root/'server-process.private.json',{'pid':123,'creation':777});before=(root/'server.json').read_bytes()
  with patch.object(d,'stamp',return_value=777):
   with self.assertRaises(ValueError):d.rebind(root,self.root/'new assets',False)
  self.assertEqual(before,(root/'server.json').read_bytes())
 def test_rebind_invalid_assets_leave_config_unchanged(self):
  root,old=self.rebind_fixture();before=(root/'server.json').read_bytes();sock=MagicMock();sock.__enter__.return_value.connect_ex.return_value=1
  with patch.object(d,'verify_assets',side_effect=ValueError('missing asset')),patch.object(d.socket,'socket',return_value=sock):
   with self.assertRaises(ValueError):d.rebind(root,self.root/'missing',False)
  self.assertEqual(before,(root/'server.json').read_bytes())
if __name__=='__main__':unittest.main()