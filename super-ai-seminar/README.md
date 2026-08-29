# SUPER AI — jonli seminar taklifnomasi

Javohir Mamatqulov va Zilola Saidqulova ishtirokidagi jonli seminar uchun
ijtimoiy tarmoq postlari. Uslub: minimalistik, zamonaviy; palitra — to'q qizil
(burgundi) va to'q olovrang urg'u.

## Tayyor fayllar

**Oq fonli variant (asosiy):**

| Fayl | O'lcham | Qayerga |
| --- | --- | --- |
| `out/story_1080x1920_white.png` | 1080×1920 (9:16) | Instagram Stories |
| `out/post_1080x1080_white.png` | 1080×1080 (1:1) | Instagram feed posti |

**To'q qizil fonli variant:**

| Fayl | O'lcham | Qayerga |
| --- | --- | --- |
| `out/story_1080x1920.png` | 1080×1920 (9:16) | Instagram Stories |
| `out/post_1080x1080.png` | 1080×1080 (1:1) | Instagram feed posti |

Barchasida taklifnoma maydonlari bor: **ism, familiya** uchun chiziq,
**o'rindiq raqami** va **qator** uchun katakchalar.

## Dizayn tizimi

Oq fonli variant (`design/base-light.css`):

- Fon: oq, ustida juda yengil iliq gradient; spikerlar ortida blush panel
  (`#FBF0EB`).
- Ranglar: to'q qizil `#8E1105` / `#5E0A03`, to'q olovrang `#E2481A`, matn
  `#2A100C`, so'lg'un `#9C7B73`.

To'q fonli variant (`design/base.css`): `#1B0407` → `#470B13` gradient, olovrang
urg'u, iliq krem matn.

Ikkalasida ham: sarlavhalar — Montserrat 900, matn — Inter; orqa fonda kontur
bilan yozilgan katta `SUPER AI` yozuvi brend elementi sifatida.

## Spikerlar rasmi

Ikkala rasm bir-biriga moslashtirilib, bitta jamoa kadriga birlashtirilgan:

1. Fon `rembg` (birefnet-portrait modeli) yordamida olib tashlanadi →
   `design/assets/w1_cut.png`, `w2_cut.png` (oq variant uchun) va
   `sp1_cut.png`, `sp2_cut.png` (to'q variant uchun).
2. `design/compose.py` alfa maskasidan bosh va yelka chiziqlarini o'lchaydi,
   so'ng:
   - bosh o'lchamlarini tenglashtiradi (ikkalasi bir xil razmerda),
   - yelkalarni bitta gorizontal chiziqqa qo'yadi,
   - ortiqcha bo'sh joyni kesib, ikkalasini yonma-yon yaqinlashtiradi,
   - kerak bo'lsa, o'ngdagi spikerni belidan pastda kesadi.
3. `design/grade.py` ranglarni tenglashtiradi: oq variantda kanal balansi bilan
   ikkala rasmning rang harorati moslanadi (teri rangi tabiiy qoladi), to'q
   variantda esa iliq burgundi duoton beriladi. Ikkala holatda ham alfa kanali
   tozalanadi.

Natija — ikkita fayl: `design/assets/crew_pair_light.png` va `crew_pair.png`.

## Qayta render qilish

```bash
cd design
python3 compose.py light          # yoki: dark / both
node shot.js                      # HTML → PNG (playwright kerak)
```

`shot.js` tizimdagi Chromium'ni ishlatadi; boshqa binarni ko'rsatish uchun
`CHROMIUM_PATH` muhit o'zgaruvchisini bering.

Matnni o'zgartirish uchun `design/story-light.html` va `design/post-light.html`
(to'q variant uchun `story.html` / `post.html`) fayllaridagi matn bloklarini
tahrirlab, `node shot.js` ni qayta ishga tushiring.
