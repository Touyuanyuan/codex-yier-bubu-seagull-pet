from pathlib import Path
import json, stat, zipfile
ROOT=Path(__file__).resolve().parents[1]
COMMON=['README.md','preview.html','install.html','install-link.txt','LICENSE','ASSET-NOTICE.md','CREDITS.md','CHANGELOG.md','pet/pet.json','pet/spritesheet.webp']
COMMON += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'docs').glob('*')) if p.is_file()]
def build():
    pet=json.loads((ROOT/'pet/pet.json').read_text(encoding='utf-8'))
    assert pet['id']=='yier-bubu-handholding-seagull' and pet['spriteVersionNumber']==2
    out=ROOT.parent/'artifacts';out.mkdir(exist_ok=True)
    results=[]
    for platform,scripts in [('windows',['install.cmd','install.ps1','install-in-codex.url']),('macos',['install.command','install.sh'])]:
        prefix=f'codex-yier-bubu-seagull-pet-v1.0.0-{platform}'
        dest=out/(prefix+'.zip')
        with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
            for name in COMMON+scripts:
                data=(ROOT/name).read_bytes();executable=name in ['install.sh','install.command']
                if executable: data=data.replace(b'\r\n',b'\n');assert data.startswith(b'#!/bin/bash\n')
                info=zipfile.ZipInfo(prefix+'/'+name);info.create_system=3
                info.external_attr=(stat.S_IFREG | (0o755 if executable else 0o644))<<16
                z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED)
        with zipfile.ZipFile(dest) as z:
            for name in ['pet/pet.json','pet/spritesheet.webp']: assert z.read(prefix+'/'+name)==(ROOT/name).read_bytes()
            if platform=='macos':
                for name in scripts:
                    assert (z.getinfo(prefix+'/'+name).external_attr>>16)&0o777==0o755
                    assert b'\r' not in z.read(prefix+'/'+name)
        results.append({'platform':platform,'file':str(dest),'bytes':dest.stat().st_size,'files':len(COMMON+scripts)})
    print(json.dumps(results,ensure_ascii=False,indent=2));return results
if __name__=='__main__': build()
