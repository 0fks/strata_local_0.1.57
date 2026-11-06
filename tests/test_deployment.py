import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('deploy',Path(__file__).resolve().parents[1]/'scripts/strata_local.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class DeploymentTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name);self.s=d.read(d.REPO/'settings.example.json');self.s['install_root']=str(self.root/'runtime');self.s['python_exe']=str(self.root/'python.exe');self.s['cuda_dir']=str(self.root/'cuda');self.s['paths']={k:str(self.root/k) for k in self.s['paths']};self.keys=['test_'+str(i) for i in range(5)]
 def test_generated_text_mode_excludes_vision(self):
  self.s['images']=False;self.s['context']=131072;c=d.server_config(self.s,self.s['paths'],self.keys,self.root/'runtime');self.assertNotIn('vision',c);self.assertNotIn('--vision',c['args']);self.assertIn('131072',c['args']);self.assertEqual(c['env']['STRATA_PLE_AUTO_RAM'],'0');self.assertEqual(c['drafting'],'mtp');self.assertEqual(c['host'],'127.0.0.1')
 def test_lan_image_and_context_agree(self):
  self.s.update(lan=True,advertise_host='192.168.1.10',images=True,context=196608);d.validate(self.s);c=d.server_config(self.s,self.s['paths'],self.keys,self.root/'runtime');client=d.opencode(self.s,'http://192.168.1.10:8188',self.keys[1]);self.assertEqual(c['host'],'0.0.0.0');self.assertFalse(c['vision']['gpu']);self.assertEqual(c['vision']['threads'],8);self.assertEqual(client['model'],'strata/'+c['model_name']);model=client['providers']['strata']['models'][c['model_name']];self.assertIn('image',model['capabilities']['input']);self.assertEqual(model['limit']['context'],196608)
 def test_merge_preserves_mcp_and_other_provider_and_backup(self):
  p=self.root/'opencode.json';original={'mcp':{'servers':{'rea':{'type':'local','command':['node','rea.mjs']}}},'providers':{'other':{'package':'other-package'}},'permissions':[{'action':'websearch','effect':'deny','resource':'*'}]};d.save(p,original);d.merge_opencode(p,d.opencode(self.s,'http://127.0.0.1:8188',self.keys[0]));merged=d.read(p);self.assertEqual(merged['mcp'],original['mcp']);self.assertEqual(merged['providers']['other'],original['providers']['other']);self.assertEqual(merged['permissions'],original['permissions']);backups=list(self.root.glob('opencode.json.strata-backup-*'));self.assertEqual(len(backups),1);self.assertEqual(d.read(backups[0]),original)
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
  s=d.read(d.REPO/'settings.example.json');p=self.root/'config'/'settings.json';d.save(p,s);resolved=d.load_settings(p);self.assertEqual(resolved['install_root'],str((p.parent/'runtime').resolve()));self.assertEqual(resolved['paths']['models'],str((p.parent/'assets/models').resolve()))
 def test_runtime_inside_clone_allowed_but_source_protected(self):
  self.s['install_root']=str(d.REPO/'custom-runtime');d.validate(self.s)
  self.s['install_root']=str(d.REPO/'vendor/strata')
  with self.assertRaises(ValueError):d.validate(self.s)
if __name__=='__main__':unittest.main()