# SUPER AI — seminar taklifnomasi (Instagram)

Javohir Mamatqulov va Zilola Saidqulovadan JONLI SEMINAR uchun ikkita post:
9:16 Stories va 1:1 feed. Qora + Claude rangi (`#d97757`), minimalistik
zamonaviy stil, ikkala spiker yonma-yon — bitta jamoa sifatida.

## Tayyor fayllar

| Fayl | O'lcham | Qayerga |
| --- | --- | --- |
| `out/super-ai-seminar-story-1080x1920.png` | 1080×1920 | Instagram Stories |
| `out/super-ai-seminar-post-1080x1080.png` | 1080×1080 | Instagram feed |

Ikkalasi ham sRGB profili bilan belgilangan.

## Har bir mehmon uchun to'ldirish

HTML fayllarda `<!-- ===== FILL PER GUEST ===== -->` izohi bilan belgilangan
blok bor. Ism-familiyani yozish uchun `.write-line` ichiga matn qo'yiladi,
o'rindiq va qator uchun esa raqam katakchalari (`.slot`) turibdi. O'zgartirgach
`node tools/render.mjs` bilan qayta render qilinadi.

## Mijozdan kutilayotgan ma'lumot

**Sana, vaqt va manzil hali berilmagan.** Ular bo'lmasa taklifnoma to'liq emas:
o'rindiq raqami bor, lekin qachon va qayerga borish kerakligi yozilmagan. Har
ikkala HTML'da tayyor joy izohga olingan — ma'lumot kelgach izohni ochish
kifoya:

```html
<div class="facts">12-oktabr &middot; 15:00 &middot; Toshkent</div>
```

## Qayta yig'ish

```bash
python3 tools/prepare_speakers.py   # ikkala portretni bir tizimga keltiradi
node tools/render.mjs               # PNG'larni chiqaradi va safe-zone'ni tekshiradi
python3 tools/embed_srgb.py         # sRGB profilini biriktiradi
```

`render.mjs` har bir matn blokining koordinatasini chop etadi va Instagram'ning
interfeysi bosib qoladigan zonaga tushib qolgan blok bo'lsa xato bilan
to'xtaydi.

## Dizayn qarorlari

**Ikkala rasm bitta jamoa bo'lib ko'rinishi.** Rasmlar butunlay boshqa
studiyalarda olingan: Javohir to'q qizil devor va to'q sariq chiziq oldida,
Zilola esa yorqin oq devor oldida. O'lchov bo'yicha Zilolaning foni uning
yuzidan ham yorqinroq, Javohirniki esa yuzidan uch baravar qorong'i edi.
Shuning uchun:

- `tools/prepare_speakers.py` har ikkala kadrni yuz markazi atrofida qayta
  kesadi — bosh o'lchami va ko'z chizig'i bir xil bo'ladi (skript buni
  tekshiradi va mos kelmasa xato beradi);
- ikkala rasm bitta duotone rampasiga (qora → Claude rangi → krem) tushiriladi,
  yorqin fonli kadr uchun alohida, yuqori tonlari siqilgan variant ishlatiladi;
- diptix to'liq kenglikda (full-bleed), orasida atigi 3px qora chok — bu ikkita
  alohida surat emas, bitta surat degan signal;
- mijozning o'z jumlasi ikki kadrga bo'lingan: chapda "Javohir Mamatqulov va",
  o'ngda "Zilola Saidqulovadan" — har bir ism o'z egasining tagida turadi,
  lekin ikkisi bitta gap bo'lib o'qiladi.

**Fon olib tashlanmagan.** Bu tarmoq siyosati sababli: cutout fayllarini
beradigan CDN (`d8j0ntlcm91z4.cloudfront.net`) bu muhitda 403 qaytaradi.
Shuning uchun birlashtirish kadr, ekspozitsiya va vinyetka orqali qilingan.

**Konsepsiya.** Faqat "AI" so'zi Claude rangidagi ramka ichida, tepasida
`NAZORATDA` yorlig'i turadi — mashina ko'rish tili. Ramka faqat sun'iy
intellekt atrofida; ikkala inson uning tashqarisida. Bu seminarning o'z
g'oyasini — "AI sizni boshqarmasdan oldin siz uni boshqaring" — bosh yozuvning
o'zida takrorlaydi.

**Shrift.** Inter Tight (sarlavha) va Inter (qolgani), o'zgaruvchan (variable)
woff2 sifatida `assets/fonts/` ichida. Latin subset o'zbekcha `ʻ` (U+02BB) va
`ʼ` (U+02BC) belgilarini o'z ichiga oladi, shuning uchun apostroflar
fallback shriftdan emas, Inter'ning o'zidan chiqadi.

## Tekshirilmagan / e'tiborga olinadigan narsalar

- **Chop etish uchun alohida variant kerak.** Hozirgi maket 92% qora bo'yoq
  qoplamasiga ega — bunday sirtga qalam yozmaydi. Bosma nusxa uchun taklifnoma
  bloki oq qog'ozga chiqarilishi kerak.
- `boshqarmasidan` — mijozning matni aynan shunday berilgan. Adabiy me'yorda
  `boshqarmasdan` bo'ladi; o'zgartirilmadi.
- O'rindiq/qator tartibi mijoz yozgan tartibda qoldirildi (odatdagi chipta
  tartibi — avval qator, keyin joy).
