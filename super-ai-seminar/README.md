# SUPER AI — jonli seminar taklifnomasi

Javohir Mamatqulov va Zilola Saidqulova ishtirokidagi jonli seminar uchun ikkita
ijtimoiy tarmoq posti. Uslub: minimalistik, zamonaviy; palitra — to'q qizil
(burgundi) va olovrang urg'u, oq rang juda kam ishlatilgan.

## Tayyor fayllar

| Fayl | O'lcham | Qayerga |
| --- | --- | --- |
| `out/story_1080x1920.png` | 1080×1920 (9:16) | Instagram Stories |
| `out/post_1080x1080.png` | 1080×1080 (1:1) | Instagram feed posti |

Ikkalasida ham taklifnoma maydonlari bor: **ism, familiya** uchun chiziq,
**o'rindiq raqami** va **qator** uchun katakchalar.

## Dizayn tizimi

- Fon: `#1B0407` → `#470B13` gradient, markazda iliq olovrang yorug'lik, ustidan
  yengil "grain" tekstura.
- Urg'u rangi: `#FF7A3C` / `#E2481A`; matn: iliq krem `#F2DED4` va so'lg'un
  `#C58C7E`.
- Shriftlar: sarlavhalar — Montserrat 900, matn — Inter.
- Orqa fonda kontur bilan yozilgan katta `SUPER AI` yozuvi brend elementi
  sifatida ishlatilgan.

## Spikerlar rasmi

Ikkala rasm bir-biriga moslashtirilib, bitta jamoa kadriga birlashtirilgan:

1. Fon `rembg` (birefnet-portrait modeli) yordamida olib tashlangan →
   `design/assets/sp1_cut.png`, `sp2_cut.png`.
2. `design/compose.py` alfa maskasidan bosh va yelka chiziqlarini o'lchaydi,
   so'ng:
   - bosh o'lchamlarini tenglashtiradi (ikkalasi bir xil razmerda),
   - yelkalarni bitta gorizontal chiziqqa qo'yadi,
   - ayol spikerni belidan pastda kesadi,
   - ortiqcha bo'sh joyni kesib, ikkalasini bir-biriga yaqinlashtiradi
     (yengil ustma-ust).
3. `design/grade.py` ikkalasiga bir xil iliq burgundi duoton grading beradi va
   alfa kanalini tozalaydi.

Natija — bitta fayl: `design/assets/crew_pair.png`.

## Qayta render qilish

```bash
cd design
python3 compose.py               # spikerlar juftligini qayta yig'ish
node shot.js                     # HTML → PNG (playwright kerak)
```

`shot.js` tizimdagi Chromium'ni ishlatadi; boshqa binarni ko'rsatish uchun
`CHROMIUM_PATH` muhit o'zgaruvchisini bering.

Matnni o'zgartirish uchun `design/story.html` va `design/post.html`
fayllaridagi matn bloklarini tahrirlab, `node shot.js` ni qayta ishga tushiring.
