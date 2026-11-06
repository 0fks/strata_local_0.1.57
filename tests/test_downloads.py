import hashlib,http.server,importlib.util,io,tarfile,tempfile,threading,unittest
from pathlib import Path
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
if __name__=='__main__':unittest.main()