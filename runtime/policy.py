"""ROM Vector domain; rendered identically for split CIL and enforcing device tests."""
TYPES = {
 'ntvectord': ['domain', 'coredomain', 'mlstrustedsubject'],
 'ntvector_data_file': ['file_type', 'data_file_type', 'core_data_file_type', 'mlstrustedobject'],
 'xposed_file': ['file_type', 'mlstrustedobject'],
 'xposed_data': ['file_type', 'data_file_type', 'core_data_file_type', 'mlstrustedobject'],
 'zygisk_file': ['file_type', 'mlstrustedobject'],
}
ALLOWS = []
def allow(a,b,c,d): ALLOWS.append((a,b,c,d))
allow('init','ntvectord','process','transition siginh rlimitinh noatsecure')
allow('ntvectord','shell_exec','file','entrypoint')
allow('ntvectord','self','process','fork sigchld sigkill sigstop signull signal getsched setsched getpgid setpgid getcap setcap getrlimit setrlimit execmem setsockcreate')
allow('ntvectord','self','capability','chown dac_override dac_read_search fowner fsetid kill setgid setuid setpcap sys_ptrace sys_admin sys_chroot sys_resource')
allow('ntvectord','self','capability2','syslog')
for kind,perms in [('dir','search open read write getattr add_name remove_name'),('file','open read write getattr map execute execute_no_trans'),('lnk_file','read getattr'),('fd','use'),('fifo_file','read write getattr'),('anon_inode','create read write ioctl'),('unix_stream_socket','create connect bind listen accept read write getattr getopt setopt shutdown connectto'),('unix_dgram_socket','create connect bind read write getattr getopt setopt sendto')]:
 allow('ntvectord','self',kind,perms)
allow('ntvectord','file_type','dir','search getattr')
for kind,perms in [('dir','search getattr open read'),('file','read open getattr map execute execute_no_trans'),('lnk_file','read getattr')]:
 allow('ntvectord','system_file_type',kind,perms)
allow('ntvectord','property_type','file','read open getattr map')
for target in ['ntvector_data_file','xposed_file','xposed_data']:
 for kind,perms in [('dir','create search open read write add_name remove_name getattr setattr relabelfrom relabelto rmdir'),('file','create open read write append getattr setattr unlink lock map execute execute_no_trans relabelfrom relabelto'),('lnk_file','create read getattr unlink'),('sock_file','create read write getattr setattr unlink')]:
  allow('ntvectord',target,kind,perms)
 allow('init',target,'dir','create search open read write add_name remove_name getattr setattr relabelfrom relabelto')
allow('ntvectord','zygisk_file','sock_file','create read write getattr setattr unlink')
for target in ['null_device','random_device','binder_device','hwbinder_device','vndbinder_device']:
 allow('ntvectord',target,'chr_file','open read write getattr ioctl map')
for target in ['proc_type','sysfs_type']:
 for kind,perms in [('dir','search open read getattr'),('file','open read getattr'),('lnk_file','read getattr')]: allow('ntvectord',target,kind,perms)
for target in ['init','zygote']:
 allow('ntvectord',target,'process','ptrace signal sigkill sigstop signull getsched setsched getcap setcap')
 for kind,perms in [('dir','search open read getattr'),('file','open read write getattr map'),('lnk_file','read getattr'),('fd','use')]:allow('ntvectord',target,kind,perms)
allow('ntvectord','proc','file','open read write getattr')
allow('ntvectord','tmpfs','file','create open read write getattr map execute unlink')
allow('ntvectord','tmpfs','dir','search write add_name remove_name mounton')
allow('ntvectord','tmpfs','filesystem','mount unmount getattr')
allow('ntvectord','system_file','file','mounton relabelfrom relabelto')
allow('ntvectord','dex2oat_exec','file','mounton open read getattr relabelfrom relabelto')
allow('ntvectord','system_file','dir','write add_name remove_name mounton')
allow('ntvectord','system_data_file','dir','create search open read write add_name remove_name getattr setattr relabelfrom relabelto')
allow('ntvectord','system_data_file','file','create open read write getattr setattr unlink lock')
allow('ntvectord','apk_data_file','dir','search open read getattr')
allow('ntvectord','apk_data_file','file','open read getattr map')
allow('ntvectord','selinuxfs','file','open read write getattr')
allow('ntvectord','kernel','security','compute_av check_context')
allow('ntvectord','servicemanager','binder','call transfer')
allow('ntvectord','domain','binder','call transfer')
allow('domain','ntvectord','binder','call transfer')
allow('domain','ntvectord','fd','use')
allow('ntvectord','service_manager_type','service_manager','find')
allow('ntvectord','serial_service','service_manager','add')
allow('ntvectord','init','fd','use')
allow('ntvectord','logd','unix_dgram_socket','sendto')
allow('ntvectord','logdw_socket','sock_file','write')
allow('ntvectord','logdr_socket','sock_file','write')
allow('ntvectord','logd','unix_stream_socket','connectto')
allow('ntvectord','logd','fd','use')
# Zygisk creates a socket with the zygote SID; Vector's dex2oat socket uses dex2oat SID.
for target in ['zygote','dex2oat']:
 allow('ntvectord',target,'unix_stream_socket','create bind listen accept read write getattr getopt setopt shutdown')
 allow(target,'ntvectord','unix_stream_socket','connectto')
 allow(target,'ntvectord','fd','use')
allow('zygote','ntvector_data_file','dir','search getattr')
allow('zygote','zygisk_file','sock_file','read write')
allow('zygote','zygote','capability','sys_chroot')
allow('zygote','zygote','process','execmem')
allow('system_server','system_server','process','execmem')
for target in ['tmpfs','appdomain_tmpfs']:allow('zygote',target,'file','open read write getattr map execute')
for target in ['proc']:allow('zygote',target,'file','open read getattr')
allow('dex2oat','dex2oat_exec','file','execute_no_trans')
allow('dex2oat','system_linker_exec','file','execute_no_trans')
allow('zygote','dex2oat','unix_stream_socket','connectto')
for source in ['dex2oat','installd','isolated_app','shell','zygote','system_server']:
 for kind,perms in [('dir','search open read getattr'),('file','open read write getattr map execute execute_no_trans')]:allow(source,'xposed_file',kind,perms)
for source in ['appdomain','system_server']:
 allow(source,'xposed_data','dir','search open read write getattr add_name remove_name')
 allow(source,'xposed_data','file','create open read write getattr setattr unlink lock map')
allow('system_server','apk_data_file','file','execute')

# init children change domain at exec while the monitor observes the fork event.
allow('ntvectord','domain','process','ptrace')
allow('ntvectord','system_file','dir','create search open read write getattr setattr add_name remove_name relabelfrom relabelto')
allow('ntvectord','system_file','file','create open read write getattr setattr append unlink lock map')

for kind,perms in [('dir','search open read getattr'),('file','open read getattr'),('lnk_file','read getattr')]:allow('ntvectord','domain',kind,perms)
allow('ntvectord','ntvector_data_file','sock_file','relabelfrom relabelto')
allow('ntvectord','zygisk_file','sock_file','relabelfrom relabelto')

allow('ntvectord','self','file','create write')
allow('ntvectord','self','process','getattr')
allow('ntvectord','zygote','unix_stream_socket','connectto')

allow('ntvectord','adb_data_file','dir','create search open read write getattr setattr add_name remove_name')
allow('ntvectord','proc','filesystem','associate')


allow('ntvectord','self','process','setfscreate')
allow('ntvectord','labeledfs','filesystem','remount')
allow('ntvectord','system_file','sock_file','create read write getattr setattr unlink')
allow('ntvectord','kmsg_device','chr_file','open read getattr')
allow('system_server','ntvectord','fifo_file','read write getattr')

allow('ntvectord','selinuxfs','dir','search open read getattr')
allow('ntvectord','self','fifo_file','ioctl')
allow('ntvectord','self','process','setcurrent')
allow('ntvectord','labeledfs','filesystem','unmount')
allow('ntvectord','kernel','system','syslog_read')
allow('ntvectord','ntvector_data_file','dir','rename reparent')
allow('ntvectord','system_file','dir','rename reparent')

allow('ntvectord','unlabeled','file','open read getattr')
allow('ntvectord','selinuxfs','file','map')

allow('ntvectord','xposed_file','dir','rename reparent')

# Manager and scoped apps receive read-only APK/DEX descriptors from the daemon.
allow('appdomain','xposed_file','file','open read getattr map execute')

for target in ['ntvector_data_file','xposed_file']:allow('ntvectord',target,'file','rename')

for target in ['ntvector_data_file','system_file','xposed_file']:
 for kind in ['sock_file','lnk_file']:allow('ntvectord',target,kind,'relabelfrom relabelto')

allow('ntvectord','dex2oat_exec','file','unlink rename setattr')

# /data/adb is restored by the base ROM before our post-fs-data action.
# Migrate Vector's existing config labels before opening its database.
allow('ntvectord','adb_data_file','dir','relabelfrom')
allow('ntvectord','adb_data_file','file','open read getattr relabelfrom')

def cil():
 lines=[]
 for name,attrs in TYPES.items():
  lines += [f'(type {name})',f'(roletype {"r" if "domain" in attrs else "object_r"} {name})']
  lines += [f'(typeattributeset {attr} ({name}))' for attr in attrs]
 for a,b,c,d in ALLOWS:lines.append(f'(allow {a} {a if b=="self" else b} ({c} ({d})))')
 return '\n'.join(lines)+'\n'

def live():
 lines=[]
 for name,attrs in TYPES.items():
  lines += [f'type {name} {attrs[0]}']+[f'typeattribute {name} {attr}' for attr in attrs[1:]]
 for a,b,c,d in ALLOWS:
  lines += [f'allow {a} {a if b=="self" else b} {c} {perm}' for perm in d.split()]
 return '\n'.join(lines)+'\n'
