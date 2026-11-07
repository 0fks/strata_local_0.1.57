import hashlib,http.server,importlib.util,io,tarfile,tempfile,threading,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
from contextlib import redirect_stdout
spec=importlib.util.spec_from_file_location('prepare',Path(__file__).resolve().parents[1]/'scripts/prepare_models.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
DATA=b'local-test-download-data'*80
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  start=int(self.headers.get('Range','bytes=0-').split('=')[1].split('-')[0]);self.send_response(206 if start else 200)
  if start:self.send_header('Content-Range',f'bytes {start}-{len(DATA)-1}/{len(DATA)}')
  self.end_headers();self.wfile.write(DATA[start:])
 def log_message(self,*args):pass
class DownloadTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.addCleanup(self.server.server_close);self.addCleanup(self.server.shutdown);self.url='http://127.0.0.1:'+str(self.server.server_port)
 def test_resume_and_hash(self):
  f=self.root/'model.gguf';f.with_name(f.name+'.part').write_bytes(DATA[:31]);p.fetch(self.url,f,len(DATA),hashlib.sha256(DATA).hexdigest());self.assertEqual(f.read_bytes(),DATA)
 def test_bad_hash_not_promoted(self):
  f=self.root/'bad.gguf'
  with self.assertRaises(ValueError):p.fetch(self.url,f,len(DATA),'0'*64)
  self.assertFalse(f.exists())
 def test_archive_traversal_rejected(self):
  archive=self.root/'bad.tar.gz'
  with tarfile.open(archive,'w:gz') as tf:
   member=tarfile.TarInfo('../escape');member.size=1;tf.addfile(member,io.BytesIO(b'x'))
  with self.assertRaises(ValueError):p.safe_unpack(archive,self.root/'out',100)
 def test_sc117_bundle_shares_assets_and_keeps_quants_separate(self):
  quants=['IQ3_S','IQ3_XXS','IQ2_XS'];entries=p.download_entries(self.root,quants,True,'https://huggingface.co')
  self.assertEqual(sum(x['group']=='models' for u,x,target in entries),6);self.assertEqual(sum(x['group']=='mtp' for u,x,target in entries),4);self.assertEqual(sum(x['group']=='vision' for u,x,target in entries),1)
  self.assertEqual(len({target for u,x,target in entries}),len(entries))
  for u,x,target in entries:
   self.assertIn('SC117/',u);self.assertNotIn('unsloth',u.lower());self.assertTrue(target.is_relative_to(self.root.resolve()))
  self.assertEqual(p.bundle_size(quants)-p.bundle_size(quants[:2]),68465153504+1548226110)
 def test_generated_pack_receipt_catches_corruption_and_wrong_quant(self):
  quant='IQ3_XXS';folder=Path(p.deploy.asset_paths(self.root,quant)['pack']);files=[]
  for name in p.deploy.read(p.ROOT/'manifests/sc117-quants.json')['generated_pack_files']:
   f=folder/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(DATA);files.append({'group':'pack','path':name,'bytes':len(DATA),'sha256':hashlib.sha256(DATA).hexdigest()})
  receipt={'profile':'SC117-'+quant,'sources':[x for x in p.deploy.catalog(quant)['files'] if x['group']=='models'],'files':files};p.deploy.save(folder/'pack-manifest.json',receipt)
  self.assertTrue(p.group_ok('pack',self.root,p.deploy.catalog(quant)['files'],quant))
  (folder/'dense.bin').write_bytes(b'x'*len(DATA));self.assertFalse(p.group_ok('pack',self.root,p.deploy.catalog(quant)['files'],quant))
  receipt['profile']='SC117-IQ2_XS';p.deploy.save(folder/'pack-manifest.json',receipt)
  with self.assertRaises(ValueError):p.deploy.pack_items(folder,quant)
 def test_safe_source_url_does_not_log_credentials(self):
  text=p.safe_url('https://user:password@example.test:8443/model.gguf?token=secret')
  self.assertEqual(text,'https://example.test:8443/model.gguf');self.assertNotIn('password',text);self.assertNotIn('secret',text)
 def test_tls_certificate_failure_reports_reason_without_retry(self):
  import ssl
  error=ssl.SSLCertVerificationError(1,'certificate verify failed');error.verify_code=20;error.verify_message='unable to get local issuer certificate'
  f=self.root/'cert.gguf';part=f.with_name(f.name+'.part');part.write_bytes(b'ab')
  with patch.object(p,'open_url',side_effect=URLError(error)) as opening,redirect_stdout(io.StringIO()) as output:
   with self.assertRaises(RuntimeError) as e:p.fetch('https://example.test/model.gguf',f,len(DATA),hashlib.sha256(DATA).hexdigest())
  self.assertEqual(opening.call_count,1);self.assertIn('unable to get local issuer certificate',str(e.exception));self.assertIn('verify_code 20',output.getvalue());self.assertEqual(part.read_bytes(),b'ab');self.assertFalse(f.exists())
 def test_tls_context_keeps_verification_and_adds_extra_roots(self):
  import ssl,types,sys
  with patch.object(p,'CA_FILE',None):
   context=p.make_tls_context();self.assertEqual(context.verify_mode,ssl.CERT_REQUIRED);self.assertTrue(context.check_hostname)
  from unittest.mock import MagicMock
  context=MagicMock()
  with patch.object(p.ssl,'create_default_context',return_value=context),patch.dict(sys.modules,{'certifi':types.SimpleNamespace(where=lambda:'public-ca.pem')}),patch.object(p,'CA_FILE','custom-ca.pem'):
   self.assertIs(p.make_tls_context(),context)
  self.assertEqual([c.kwargs for c in context.load_verify_locations.call_args_list],[{'cafile':'public-ca.pem'},{'cafile':'custom-ca.pem'}])
 def test_timeout_reports_destination_and_keeps_partial(self):
  f=self.root/'timeout.gguf';part=f.with_name(f.name+'.part');part.write_bytes(b'ab')
  def fail(*args,**kwargs):
   p.LAST_HOST='blocked-cdn.example';raise URLError(TimeoutError('timed out'))
  with patch.object(p,'open_url',side_effect=fail),patch.object(p.time,'sleep'),redirect_stdout(io.StringIO()) as output:
   with self.assertRaises(RuntimeError) as e:p.fetch(self.url,f,len(DATA),hashlib.sha256(DATA).hexdigest())
  self.assertIn('blocked-cdn.example',str(e.exception));self.assertEqual(part.read_bytes(),b'ab');self.assertFalse(f.exists());self.assertIn('Connecting (attempt 1/3',output.getvalue())
if __name__=='__main__':unittest.main()