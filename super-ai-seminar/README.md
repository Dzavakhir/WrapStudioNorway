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

Ikkala rasm bir-biriga moslashtirilgan, ya'ni bitta jamoa bo'lib ko'rinadi:

1. Fon `rembg` (birefnet-portrait modeli) yordamida olib tashlangan →
   `design/assets/sp1_cut.png`, `sp2_cut.png`.
2. `design/grade.py` ikkala kesimga bir xil iliq burgundi duoton grading beradi,
   alfa kanalini tozalaydi va yorug'lik darajasini tenglashtiradi →
   `sp1_g.png`, `sp2_g2.png`.
3. Kompozitsiyada bosh o'lchamlari tenglashtirilib, ikkalasi bitta "pol"
   chizig'iga qo'yilgan.

## Qayta render qilish

```bash
cd design
python3 grade.py                 # rasmlarni qayta gradinglash (ixtiyoriy)
node shot.js                     # HTML → PNG (playwright kerak)
```

`shot.js` tizimdagi Chromium'ni ishlatadi; boshqa binarni ko'rsatish uchun
`CHROMIUM_PATH` muhit o'zgaruvchisini bering.

Matnni o'zgartirish uchun `design/story.html` va `design/post.html`
fayllaridagi matn bloklarini tahrirlab, `node shot.js` ni qayta ishga tushiring.
