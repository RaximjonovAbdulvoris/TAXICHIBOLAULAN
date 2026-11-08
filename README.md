# TAXICHI BOLA — @taxichibolaulan_bot

LIDERBOT asosida alohida tayyorlangan bitta taksopark boti. Asl LIDER repozitori o‘zgartirilmaydi.

## Funksiyalar
- Menyu: Ulanish uchun Ariza, Brend Ariza, Ofis manzili, Bog‘lanish.
- Hudud tanlanmaydi; barcha haydovchi arizalari bitta DRIVER_GROUP_1 guruhiga yuboriladi.
- Ism-familiya va telefonni foydalanuvchi kiritadi. Hujjatlar original namunalar orqali so‘raladi.
- Mahalliy OCR: familiya, ism, tug‘ilgan sana/joy, PINFL, prava raqami/muddati va texpasport seriyasi. API kaliti kerak emas. Natija operator tomonidan hujjat bilan tekshiriladi.
- Ariza 1, 2, 3… tarzida raqamlanadi; operator kartasi ko‘chirishga qulay.
- Tayyor, Jarayonda, Chala rasm, Boshqa park, O‘chirish va ZIP tugmalari.
- Tayyor arizani arxivga ko‘chiradi; Chala/Boshqa park alohida guruhlarga o‘tkazadi va arizachiga xabar beradi.
- ZIP ichida haydovchi nomidagi papka va hujjatlar; ko‘chirishda eski ZIP xabarlari tozalanadi.
- Brend arizasi oddiy post; Google Sheets, brend tasdiqlashi, Spectre va konkurs yo‘q.
- Premium emoji imkoniyati, original hujjat shablonlari va shifrlangan ariza holati.

## Sozlash
Python 3.11+, `requirements.txt` va OCR uchun `requirements-ocr.txt` kerak.
`.env.example`ni alohida `.env`ga ko‘chiring. Token, beshta guruh (ariza/brend/arxiv/chala/boshqa park), CONTACT_PHONE, CONTACT_TELEGRAM, OFFICE_ADDRESS, OFFICE_MAP_URL ni to‘ldiring.
Aloqa/ofis qiymatlari berilmaguncha bot ularni hali qo‘shilmagan deb ko‘rsatadi; boshqa park kontaktlari ishlatilmaydi.

Muhit faylini systemd EnvironmentFile orqali yuklang. Start: `python -m bot.main`.
Bir token uchun bitta jarayon ishlasin. PERSIST_DIR yangi bot uchun alohida, yozish mumkin bo‘lgan papka bo‘lsin. Boshqa bot tokeni yoki persistence fayllarini ko‘chirmang.

OCR tizim paketlari: libseccomp2 libgl1 libglib2.0-0. Tekshiruv: `python scripts/check_neural_ocr.py`.
Guruhlar tekshiruvi: `python -m bot.configure check`. Bot guruhlarda administrator va o‘chirish huquqiga ega bo‘lsin.
Unit testlar: `python -m unittest discover -s tests -q`.

Ishga tushirishdan oldin haqiqiy test arizasi bilan guruh, ZIP, arxiv, Chala/Boshqa park va xabarlarni tekshiring. OCR uchun xatosiz o‘qish yoki qat’iy tezlik kafolati berilmaydi. Telegram hujjatlarni uzatadi; server va guruh a’zolari kirishini nazorat qiling. Shifrlangan holatni tiklash uchun bot_persistence.pkl va bot_persistence.key birga zaxiralansin.
