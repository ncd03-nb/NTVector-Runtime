"""Rebuild NeoZygisk's ROM mode from the pinned patched source (Linux/WSL)."""
import argparse,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--sdk',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
root=a.source.resolve();sdk=a.sdk.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
ndk=sdk/'ndk/30.0.16248370';cmake=sdk/'cmake/3.31.6/bin/cmake';ninja=sdk/'cmake/3.31.6/bin/ninja'
env=os.environ.copy();env.update(ANDROID_NDK_HOME=str(ndk),MIN_APATCH_VERSION='10762',MIN_KSU_VERSION='10940',MAX_KSU_VERSION='30000',MIN_MAGISK_VERSION='26402',ZKSU_VERSION='nt-rom-1')
def run(v,cwd=None):subprocess.run([str(x) for x in v],env=env,cwd=cwd,check=True)
build=out/'native-arm64-v8a'
run([cmake,'-S',root/'loader/src','-B',build,'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+str(ninja),'-DCMAKE_TOOLCHAIN_FILE='+str(ndk/'build/cmake/android.toolchain.cmake'),'-DANDROID_ABI=arm64-v8a','-DANDROID_PLATFORM=android-26','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS=-DWORK_DIRECTORY=\\\"/data/misc/ntlsposed/runtime\\\"','-DZKSU_VERSION=nt-rom-1'])
run([cmake,'--build',build,'-j','8'])
run(['cargo','ndk','--platform','26','-t','arm64-v8a','build','--release','--features','rom','--target-dir',out/'rust-target'],root/'zygiskd')
