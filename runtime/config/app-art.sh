#!/system/bin/sh
# Keep compiler-service wrappers out of app Zygote mount namespaces.
# Apps use original ART; Vector's selected module hooks remain independent.
set -eu
base=/data/misc/ntlsposed
[ ! -f "$base/disable" ] || exit 0
[ -f "$base/prepared" ] || exit 0
[ "$(cat "$base/prepared")" = "$(cat /proc/sys/kernel/random/boot_id)" ] || exit 0
wrapper_mounts() {
    awk '$5 ~ /^\/apex\/com[.]android[.](art|runtime)\/bin\/dex2oat(d)?(32|64)?$/ && ($4 == "/misc/ntlsposed/modules/zygisk_vector/bin/dex2oat32" || $4 == "/misc/ntlsposed/modules/zygisk_vector/bin/dex2oat64" || $4 == "/data/misc/ntlsposed/modules/zygisk_vector/bin/dex2oat32" || $4 == "/data/misc/ntlsposed/modules/zygisk_vector/bin/dex2oat64") {print $5}' "$1"
}
if [ "${1:-}" = local ]; then
    # Never remove the compiler-service mounts in init's namespace.
    [ "$(readlink /proc/self/ns/mnt)" != "$(readlink /proc/1/ns/mnt)" ] || exit 1
    targets=$(wrapper_mounts /proc/self/mountinfo)
    for target in $targets; do umount "$target"; done
    [ -z "$(wrapper_mounts /proc/self/mountinfo)" ] || exit 1
    [ -z "$targets" ] || log -t NTVector 'Original ART restored in app Zygote namespace'
    exit 0
fi
# Startup and Zygote restarts can overlap with secondary Zygote creation.
# This asynchronous worker is bounded and never blocks init's boot actions.
n=0
while [ "$n" -lt 12 ]; do
    if [ -n "$(wrapper_mounts /proc/1/mountinfo)" ]; then
        for pid in $(pidof zygote64 zygote zygote_tango zygote_next || true); do
            [ -r "/proc/$pid/ns/mnt" ] || continue
            # A vendor compiler/preloader can share init's namespace; leave it alone.
            if [ "$(readlink /proc/$pid/ns/mnt)" = "$(readlink /proc/1/ns/mnt)" ]; then
                continue
            fi
            [ -n "$(wrapper_mounts /proc/$pid/mountinfo)" ] || continue
            if ! nsenter -t "$pid" -m -- /system/bin/sh "$0" local; then
                log -p w -t NTVector "App ART namespace not ready for Zygote $pid"
            fi
        done
    fi
    n=$((n+1))
    sleep 0.5
done
