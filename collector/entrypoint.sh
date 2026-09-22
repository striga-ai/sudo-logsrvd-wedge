#!/bin/sh
# Pick the source build when it is present, otherwise the distribution's own binary.
if [ -x /opt/sudo-plain/sbin/sudo_logsrvd ]; then
    BIN=/opt/sudo-plain/sbin/sudo_logsrvd
else
    BIN=/usr/sbin/sudo_logsrvd
fi
echo "collector: $("$BIN" -V | head -1)  [$BIN]"
# LC_ALL=C keeps strlen(fmt) measured on the untranslated format strings, which is
# what fixes the trigger length at 937. Distribution builds ship translations.
exec env LC_ALL=C "$BIN" -n
