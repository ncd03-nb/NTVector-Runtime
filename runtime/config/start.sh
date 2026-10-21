#!/system/bin/sh
# Only init starts this root-owned service. Module APKs are managed by Vector.
set -eu
code=/system_ext/etc/ntvector
base=/data/misc/ntlsposed
module=/data/misc/ntlsposed/modules/zygisk_vector
compat=/data/adb/modules/zygisk_vector
boot_id=$(cat /proc/sys/kernel/random/boot_id)
[ ! -f "$base/disable" ] || exit 0
ready() { [ -f "$base/prepared" ] && [ "$(cat "$base/prepared")" = "$boot_id" ]; }
case "${1:-}" in
 prepare)
    rm -f "$base/prepared"
    cd "$code"
    sha256sum -c SHA256SUMS >/dev/null || { log -p e -t NTVector 'Payload verification failed; skipped'; exit 1; }
    if [ -e "$module" ] && [ ! -f "$module/.nt-rom-owned" ]; then
        log -p w -t NTVector 'User-owned Vector installation exists; ROM loader skipped'
        exit 0
    fi
    # A previous ROM-owned module stays disabled in the root manager. Its scripts
    # and native Zygisk entry are never used by the ROM loader.
    if [ -f "$compat/module.prop" ] && [ ! -f "$compat/.nt-rom-owned" ]; then
        log -p w -t NTVector 'Separate user Vector installation exists; ROM startup skipped'
        exit 0
    fi
    mkdir -p "$base/modules" "$base/runtime/lib64" "$base/loader/bin" "$compat/bin"
    # Fresh /data/adb directories inherit adb_data_file, which the daemon must
    # not receive general file-write access to. Relabel only these owned dirs
    # before creating disable or copying the two upstream compatibility libs.
    chcon u:object_r:xposed_file:s0 "$compat" "$compat/bin"
    touch "$compat/disable"
    # Only these two upstream hardcoded compatibility paths are needed.
    cp "$code/dist/vector/bin/liboat_hook32.so" "$compat/bin/liboat_hook32.so"
    cp "$code/dist/vector/bin/liboat_hook64.so" "$compat/bin/liboat_hook64.so"
    chcon u:object_r:xposed_file:s0 "$compat/bin/liboat_hook32.so" "$compat/bin/liboat_hook64.so"
    chmod 0700 "$base"
    cp "$code/dist/runtime/lib64/libzygisk.so" "$base/runtime/lib64/libzygisk.so.new"
    mv "$base/runtime/lib64/libzygisk.so.new" "$base/runtime/lib64/libzygisk.so"
    cp "$code/dist/loader/bin/zygisk-ptrace64" "$base/loader/bin/zygisk-ptrace64"
    cp "$code/dist/loader/bin/zygiskd64" "$base/loader/bin/zygiskd64"
    cp "$code/dist/loader/module.prop" "$base/loader/module.prop"
    keep_disabled=false
    [ ! -f "$module/disable" ] || keep_disabled=true
    # This exact directory is owned only by this installer and is never app-writable.
    rm -rf /data/misc/ntlsposed/vector-stage
    mkdir /data/misc/ntlsposed/vector-stage
    cp -R "$code/dist/vector/." /data/misc/ntlsposed/vector-stage/
    chown -R 0:0 /data/misc/ntlsposed/vector-stage
    chmod -R u+rwX,go+rX /data/misc/ntlsposed/vector-stage
    chmod 0755 /data/misc/ntlsposed/vector-stage/bin/* /data/misc/ntlsposed/vector-stage/cli
    rm -rf /data/misc/ntlsposed/vector-previous
    if [ -e "$module" ]; then mv "$module" /data/misc/ntlsposed/vector-previous; fi
    mv /data/misc/ntlsposed/vector-stage "$module"
    [ "$keep_disabled" = false ] || touch "$module/disable"
    chcon -R u:object_r:xposed_file:s0 "$module" "$base/loader/bin" "$base/runtime/lib64"
    chmod 0755 "$base/loader/bin/"*
    rm -f "$base/runtime/init_monitor" "$base/runtime/cp64.sock"
    mkdir -p /data/adb/lspd
    chcon -R u:object_r:ntvector_data_file:s0 /data/adb/lspd
    printf '%s' "$boot_id" > "$base/prepared"
    ;;
 monitor)
    ready || exit 0
    cd "$base/loader"
    exec ./bin/zygisk-ptrace64 monitor
    ;;
 ready)
    ready || exit 0
    # This bounded wait completes before init starts Zygote.
    n=0
    while [ ! -S "$base/runtime/init_monitor" ] && [ "$n" -lt 50 ]; do
        sleep 0.1
        n=$((n+1))
    done
    [ -S "$base/runtime/init_monitor" ] || rm -f "$base/prepared"
    ;;
 daemon)
    ready || exit 0
    cd "$module"
    exec /system/bin/app_process -Djava.class.path=/data/misc/ntlsposed/modules/zygisk_vector/daemon.apk /system/bin --nice-name=vectord org.matrix.vector.daemon.VectorDaemon --system-server-max-retry=0
    ;;
 *) exit 2 ;;
esac
