import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('provider_export',Path(__file__).resolve().parents[1]/'scripts/export_opencode_provider.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
spec=importlib.util.spec_from_file_location('provider_deploy',Path(__file__).resolve().parents[1]/'scripts/strata_local.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class ProviderExportTests(unittest.TestCase):
 def test_legacy_adapter_preserves_endpoint_model_limits_and_reasoning(self):
  for quant in d.QUANTS:
   s=d.read(d.REPO/'settings.example.json');s['quant']=quant;client=d.opencode(s,'http://127.0.0.1:18765','test-key');original=json.dumps(client);result=e.convert(client);provider=result['provider']['strata'];mid=d.model_id(s)
   self.assertEqual(set(result),{'provider'});self.assertEqual(provider['npm'],'@ai-sdk/openai-compatible');self.assertEqual(provider['options'],client['providers']['strata']['settings']);self.assertEqual(set(provider['models']),{mid});model=provider['models'][mid];self.assertTrue(model['tool_call']);self.assertIn('image',model['modalities']['input']);self.assertEqual(model['limit']['context'],196608);self.assertEqual(model['interleaved']['field'],'reasoning_content');self.assertNotIn('capabilities',model);self.assertEqual(json.dumps(client),original)
 def test_exports_can_be_pasted_without_touching_existing_config_or_client(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);s=d.read(d.REPO/'settings.example.json');paths=[]
   for mode,url in [('Local','http://127.0.0.1:18765'),('LAN','http://192.168.1.25:18765')]:
    file=root/'clients'/mode/'opencode.json';d.save(file,d.opencode(s,url,'test-'+mode));paths.append((file,file.read_bytes()))
   config={'$schema':'http://schema.example.test/config.json','provider':{'company':{'npm':'company-provider'}},'mcp':{'rea':{'command':['node','rea.js']}}};d.save(root/'config.json',config);before=(root/'config.json').read_bytes()
   written=e.export_root(root);self.assertEqual(len(written),4);self.assertEqual((root/'config.json').read_bytes(),before)
   entry=json.loads('{'+(root/'clients/Local/provider-entry.txt').read_text(encoding='utf-8')+'}');config['provider'].update(entry);self.assertIn('company',config['provider']);self.assertIn('strata',config['provider']);self.assertIn('rea',config['mcp']);self.assertEqual(config['$schema'],'http://schema.example.test/config.json')
   self.assertEqual(json.loads((root/'clients/LAN/provider.json').read_text())['provider']['strata']['options']['baseURL'],'http://192.168.1.25:18765/v1')
   for file,data in paths:self.assertEqual(file.read_bytes(),data)
 def test_legacy_input_is_not_converted_again(self):
  source={'provider':{'strata':{'npm':'@ai-sdk/openai-compatible','options':{'baseURL':'http://127.0.0.1:18765/v1'},'models':{'model':{'name':'test'}}}}};self.assertEqual(e.convert(source),source)
