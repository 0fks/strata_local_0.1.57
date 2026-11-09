"""Export a Strata-only entry for OpenCode's singular provider config."""
import argparse,json,os,sys
from pathlib import Path

def convert(client):
    if 'strata' in client.get('provider',{}):return {'provider':{'strata':client['provider']['strata']}}
    source=client.get('providers',{}).get('strata')
    if not isinstance(source,dict):raise ValueError('No Strata provider in the generated client JSON')
    models={}
    for mid,model in source.get('models',{}).items():
        caps=model.get('capabilities',{})
        item={'name':model.get('name',mid),'tool_call':caps.get('tools',True),'modalities':{'input':caps.get('input',['text']),'output':caps.get('output',['text'])},'limit':dict(model.get('limit',{}))}
        field=model.get('compatibility',{}).get('reasoningField')
        if field:item['interleaved']={'field':field}
        models[mid]=item
    if not models:raise ValueError('No explicit Strata models in the generated client JSON')
    return {'provider':{'strata':{'npm':'@ai-sdk/openai-compatible','name':source.get('name','Strata Local'),'options':dict(source.get('settings',{})),'models':models}}}

def write_exports(client_path):
    client_path=Path(client_path);fragment=convert(json.loads(client_path.read_text(encoding='utf-8-sig')))
    files={client_path.parent/'provider.json':json.dumps(fragment,ensure_ascii=False,indent=2)+'\n',client_path.parent/'provider-entry.txt':json.dumps(fragment['provider'],ensure_ascii=False,indent=2)[2:-2]+'\n'}
    for path,text in files.items():
        temp=path.with_name(path.name+'.tmp');temp.write_text(text,encoding='utf-8');os.replace(temp,path)
    return list(files)

def export_root(root):
    root=Path(root).resolve();written=[]
    for mode in ('Local','LAN'):
        source=root/'clients'/mode/'opencode.json'
        if source.is_file():written.extend(write_exports(source))
    if not written:raise ValueError('Generated client JSON not found under the selected runtime/clients folder')
    return written

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);a=ap.parse_args()
    for path in export_root(a.root):print('Created: '+str(path))
    print('Paste provider-entry.txt INSIDE the existing config.json provider object. Keep the existing schema, other providers and MCP. Files contain API keys; do not publish them.')
if __name__=='__main__':
    try:main()
    except Exception as exc:print('ERROR: '+str(exc),file=sys.stderr);sys.exit(1)
