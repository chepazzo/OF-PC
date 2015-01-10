#! /bin/sh

main() {
    if init_is_upstart; then
        echo 'upstart'
        exit 0
    fi
    if init_is_lsb; then
        echo 'lsb'
        exit 0
    fi
    if init_is_systemd; then
        echo 'systemd'
        exit 0
    fi
}

init_is_lsb() {
    if test -f /lib/lsb/init-functions; then
        return 1
    fi
    return 0
}

init_is_upstart() {
   if [ -x /sbin/initctl ] && /sbin/initctl version 2>/dev/null | /bin/grep -q upstart; then
       return 0
   fi
   return 1
}

init_is_systemd() {
    if [ -x /usr/sbin/systemctl ]; then
        return 1
    fi
    return 0
}

main
exit 0
