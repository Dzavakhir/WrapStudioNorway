# SUPER AI — jonli seminar taklifnomasi

Javohir Mamatqulov va Zilola Saidqulova ishtirokidagi jonli seminar uchun
ikkita post: Instagram Stories (9:16) va lenta uchun kvadrat post (1:1).

Uslub: minimalistik zamonaviy — oq fon, qora qizil (`#8E1116`) va toʻq
olovrang (`#C2401B`) urgʻu ranglari, Space Grotesk + Inter shriftlari.

## Natijalar

| Fayl | Oʻlcham | Nima uchun |
| --- | --- | --- |
| `out/superai-seminar-story-1080x1920.png` | 1080×1920 | Instagram / Telegram stories |
| `out/superai-seminar-post-1080x1080.png` | 1080×1080 | Instagram lenta posti |

Har ikkalasida ham ishtirokchi uchun toʻldiriladigan joy bor: **ism, familiya**,
**oʻrindiq raqami** va **qator**.

## Tuzilishi

```
story-9x16.html      9:16 maket
post-1x1.html        1:1 maket
assets/style.css     umumiy stil (ranglar, tipografika, bloklar)
assets/fonts.css     mahalliy shriftlar (assets/fonts/*.woff2)
assets/speaker1.png  Javohir Mamatqulov — foni olib tashlangan
assets/speaker2.png  Zilola Saidqulova — foni olib tashlangan
assets/speakers-pair.png  ikkalasi bitta jamoa sifatida
build_pair.py        juftlik kompozitsiyasini yigʻadi
render.sh            HTML → PNG
```

## Spikerlar rasmi

Ikki rasm turli fonda (biri toʻq olovrang studiya, ikkinchisi oq devor) suratga
olingan. Ular bitta jamoadek koʻrinishi uchun:

1. `rembg` (isnet-general-use, alpha matting) bilan fon olib tashlangan;
2. `build_pair.py` boshlar kengligini bir xil qilib, koʻz chizigʻi boʻyicha
   tekislaydi;
3. yelkalar orasidagi boʻshliq har bir qator boʻyicha hisoblanib, ikkalasi
   yonma-yon qoʻyiladi;
4. pastki qirrasi shaffoflikka silliq oʻtadi, shunda oq fonga qorishib ketadi.

Rasm yoki oʻlchamlar oʻzgarsa, `build_pair.py` ichidagi `SPEAKERS` roʻyxatidagi
koʻz chizigʻi va bosh kengligi qiymatlarini yangilash kerak.

## Qayta chiqarish

```bash
pip install pillow rembg onnxruntime   # faqat kesish uchun kerak
python3 build_pair.py                  # spikerlar juftligini yigʻish
./render.sh                            # PNG'larni chiqarish
```

`render.sh` Chromium'ni 2x masshtabda ishlatib, soʻng Lanczos bilan aniq
oʻlchamga keltiradi. Chromium yoʻli `CHROME` oʻzgaruvchisi orqali beriladi.

Matnni oʻzgartirish uchun HTML fayllardagi soʻzlarni tahrirlab, `./render.sh`
ni qayta ishga tushirish kifoya.
