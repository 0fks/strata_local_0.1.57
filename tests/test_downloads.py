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
 def test_modelscope_paths_and_generated_pack_corruption(self):
  manifest=p.deploy.read(p.ROOT/'manifests/assets.json');pins=[x for x in manifest['files'] if x['group']=='models'];self.assertEqual(len(pins),4)
  for x in pins:
   url=p.model_url('https://www.modelscope.cn',x['group'],x['path']);self.assertIn('/models/unsloth/',url);self.assertIn('/UD-IQ3_XXS/',url);self.assertNotIn('huggingface',url)
  folder=self.root/'pack';files=[]
  for name in manifest['generated_pack_files']:
   f=folder/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(DATA);files.append({'group':'pack','path':name,'bytes':len(DATA),'sha256':hashlib.sha256(DATA).hexdigest()})
  p.deploy.save(folder/'pack-manifest.json',{'profile':manifest['profile'],'sources':pins,'files':files});self.assertTrue(p.group_ok('pack',self.root,manifest['files']))
  (folder/'dense.bin').write_bytes(b'x'*len(DATA));self.assertFalse(p.group_ok('pack',self.root,manifest['files']))
 def test_safe_source_url_does_not_log_credentials(self):
  text=p.safe_url('https://user:password@example.test:8443/model.gguf?token=secret')
  self.assertEqual(text,'https://example.test:8443/model.gguf');self.assertNotIn('password',text);self.assertNotIn('secret',text)
 def test_timeout_reports_destination_and_keeps_partial(self):
  f=self.root/'timeout.gguf';part=f.with_name(f.name+'.part');part.write_bytes(b'ab')
  def fail(*args,**kwargs):
   p.LAST_HOST='blocked-cdn.example';raise URLError(TimeoutError('timed out'))
  with patch.object(p,'open_url',side_effect=fail),patch.object(p.time,'sleep'),redirect_stdout(io.StringIO()) as output:
   with self.assertRaises(RuntimeError) as e:p.fetch(self.url,f,len(DATA),hashlib.sha256(DATA).hexdigest())
  self.assertIn('blocked-cdn.example',str(e.exception));self.assertEqual(part.read_bytes(),b'ab');self.assertFalse(f.exists());self.assertIn('Connecting (attempt 1/3',output.getvalue())
if __name__=='__main__':unittest.main()