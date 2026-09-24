#!/bin/sh
set -eu

fc-cache -f
font_family="$(fc-match -f '%{family[0]}' 'Gill Sans' 2>/dev/null || true)"
case "$font_family" in
    *"Gill Sans"*)
        ;;
    *)
        echo "ERROR: Gill Sans is not installed in the container. Add licensed font files to ./fonts." >&2
        echo "Resolved font: ${font_family:-none}" >&2
        exit 1
        ;;
esac

exec "$@"