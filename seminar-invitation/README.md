# SUPER AI — jonli seminar taklifnomasi

Javohir Mamatqulov va Zilola Saidqulova ishtirokidagi jonli seminar uchun
ikkita post: Instagram Stories (9:16) va lenta uchun kvadrat post (1:1).

Uslub: minimalistik zamonaviy — oq fon, qora qizil (`#8E1116`) va toʻq
olovrang (`#C2401B`) urgʻu ranglari, Space Grotesk + Inter shriftlari.
Spikerlar hech qanday ramkasiz, toʻgʻridan-toʻgʻri oq fonda turadi; pastdagi
qora qizil lenta ishtirokchi maʼlumotlarini oʻz ichiga oladi va figuralarni
tagidan kesib turadi.

## Natijalar

| Fayl | Oʻlcham | Nima uchun |
| --- | --- | --- |
| `out/superai-seminar-story-1080x1920.png` | 1080×1920 | Instagram / Telegram stories |
| `out/superai-seminar-post-1080x1080.png` | 1080×1080 | Instagram lenta posti |
| `out/*@2x.png` | 2160×3840 / 2160×2160 | retina / chop etish uchun toʻliq oʻlcham |

Har ikkalasida ham ishtirokchi uchun toʻldiriladigan joy bor: **ism, familiya**,
**oʻrindiq raqami** va **qator**.

## Tuzilishi

```
story-9x16.html            9:16 maket
post-1x1.html              1:1 maket
assets/style.css           umumiy stil (ranglar, tipografika, bloklar)
assets/fonts.css           mahalliy shriftlar (Inter, Inter Tight — assets/fonts/*.woff2)
assets/speaker1.png        Javohir Mamatqulov — foni olib tashlangan (x1)
assets/speaker2.png        Zilola Saidqulova — foni olib tashlangan (x1)
assets/speaker1-graded.png  retush + rang korreksiyasidan keyin
assets/speaker2-graded.png  x2 apskeyl + kesish + rang korreksiyasidan keyin
assets/speakers-pair.png   ikkalasi bitta jamoa sifatida
upscale.py                 EDSR x2 apskeyl (OpenCV dnn_superres)
cutout.py                  rembg bilan fonni olib tashlash
retouch.py                 kepkadagi begona brend yozuvini olib tashlash
grade.py                   qirralarni tozalash + ikki suratni bir yorugʻlikka keltirish
build_pair.py              juftlik kompozitsiyasini yigʻadi
render.sh                  HTML → PNG (1x va 2x)
```

`assets/src/` (model fayli, apskeyl natijalari) git'ga kirmaydi — `.gitignore`.

## Spikerlar rasmi

Ikki rasm turli fonda va turli yorugʻlikda (biri toʻq olovrang studiya,
ikkinchisi oq devor) suratga olingan. Ular bitta seansda olingandek koʻrinishi
uchun toʻliq pipeline:

1. **Apskeyl.** Zilolaning surati 1178 px — 2x eksport uchun EDSR x2 bilan
   2356 px ga kattalashtirilgan (`upscale.py`). Javohirning 1706 px surati
   yetarli.
2. **Kesish.** `rembg` isnet-general-use + alpha matting (`cutout.py`).
3. **Retush.** Kepkadagi begona brend yozuvi olib tashlangan: yozuv konturi
   boʻyicha yaxlit maska, NS-inpaint, mato donadorligi qaytarilgan
   (`retouch.py`).
4. **Rang korreksiyasi** (`grade.py`, oʻlchovlar asosida): Javohirning oq
   futbolkasi boʻyicha oq balans (R 0.934 / B 1.032), yorqinlik gamma 0.787,
   yengil keskinlashtirish; Zilolada gamma 1.19, kontrast 0.88, oq kurtka
   himoyalangan. Natijada ikkalasining teri toni 3.5 L va 0.06 R/G ichida.
   Yarim shaffof qirralar toza rang bilan toʻldirilgan, mayda orolchalar
   olib tashlangan, Zilolaning yumshoq maskasi 1.6 px choke qilingan.
5. **Juftlik** (`build_pair.py`): boshlar bir xil kenglikda, koʻz chizigʻi
   bir xil, boshlar markazlari `HEAD_GAP` masofada — yelkalar tegib turadi.
   Javohirning tirsagi toʻliq saqlanadi, shuning uchun kvadrat postda qoʻli
   tabiiy tugaydi, storisda kadrdan chiqib ketadi. Qoʻllar qizil lenta
   orqasida qoladi.

Rasm yoki oʻlchamlar oʻzgarsa, `build_pair.py` ichidagi `SPEAKERS` roʻyxatidagi
koʻz chizigʻi va bosh kengligi qiymatlarini yangilash kerak. Ikkovi orasidagi
zichlikni `HEAD_GAP`, chetdagi joyni `SIDE` boshqaradi.

## Qayta chiqarish

```bash
pip install pillow numpy rembg onnxruntime opencv-contrib-python-headless
python3 upscale.py <asl-zilola.jpg> assets/src/speaker2-x2.png     # EDSR_x2.pb kerak
python3 cutout.py assets/src/speaker2-x2.png assets/src/speaker2-x2-cut.png
python3 retouch.py assets/speaker1.png assets/src/speaker1-retouched.png
python3 grade.py assets/src/speaker1-retouched.png assets/speaker1-graded.png --profile man
python3 grade.py assets/src/speaker2-x2-cut.png assets/speaker2-graded.png --profile woman --alpha-sigma 2.0 --erosion 1.6
python3 build_pair.py
./render.sh
```

`render.sh` Chromium'ni 2x masshtabda ishlatib, soʻng Lanczos bilan aniq
oʻlchamga keltiradi. Chromium yoʻli `CHROME` oʻzgaruvchisi orqali beriladi.

Matnni oʻzgartirish uchun HTML fayllardagi soʻzlarni tahrirlab, `./render.sh`
ni qayta ishga tushirish kifoya.
