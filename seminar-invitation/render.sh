#!/usr/bin/env bash
# HTML maketlarni PNG'ga chiqaradi.
# Chromium headless oynasi pastdan biroz kesib qo'yadi — shu sabab zaxira balandlik
# bilan render qilinib, so'ng aniq o'lchamga qirqiladi va Lanczos bilan kichraytiriladi.
set -euo pipefail
cd "$(dirname "$0")"
CHROME=${CHROME:-/opt/pw-browsers/chromium-1194/chrome-linux/chrome}
SCALE=2
SLACK=200

render() { # $1=html $2=kenglik $3=balandlik $4=natija
  "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
    --force-device-scale-factor="$SCALE" --window-size="$2,$(( $3 + SLACK ))" \
    --virtual-time-budget=8000 --default-background-color=FFFFFFFF \
    --screenshot=/tmp/_render.png "file://$PWD/$1" >/dev/null 2>&1
  python3 -c "
from PIL import Image
s, w, h = $SCALE, $2, $3
im = Image.open('/tmp/_render.png').convert('RGB').crop((0, 0, w * s, h * s))
im.resize((w, h), Image.LANCZOS).save('$4')
print('$4', (w, h))"
}

mkdir -p out
render story-9x16.html 1080 1920 out/superai-seminar-story-1080x1920.png
render post-1x1.html   1080 1080 out/superai-seminar-post-1080x1080.png
