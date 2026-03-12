#!/usr/bin/env python3
"""
🏫 OQUV MARKAZI — Nemis tili kurslari Telegram Bot
✅ Ro'yxatdan o'tish + Uy vazifasi + Test + Baholash tizimi
✅ Davomat belgilash + Dars jadvali
✅ Kursga yozilish + To'lov tasdiqlash
✅ To'lov tarixi + E'lonlar + Reyting + Admin bog'lanish (yangi!)

O'rnatish:
    pip install pyTelegramBotAPI

Ishga tushirish:
    1. @BotFather → /newbot → TOKEN oling
    2. BOT_TOKEN va DOMLA_PAROLI ni o'zgartiring
    3. python vazifa_bot.py
"""

import telebot
from telebot import types
import datetime
import random

# ============================================================
#  SOZLAMALAR
# ============================================================
BOT_TOKEN       = "8741092251:AAECrlLCFfOx7xx41j-IOwq4MdukDHb8Sps"
DOMLA_PAROLI    = "domla2024"    # O'qituvchi paroli
OQUVCHI_PAROLI  = "oquvchi2024"  # O'quvchi paroli
# ============================================================

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# XOTIRA
# ============================================================
foydalanuvchilar = {}  # {uid: {rol, ism, sinf, holat}}
vazifalar        = []  # [{id, sarlavha, tavsif, muddat, sana}]
topshirishlar    = []  # [{vazifa_id, vazifa_nomi, oquvchi_id, ism, sinf, matn, vaqt, baho, izoh}]
testlar          = []  # [{id, savol, variantlar, togri, yaratgan, sana}]
aktiv_testlar    = {}  # {uid: {savollar, joriy, ball, boshlanish}}
test_natijalari  = []  # [{uid, ism, sinf, ball, jami, baho, vaqt}]
baholar          = []  # [{uid, ism, sinf, tur, ball, max_ball, izoh, sana, domla}]

# Yangi: Davomat va Dars jadvali
davomat_yozuvlari = []  # [{sana, sinf, uid, ism, holat, izoh, domla_uid}]
dars_jadvali      = {}  # {sinf: [{kun, soat, fan, xona}]}

# Yangi: Kurslar tizimi
kurslar       = []  # [{id, nomi, tavsif, narx, muddat, joylar, sana, aktiv}]
kurs_arizalar = []  # [{id, kurs_id, kurs_nomi, uid, ism, sinf, holat, izoh, vaqt}]
               # holat: "kutilmoqda" | "tasdiqlandi" | "rad_etildi"

# Yangi: To'lov tarixi
tolov_tarix   = []  # [{id, uid, ism, sinf, summa, tur, izoh, holat, sana, domla}]
               # holat: "tasdiqlandi" | "kutilmoqda" | "rad_etildi"

# Yangi: E'lonlar
elonlar       = []  # [{id, sarlavha, matn, domla, sana, muhim}]

# Yangi: Admin xabarlari
admin_xabarlar = []  # [{id, uid, ism, matn, javob, vaqt, javob_vaqt}]

# Vaqtinchalik
hw_temp       = {}
test_temp     = {}
baho_temp     = {}
davomat_temp  = {}
jadval_temp   = {}
kurs_temp     = {}
tolov_temp    = {}   # to'lov qo'shish jarayoni
elon_temp     = {}   # e'lon yaratish jarayoni

# ============================================================
# MENYULAR
# ============================================================

def rol_tanlash_menyu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add(
        types.KeyboardButton("👨‍🏫 O'qituvchi sifatida kirish"),
        types.KeyboardButton("👨‍🎓 O'quvchi sifatida kirish"),
        types.KeyboardButton("🎓 Kursga yozilish"),
    )
    return m

def domla_menyu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(
        types.KeyboardButton("📝 Yangi vazifa berish"),
        types.KeyboardButton("📋 Barcha vazifalar"),
        types.KeyboardButton("📥 Topshirishlar"),
        types.KeyboardButton("➕ Test savoli qo'shish"),
        types.KeyboardButton("📊 Test natijalari"),
        types.KeyboardButton("⭐ Baho berish"),
        types.KeyboardButton("📈 Baholar jurnali"),
        types.KeyboardButton("👥 O'quvchilar"),
        types.KeyboardButton("📊 Davomat belgilash"),
        types.KeyboardButton("📅 Dars jadvali"),
        types.KeyboardButton("🗓 Davomat hisoboti"),
        types.KeyboardButton("🎓 Kurslarni boshqarish"),
        types.KeyboardButton("📨 Kurs arizalari"),
        types.KeyboardButton("💰 To'lovlarni boshqarish"),
        types.KeyboardButton("📣 E'lon yuborish"),
        types.KeyboardButton("📬 Admin xabarlari"),
        types.KeyboardButton("🏅 Reyting"),
        types.KeyboardButton("🔑 Parollarni sozlash"),
        types.KeyboardButton("🚪 Chiqish"),
    )
    return m

def oquvchi_menyu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(
        types.KeyboardButton("📚 Vazifalarni ko'rish"),
        types.KeyboardButton("📤 Vazifa topshirish"),
        types.KeyboardButton("✅ Mening topshirishlarim"),
        types.KeyboardButton("🧪 Testni boshlash"),
        types.KeyboardButton("🏆 Mening natijalarim"),
        types.KeyboardButton("📋 Mening baholarim"),
        types.KeyboardButton("📅 Dars jadvalim"),
        types.KeyboardButton("📊 Mening davomatim"),
        types.KeyboardButton("🎓 Kurslarga yozilish"),
        types.KeyboardButton("📜 Mening kurslarim"),
        types.KeyboardButton("💳 To'lov tarixim"),
        types.KeyboardButton("📣 E'lonlar"),
        types.KeyboardButton("🏅 Reyting"),
        types.KeyboardButton("📞 Admin bilan bog'lanish"),
        types.KeyboardButton("👤 Mening profilim"),
        types.KeyboardButton("🔑 Parolni o'zgartirish"),
        types.KeyboardButton("🚪 Chiqish"),
    )
    return m

# ============================================================
# YORDAMCHI
# ============================================================

def get_user(uid):
    return foydalanuvchilar.get(uid)

def is_registered(uid):
    u = get_user(uid)
    return u and u.get("holat") == "done"

def is_domla(uid):
    u = get_user(uid)
    return u and u.get("rol") == "domla" and u.get("holat") == "done"

def is_oquvchi(uid):
    u = get_user(uid)
    return u and u.get("rol") == "oquvchi" and u.get("holat") == "done"

def require_auth(message):
    if not is_registered(message.from_user.id):
        bot.send_message(message.chat.id,
            "⚠️ Avval tizimga kirishingiz kerak.\n/start ni bosing.",
            reply_markup=types.ReplyKeyboardRemove())
        return True
    return False

def ball_baho(ball, max_ball):
    if max_ball == 0:
        return "—"
    foiz = ball / max_ball * 100
    if foiz >= 90: return "5 ⭐⭐⭐⭐⭐"
    if foiz >= 75: return "4 ⭐⭐⭐⭐"
    if foiz >= 55: return "3 ⭐⭐⭐"
    return "2 ⭐⭐"

def test_baho(ball, jami):
    foiz = ball / jami * 100 if jami else 0
    if foiz == 100: return "🏆 A'lo — 5"
    if foiz >= 80:  return "🥇 Yaxshi — 4"
    if foiz >= 60:  return "🥈 Qoniqarli — 3"
    return "🥉 Qoniqarsiz — 2"

def oquvchilar_royxati_inline():
    oq = [(sid, info) for sid, info in foydalanuvchilar.items()
          if info.get("rol") == "oquvchi" and info.get("holat") == "done"]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for sid, info in oq:
        markup.add(types.InlineKeyboardButton(
            f"👤 {info['ism']} ({info.get('sinf','—')})",
            callback_data=f"baho_oquvchi_{sid}"
        ))
    return markup, len(oq)

def _ortacha_baho(uid):
    mening = [b for b in baholar if b["uid"] == uid]
    if not mening: return "—"
    foizlar = [b["ball"]/b["max_ball"]*100 for b in mening if b["max_ball"]>0]
    if not foizlar: return "—"
    avg = sum(foizlar)/len(foizlar)
    if avg >= 90: return "5.0 ⭐"
    if avg >= 75: return "4.0 ⭐"
    if avg >= 55: return "3.0 ⭐"
    return "2.0 ⭐"

# Haftaning kunlari
KUNLAR = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]

# ============================================================
# /start
# ============================================================

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    if is_registered(uid):
        u = get_user(uid)
        # Parol tekshiruvi — o'quvchi uchun qayta kirish
        if u.get("rol") == "oquvchi":
            u["holat"] = "login_parol"
            u["login_urinish"] = 0
            msg = bot.send_message(uid,
                f"👋 Salom! *{u['ism']}*\n\n🔐 Parolingizni kiriting:",
                parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, oquvchi_login_parol)
        else:
            menyu = domla_menyu()
            bot.send_message(uid, f"👋 Qaytib keldingiz, *{u['ism']} domla*!",
                             parse_mode="Markdown", reply_markup=menyu)
        return
    foydalanuvchilar[uid] = {"holat": "register_role"}
    bot.send_message(uid,
        "🎓 *Oquv Markaziga xush kelibsiz!*\n\nKim sifatida kirishni tanlang 👇",
        parse_mode="Markdown", reply_markup=rol_tanlash_menyu())

# ============================================================
# O'QITUVCHI — RO'YXATDAN O'TISH
# ============================================================

@bot.message_handler(func=lambda m: m.text == "👨‍🏫 O'qituvchi sifatida kirish")
def rol_domla(message):
    uid = message.from_user.id
    foydalanuvchilar[uid] = {"holat": "domla_parol", "rol": "domla"}
    msg = bot.send_message(message.chat.id,
        "🔐 *O'qituvchi paneli*\n\nParolni kiriting:",
        parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, domla_parol_tekshir)

def domla_parol_tekshir(message):
    uid = message.from_user.id
    if message.text.strip() == DOMLA_PAROLI:
        foydalanuvchilar[uid]["holat"] = "domla_ism"
        msg = bot.send_message(message.chat.id,
            "✅ *Parol to'g'ri!*\n\nIsmingizni kiriting:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, domla_ism_saqlash)
    else:
        foydalanuvchilar.pop(uid, None)
        bot.send_message(message.chat.id,
            "❌ *Noto'g'ri parol!* /start dan qayta urining.",
            parse_mode="Markdown", reply_markup=rol_tanlash_menyu())

def domla_ism_saqlash(message):
    uid = message.from_user.id
    foydalanuvchilar[uid].update({
        "ism": message.text.strip(),
        "username": message.from_user.username or "",
        "qoshilgan": str(datetime.date.today()),
        "holat": "done",
    })
    bot.send_message(message.chat.id,
        f"🎉 *Xush kelibsiz, {foydalanuvchilar[uid]['ism']} domla!*\n\nMenyudan foydalaning 👇",
        parse_mode="Markdown", reply_markup=domla_menyu())

# ============================================================
# O'QUVCHI — RO'YXATDAN O'TISH
# ============================================================

# ============================================================
# O'QUVCHI — RO'YXATDAN O'TISH
# ============================================================

@bot.message_handler(func=lambda m: m.text == "👨‍🎓 O'quvchi sifatida kirish")
def rol_oquvchi(message):
    uid = message.from_user.id

    # Allaqachon ro'yxatdan o'tgan — parol so'raymiz
    mavjud = next((u for u in foydalanuvchilar.values()
                   if u.get("telegram_id") == uid
                   and u.get("rol") == "oquvchi"
                   and u.get("holat") == "done"), None)
    if mavjud:
        foydalanuvchilar[uid] = dict(mavjud)  # qayta yuklash
        foydalanuvchilar[uid]["holat"] = "login_parol"
        msg = bot.send_message(message.chat.id,
            "👨‍🎓 *O'quvchi tizimga kirish*\n\n🔐 Parolingizni kiriting:",
            parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, oquvchi_login_parol)
        return

    # Birinchi marta — ro'yxatdan o'tish
    foydalanuvchilar[uid] = {"holat": "oquvchi_ism", "rol": "oquvchi", "telegram_id": uid}
    msg = bot.send_message(message.chat.id,
        "👨‍🎓 *O'quvchi ro'yxatdan o'tish*\n\n"
        "1️⃣ To'liq ismingizni kiriting:",
        parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, oquvchi_ism_saqlash)


def oquvchi_login_parol(message):
    """Mavjud o'quvchi parol bilan kiradi"""
    uid = message.from_user.id
    u   = foydalanuvchilar.get(uid, {})
    if message.text.strip() == u.get("parol", ""):
        u["holat"] = "done"
        bot.send_message(message.chat.id,
            f"✅ *Xush kelibsiz, {u['ism']}!*",
            parse_mode="Markdown", reply_markup=oquvchi_menyu())
    else:
        # 3 marta urinish
        u["login_urinish"] = u.get("login_urinish", 0) + 1
        qolgan = 3 - u["login_urinish"]
        if qolgan <= 0:
            foydalanuvchilar.pop(uid, None)
            bot.send_message(message.chat.id,
                "🔒 *3 marta noto'g'ri parol!*\n\n/start dan qayta urining.",
                parse_mode="Markdown", reply_markup=rol_tanlash_menyu())
        else:
            msg = bot.send_message(message.chat.id,
                f"❌ *Noto'g'ri parol!*\nQolgan urinish: *{qolgan} ta*\n\nQayta kiriting:",
                parse_mode="Markdown")
            bot.register_next_step_handler(msg, oquvchi_login_parol)


def oquvchi_reg_parol_kirish(message):
    uid   = message.from_user.id
    parol = message.text.strip()
    if len(parol) < 4:
        msg = bot.send_message(message.chat.id,
            "❌ Parol kamida *4 ta belgi* bo'lishi kerak!\nQayta kiriting:",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, oquvchi_reg_parol_kirish)
        return
    foydalanuvchilar[uid]["parol_temp"] = parol
    msg = bot.send_message(message.chat.id,
        "2️⃣ 🔐 Parolni qayta kiriting _(tasdiqlash)_:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, oquvchi_reg_parol_tasdiqlash)


def oquvchi_reg_parol_tasdiqlash(message):
    uid   = message.from_user.id
    u     = foydalanuvchilar.get(uid, {})
    parol = message.text.strip()
    if parol != u.get("parol_temp", ""):
        msg = bot.send_message(message.chat.id,
            "❌ *Parollar mos kelmadi!*\nQaytadan o'rnating:",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, oquvchi_reg_parol_kirish)
        return
    foydalanuvchilar[uid].update({
        "parol":         parol,
        "sinf":          "—",
        "username":      message.from_user.username or "",
        "qoshilgan":     str(datetime.date.today()),
        "holat":         "done",
        "login_urinish": 0,
    })
    foydalanuvchilar[uid].pop("parol_temp", None)
    u = foydalanuvchilar[uid]
    bot.send_message(message.chat.id,
        f"🎉 *Ro'yxatdan o'tdingiz!*\n\n"
        f"👤 *{u['ism']}*\n"
        f"🔐 Parol: `{parol}`\n\n"
        f"⚠️ _Parolingizni yodda saqlang!_\n\n"
        f"Menyudan foydalaning 👇",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())


def oquvchi_ism_saqlash(message):
    uid = message.from_user.id
    foydalanuvchilar[uid]["ism"] = message.text.strip()
    msg = bot.send_message(message.chat.id,
        "2️⃣ 🔐 O'zingiz uchun parol o'rnating:\n"
        "_(kamida 4 ta belgi, raqam yoki harf)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, oquvchi_reg_parol_kirish)


def oquvchi_sinf_saqlash(message):
    pass  # eski mos kelish uchun saqlab qolindi


def oquvchi_parol_ornatish(message):
    uid   = message.from_user.id
    parol = message.text.strip()
    if len(parol) < 4:
        msg = bot.send_message(message.chat.id,
            "❌ Parol kamida *4 ta belgi* bo'lishi kerak!\nQayta kiriting:",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, oquvchi_parol_ornatish)
        return
    foydalanuvchilar[uid]["holat_parol"] = "tasdiqlash"
    foydalanuvchilar[uid]["parol_temp"]  = parol
    msg = bot.send_message(message.chat.id,
        "4️⃣ 🔐 Parolni qayta kiriting _(tasdiqlash uchun)_:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, oquvchi_parol_tasdiqlash)


def oquvchi_parol_tasdiqlash(message):
    uid   = message.from_user.id
    u     = foydalanuvchilar.get(uid, {})
    parol = message.text.strip()

    if parol != u.get("parol_temp", ""):
        msg = bot.send_message(message.chat.id,
            "❌ *Parollar mos kelmadi!*\nQaytadan o'rnating:",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, oquvchi_parol_ornatish)
        return

    foydalanuvchilar[uid].update({
        "parol":        parol,
        "sinf":         "—",
        "username":     message.from_user.username or "",
        "qoshilgan":    str(datetime.date.today()),
        "holat":        "done",
        "login_urinish": 0,
    })
    foydalanuvchilar[uid].pop("parol_temp", None)
    foydalanuvchilar[uid].pop("holat_parol", None)

    u = foydalanuvchilar[uid]
    bot.send_message(message.chat.id,
        f"🎉 *Ro'yxatdan o'tdingiz!*\n\n"
        f"👤 *{u['ism']}*\n"
        f"🔐 Parol: `{parol}`\n\n"
        f"⚠️ _Parolingizni yodda saqlang!_\n\n"
        f"Menyudan foydalaning 👇",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())

# ============================================================
# KURSGA YOZILISH — RO'YXATDAN O'TMAGAN FOYDALANUVCHI UCHUN
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🎓 Kursga yozilish")
def tashqi_kursga_yozilish(message):
    uid = message.from_user.id

    # Agar allaqachon ro'yxatdan o'tgan o'quvchi bosgan bo'lsa
    if is_oquvchi(uid):
        oquvchi_kurslarga_yozilish(message)
        return

    # Ro'yxatdan o'tmagan yangi odam
    aktiv_kurslar = [k for k in kurslar if k["aktiv"]]
    if not aktiv_kurslar:
        bot.send_message(message.chat.id,
            "🎓 Hozircha ochiq kurs yo'q.\n\nYangi kurslar e'lon qilinganda xabar beramiz! 🔔",
            reply_markup=rol_tanlash_menyu())
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for k in aktiv_kurslar:
        yozilganlar = sum(1 for a in kurs_arizalar
                          if a["kurs_id"] == k["id"] and a["holat"] == "tasdiqlandi")
        joy_ok = k["joylar"] == 0 or yozilganlar < k["joylar"]
        if joy_ok:
            markup.add(types.InlineKeyboardButton(
                f"🎓 {k['nomi']} — {k['narx']}",
                callback_data=f"tashqi_kurs_{k['id']}_{uid}"))
        else:
            markup.add(types.InlineKeyboardButton(
                f"🔴 {k['nomi']} — To'lgan",
                callback_data=f"tashqi_info_{k['id']}"))

    bot.send_message(message.chat.id,
        "🎓 *Kurslarimiz:*\n\nYozilmoqchi bo'lgan kursni tanlang 👇",
        parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tashqi_info_"))
def tashqi_kurs_info(call):
    bot.answer_callback_query(call.id, "Bu kurs to'lgan. Boshqa kursni tanlang.", show_alert=True)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tashqi_kurs_"))
def tashqi_kurs_tanlandi(call):
    parts   = call.data.split("_")
    kurs_id = int(parts[2])
    uid     = int(parts[3])

    if call.from_user.id != uid:
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    kurs = next((k for k in kurslar if k["id"] == kurs_id), None)
    if not kurs:
        bot.answer_callback_query(call.id, "Kurs topilmadi.")
        return

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    jadval      = kurs.get("jadval", [])
    jadval_text = "\n".join(f"📅 {j['kun']}: ⏰ {j['vaqt']}" for j in jadval) if jadval else "—"
    yozilganlar = sum(1 for a in kurs_arizalar
                      if a["kurs_id"] == kurs_id and a["holat"] == "tasdiqlandi")
    joy_text    = f"{kurs['joylar'] - yozilganlar} ta bo'sh o'rin" if kurs["joylar"] > 0 else "Cheksiz"

    markup = types.InlineKeyboardMarkup(row_width=1)
    for j in jadval:
        markup.add(types.InlineKeyboardButton(
            f"📅 {j['kun']}  ⏰ {j['vaqt']}",
            callback_data=f"tashqi_vaxt_{kurs_id}_{j['kun']}_{uid}"))
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="tashqi_bekor"))

    bot.send_message(call.message.chat.id,
        f"🎓 *{kurs['nomi']}*\n\n"
        f"📝 {kurs['tavsif']}\n"
        f"💰 Narx: *{kurs['narx']}*\n"
        f"⏳ Muddat: *{kurs['muddat']}*\n"
        f"👥 Bo'sh o'rin: {joy_text}\n\n"
        f"*Dars kunlari va vaqtlari:*\n{jadval_text}\n\n"
        f"👇 Qaysi kunda qatnashmoqchisiz — tanlang:",
        parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "tashqi_bekor")
def tashqi_bekor(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, "Bekor qilindi.", reply_markup=rol_tanlash_menyu())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tashqi_vaxt_"))
def tashqi_vaxt_tanlandi(call):
    parts   = call.data.split("_")
    kurs_id = int(parts[2])
    # kun nomi "Dushanba" kabi, uid oxirida
    uid     = int(parts[-1])
    kun     = "_".join(parts[3:-1])

    if call.from_user.id != uid:
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    kurs = next((k for k in kurslar if k["id"] == kurs_id), None)
    jadval_entry = next((j for j in kurs.get("jadval", []) if j["kun"] == kun), None)
    vaqt = jadval_entry["vaqt"] if jadval_entry else "—"

    # Temp saqlaymiz
    kurs_temp[uid] = {
        "kurs_id":        kurs_id,
        "kurs_nomi":      kurs["nomi"],
        "tanlangan_kun":  kun,
        "tanlangan_vaqt": vaqt,
        "tashqi":         True,   # ro'yxatdan o'tmagan
    }

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    msg = bot.send_message(call.message.chat.id,
        f"✅ Tanlangan: *{kun}*  ⏰ *{vaqt}*\n\n"
        f"1️⃣ To'liq ismingizni kiriting:",
        parse_mode="Markdown")
    bot.answer_callback_query(call.id)
    bot.register_next_step_handler(msg, lambda m: tashqi_ism_qabul(m, uid))


def tashqi_ism_qabul(message, uid):
    kurs_temp[uid]["ism"] = message.text.strip()
    msg = bot.send_message(message.chat.id,
        "2️⃣ 📞 Telefon raqamingizni kiriting:\n_(masalan: +998 90 123 45 67)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: tashqi_telefon_qabul(m, uid))


def tashqi_telefon_qabul(message, uid):
    telefon = message.text.strip()
    if len(telefon) < 7:
        msg = bot.send_message(message.chat.id,
            "❌ Telefon noto'g'ri. Qayta kiriting:\n_(masalan: +998901234567)_",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, lambda m: tashqi_telefon_qabul(m, uid))
        return

    temp = kurs_temp.pop(uid, {})
    if not temp:
        bot.send_message(message.chat.id,
            "❌ Sessiya tugagan. Qaytadan bosing.", reply_markup=rol_tanlash_menyu())
        return

    kurs = next((k for k in kurslar if k["id"] == temp["kurs_id"]), None)
    ariza = {
        "id":             len(kurs_arizalar) + 1,
        "kurs_id":        temp["kurs_id"],
        "kurs_nomi":      temp["kurs_nomi"],
        "uid":            uid,
        "ism":            temp.get("ism", "—"),
        "sinf":           "—",
        "telefon":        telefon,
        "kun":            temp.get("tanlangan_kun", "—"),
        "vaqt":           temp.get("tanlangan_vaqt", "—"),
        "holat":          "kutilmoqda",
        "izoh":           "",
        "vaqt_yuborildi": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
    }
    kurs_arizalar.append(ariza)

    bot.send_message(message.chat.id,
        f"🎉 *Arizangiz qabul qilindi!*\n\n"
        f"👤 Ism: *{ariza['ism']}*\n"
        f"📞 Tel: *{telefon}*\n"
        f"🎓 Kurs: *{ariza['kurs_nomi']}*\n"
        f"📅 Kun: *{ariza['kun']}*  ⏰ *{ariza['vaqt']}*\n\n"
        f"✅ O'qituvchi siz bilan tez orada bog'lanadi! 🔔\n\n"
        f"Botdan to'liq foydalanish uchun ro'yxatdan o'ting 👇",
        parse_mode="Markdown", reply_markup=rol_tanlash_menyu())

    # Domlaga xabar
    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "domla" and info.get("holat") == "done":
            try:
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ariza_tasd_{ariza['id']}"),
                    types.InlineKeyboardButton("❌ Rad etish",  callback_data=f"ariza_rad_{ariza['id']}"),
                )
                bot.send_message(sid,
                    f"📨 *Yangi kurs arizasi!* (Tashqi)\n\n"
                    f"👤 *{ariza['ism']}*\n"
                    f"📞 Tel: {telefon}\n"
                    f"🎓 {ariza['kurs_nomi']}\n"
                    f"📅 {ariza['kun']}  ⏰ {ariza['vaqt']}\n"
                    f"🕐 {ariza['vaqt_yuborildi']}",
                    parse_mode="Markdown", reply_markup=markup)
            except: pass


# ============================================================
# CHIQISH
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🚪 Chiqish")
def chiqish(message):
    foydalanuvchilar.pop(message.from_user.id, None)
    bot.send_message(message.chat.id,
        "👋 Tizimdan chiqdingiz. /start bosing.",
        reply_markup=types.ReplyKeyboardRemove())

# ============================================================
# DOMLA: YANGI VAZIFA
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📝 Yangi vazifa berish")
def yangi_vazifa(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return
    hw_temp[message.from_user.id] = {}
    msg = bot.send_message(message.chat.id,
        "📝 *Yangi uy vazifasi*\n\n1️⃣ Sarlavhani yozing:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, vazifa_sarlavha)

def vazifa_sarlavha(message):
    hw_temp[message.from_user.id]["sarlavha"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "2️⃣ Vazifa mazmunini yozing:")
    bot.register_next_step_handler(msg, vazifa_tavsif)

def vazifa_tavsif(message):
    hw_temp[message.from_user.id]["tavsif"] = message.text.strip()
    msg = bot.send_message(message.chat.id,
        "3️⃣ Topshirish muddatini yozing:\n_(masalan: 15-mart)_", parse_mode="Markdown")
    bot.register_next_step_handler(msg, vazifa_muddat)

def vazifa_muddat(message):
    uid  = message.from_user.id
    temp = hw_temp.get(uid, {})
    vazifa = {
        "id": len(vazifalar) + 1,
        "sarlavha": temp.get("sarlavha", "—"),
        "tavsif":   temp.get("tavsif", "—"),
        "muddat":   message.text.strip(),
        "sana":     str(datetime.date.today()),
    }
    vazifalar.append(vazifa)
    bot.send_message(message.chat.id,
        f"✅ *Vazifa qo'shildi!*\n\n📌 *{vazifa['sarlavha']}*\n📝 {vazifa['tavsif']}\n📅 {vazifa['muddat']}",
        parse_mode="Markdown", reply_markup=domla_menyu())
    sent = 0
    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "oquvchi" and info.get("holat") == "done":
            try:
                bot.send_message(sid,
                    f"🔔 *Yangi uy vazifasi!*\n\n📌 *{vazifa['sarlavha']}*\n📝 {vazifa['tavsif']}\n📅 Muddat: {vazifa['muddat']}",
                    parse_mode="Markdown")
                sent += 1
            except: pass
    if sent:
        bot.send_message(message.chat.id, f"📣 {sent} ta o'quvchiga xabar yuborildi.")

# ============================================================
# DOMLA: BARCHA VAZIFALAR
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📋 Barcha vazifalar")
def barcha_vazifalar(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return
    if not vazifalar:
        bot.send_message(message.chat.id, "📋 Hozircha vazifa yo'q.", reply_markup=domla_menyu())
        return
    text = "📋 *Berilgan vazifalar:*\n\n"
    for v in reversed(vazifalar[-10:]):
        n = sum(1 for t in topshirishlar if t["vazifa_id"] == v["id"])
        text += f"*№{v['id']}. {v['sarlavha']}*\n📝 {v['tavsif']}\n📅 {v['muddat']} | ✅ {n} ta topshirdi\n─────────────────\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())

# ============================================================
# DOMLA: TOPSHIRISHLAR
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📥 Topshirishlar")
def topshirishlar_domla(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return
    if not topshirishlar:
        bot.send_message(message.chat.id, "📥 Hech kim topshirmagan.", reply_markup=domla_menyu())
        return
    text = f"📥 *Topshirishlar ({len(topshirishlar)} ta):*\n\n"
    for i, t in enumerate(reversed(topshirishlar[-15:])):
        baho_text = t.get("baho", "⏳ Baholanmagan")
        izoh_text = f"\n   💬 {t['izoh']}" if t.get("izoh") else ""
        text += (f"*{i+1}. {t['ism']}* ({t.get('sinf','—')})\n"
                 f"   📌 {t['vazifa_nomi']}\n"
                 f"   📝 {t['matn'][:80]}{'...' if len(t['matn'])>80 else ''}\n"
                 f"   ⭐ Baho: {baho_text}{izoh_text}\n"
                 f"   🕐 {t['vaqt']}\n─────────────────\n")
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())

# ============================================================
# DOMLA: O'QUVCHILAR
# ============================================================

@bot.message_handler(func=lambda m: m.text == "👥 O'quvchilar")
def oquvchilar_korsatish(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return
    oq = [(s,i) for s,i in foydalanuvchilar.items()
          if i.get("rol")=="oquvchi" and i.get("holat")=="done"]
    if not oq:
        bot.send_message(message.chat.id, "👥 O'quvchi yo'q.", reply_markup=domla_menyu())
        return
    text = f"👥 *O'quvchilar ({len(oq)} ta):*\n\n"
    for i, (sid, info) in enumerate(oq, 1):
        topsh = sum(1 for t in topshirishlar if t["oquvchi_id"] == sid)
        nats  = [n["ball"]/n["jami"]*100 for n in test_natijalari if n["uid"]==sid and n["jami"]>0]
        avg_t = f"{sum(nats)/len(nats):.0f}%" if nats else "—"
        ort_b = _ortacha_baho(sid)
        # Davomat foizi
        mening_dav = [d for d in davomat_yozuvlari if d["uid"] == sid]
        keldi_soni = sum(1 for d in mening_dav if d["holat"] == "keldi")
        dav_foiz = f"{keldi_soni}/{len(mening_dav)}" if mening_dav else "—"
        text += (f"{i}. *{info['ism']}* ({info.get('sinf','—')})\n"
                 f"   ✅ Vazifa: {topsh} | 🧪 Test: {avg_t} | ⭐ O'rt baho: {ort_b} | 📊 Davomat: {dav_foiz}\n\n")
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())

# ============================================================
# DOMLA: TEST SAVOLI QO'SHISH
# ============================================================

@bot.message_handler(func=lambda m: m.text == "➕ Test savoli qo'shish")
def test_savol_qosh(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return
    test_temp[message.from_user.id] = {}
    msg = bot.send_message(message.chat.id,
        "🧪 *Yangi test savoli*\n\n1️⃣ Savol matnini yozing:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, test_savol_matn)

def test_savol_matn(message):
    test_temp[message.from_user.id]["savol"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "2️⃣ *A* variantini yozing:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, test_variant_a)

def test_variant_a(message):
    test_temp[message.from_user.id]["A"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "3️⃣ *B* variantini yozing:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, test_variant_b)

def test_variant_b(message):
    test_temp[message.from_user.id]["B"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "4️⃣ *C* variantini yozing:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, test_variant_c)

def test_variant_c(message):
    test_temp[message.from_user.id]["C"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "5️⃣ *D* variantini yozing:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, test_variant_d)

def test_variant_d(message):
    test_temp[message.from_user.id]["D"] = message.text.strip()
    uid  = message.from_user.id
    temp = test_temp[uid]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"A) {temp['A']}", callback_data=f"togri_0_{uid}"),
        types.InlineKeyboardButton(f"B) {temp['B']}", callback_data=f"togri_1_{uid}"),
        types.InlineKeyboardButton(f"C) {temp['C']}", callback_data=f"togri_2_{uid}"),
        types.InlineKeyboardButton(f"D) {temp['D']}", callback_data=f"togri_3_{uid}"),
    )
    bot.send_message(message.chat.id,
        f"6️⃣ *To'g'ri javobni tanlang:*\n\n❓ {temp['savol']}\n\n"
        f"A) {temp['A']}\nB) {temp['B']}\nC) {temp['C']}\nD) {temp['D']}",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("togri_"))
def togri_javob_tanlash(call):
    parts  = call.data.split("_")
    togri  = int(parts[1])
    uid    = int(parts[2])
    if call.from_user.id != uid:
        bot.answer_callback_query(call.id, "Bu sizning savolingiz emas.")
        return
    temp = test_temp.get(uid, {})
    savol = {
        "id": len(testlar) + 1,
        "savol": temp["savol"],
        "variantlar": [temp["A"], temp["B"], temp["C"], temp["D"]],
        "togri": togri,
        "yaratgan": foydalanuvchilar[uid].get("ism", "Domla"),
        "sana": str(datetime.date.today()),
    }
    testlar.append(savol)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    harflar = ["A", "B", "C", "D"]
    bot.send_message(call.message.chat.id,
        f"✅ *Savol saqlandi!*\n\n❓ {savol['savol']}\n"
        f"✔️ To'g'ri: *{harflar[togri]}) {savol['variantlar'][togri]}*\n\nJami: *{len(testlar)} ta savol*",
        parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id, "✅ Saqlandi!")

# ============================================================
# DOMLA: TEST NATIJALARI
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📊 Test natijalari")
def test_natijalari_domla(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return
    if not test_natijalari:
        bot.send_message(message.chat.id, "📊 Hozircha test natijalari yo'q.", reply_markup=domla_menyu())
        return
    sorted_n = sorted(test_natijalari, key=lambda x: x["ball"]/x["jami"] if x["jami"] else 0, reverse=True)
    text = f"📊 *Test natijalari ({len(test_natijalari)} ta):*\n\n"
    for i, n in enumerate(sorted_n[:20], 1):
        foiz = int(n['ball']/n['jami']*100) if n['jami'] else 0
        text += (f"{i}. *{n['ism']}* ({n.get('sinf','—')})\n"
                 f"   🎯 {n['ball']}/{n['jami']} ({foiz}%) — {n['baho']}\n"
                 f"   🕐 {n['vaqt']}\n\n")
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())

# ============================================================
# ⭐ DOMLA: BAHO BERISH TIZIMI
# ============================================================

@bot.message_handler(func=lambda m: m.text == "⭐ Baho berish")
def baho_berish_boshlash(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    markup, soni = oquvchilar_royxati_inline()
    if soni == 0:
        bot.send_message(message.chat.id,
            "👥 Hozircha ro'yxatdan o'tgan o'quvchi yo'q.", reply_markup=domla_menyu())
        return

    bot.send_message(message.chat.id,
        "⭐ *Baho berish*\n\nO'quvchini tanlang:",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("baho_oquvchi_"))
def baho_oquvchi_tanlandi(call):
    if not is_domla(call.from_user.id):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    oquvchi_id = int(call.data.split("_")[2])
    u = get_user(oquvchi_id)
    if not u:
        bot.answer_callback_query(call.id, "O'quvchi topilmadi.")
        return

    baho_temp[call.from_user.id] = {"oquvchi_id": oquvchi_id}
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📝 Uy vazifasi", callback_data="baho_tur_vazifa"),
        types.InlineKeyboardButton("🧪 Test / Nazorat", callback_data="baho_tur_test"),
        types.InlineKeyboardButton("💬 Dars javobi", callback_data="baho_tur_dars"),
        types.InlineKeyboardButton("🌟 Faollik", callback_data="baho_tur_faollik"),
    )
    bot.send_message(call.message.chat.id,
        f"👤 O'quvchi: *{u['ism']}* ({u.get('sinf','—')})\n\n"
        f"Baho turini tanlang:",
        parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("baho_tur_"))
def baho_tur_tanlandi(call):
    if not is_domla(call.from_user.id):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    tur_map = {
        "baho_tur_vazifa":  "📝 Uy vazifasi",
        "baho_tur_test":    "🧪 Test / Nazorat",
        "baho_tur_dars":    "💬 Dars javobi",
        "baho_tur_faollik": "🌟 Faollik",
    }
    tur = tur_map.get(call.data, "Boshqa")
    baho_temp[call.from_user.id]["tur"] = tur
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("5 balldan 5", callback_data="baho_ball_5_5"),
        types.InlineKeyboardButton("4 balldan 5", callback_data="baho_ball_4_5"),
        types.InlineKeyboardButton("3 balldan 5", callback_data="baho_ball_3_5"),
        types.InlineKeyboardButton("2 balldan 5", callback_data="baho_ball_2_5"),
        types.InlineKeyboardButton("10 dan 10",   callback_data="baho_ball_10_10"),
        types.InlineKeyboardButton("8 dan 10",    callback_data="baho_ball_8_10"),
        types.InlineKeyboardButton("6 dan 10",    callback_data="baho_ball_6_10"),
        types.InlineKeyboardButton("4 dan 10",    callback_data="baho_ball_4_10"),
        types.InlineKeyboardButton("✏️ O'zim kiriting", callback_data="baho_ball_custom"),
    )
    bot.send_message(call.message.chat.id,
        f"Tur: *{tur}*\n\nBallni tanlang yoki o'zingiz kiriting:",
        parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("baho_ball_"))
def baho_ball_tanlandi(call):
    if not is_domla(call.from_user.id):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    uid = call.from_user.id
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if call.data == "baho_ball_custom":
        msg = bot.send_message(call.message.chat.id,
            "✏️ Ball kiriting formatda: *olingan/maksimal*\n_(masalan: 7/10 yoki 4/5)_",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, baho_custom_ball)
    else:
        parts = call.data.replace("baho_ball_", "").split("_")
        ball, max_ball = int(parts[0]), int(parts[1])
        baho_temp[uid]["ball"]     = ball
        baho_temp[uid]["max_ball"] = max_ball
        msg = bot.send_message(call.message.chat.id,
            f"Ball: *{ball}/{max_ball}*\n\n💬 Izoh yozing _(ixtiyoriy, o'tkazish uchun — yozing)_:",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, baho_izoh_saqlash)
    bot.answer_callback_query(call.id)

def baho_custom_ball(message):
    uid = message.from_user.id
    try:
        parts = message.text.strip().split("/")
        ball, max_ball = int(parts[0]), int(parts[1])
        if ball > max_ball or ball < 0 or max_ball <= 0:
            raise ValueError
        baho_temp[uid]["ball"]     = ball
        baho_temp[uid]["max_ball"] = max_ball
        msg = bot.send_message(message.chat.id,
            f"Ball: *{ball}/{max_ball}*\n\n💬 Izoh yozing _(ixtiyoriy, o'tkazish uchun — yozing)_:",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, baho_izoh_saqlash)
    except:
        msg = bot.send_message(message.chat.id,
            "❌ Noto'g'ri format. Qayta kiriting:\n_(masalan: 7/10)_", parse_mode="Markdown")
        bot.register_next_step_handler(msg, baho_custom_ball)

def baho_izoh_saqlash(message):
    uid  = message.from_user.id
    temp = baho_temp.get(uid, {})
    izoh = "" if message.text.strip() == "—" else message.text.strip()

    oquvchi_id = temp.get("oquvchi_id")
    oquvchi    = get_user(oquvchi_id)
    domla_ism  = get_user(uid)

    ball      = temp.get("ball", 0)
    max_ball  = temp.get("max_ball", 5)
    tur       = temp.get("tur", "Boshqa")
    baho_text = ball_baho(ball, max_ball)
    foiz      = int(ball / max_ball * 100) if max_ball else 0

    yozuv = {
        "uid":      oquvchi_id,
        "ism":      oquvchi.get("ism", "—") if oquvchi else "—",
        "sinf":     oquvchi.get("sinf", "—") if oquvchi else "—",
        "tur":      tur,
        "ball":     ball,
        "max_ball": max_ball,
        "foiz":     foiz,
        "baho":     baho_text,
        "izoh":     izoh,
        "sana":     str(datetime.date.today()),
        "domla":    domla_ism.get("ism", "Domla") if domla_ism else "Domla",
    }
    baholar.append(yozuv)
    baho_temp.pop(uid, None)

    bot.send_message(message.chat.id,
        f"✅ *Baho berildi!*\n\n"
        f"👤 O'quvchi: *{yozuv['ism']}* ({yozuv['sinf']})\n"
        f"📂 Tur: {tur}\n"
        f"🎯 Ball: *{ball}/{max_ball}* ({foiz}%)\n"
        f"⭐ Baho: *{baho_text}*\n"
        f"💬 Izoh: {izoh or '—'}",
        parse_mode="Markdown", reply_markup=domla_menyu())

    if oquvchi_id:
        try:
            izoh_qism = f"\n💬 *Izoh:* {izoh}" if izoh else ""
            bot.send_message(oquvchi_id,
                f"⭐ *Sizga baho qo'yildi!*\n\n"
                f"📂 *Tur:* {tur}\n"
                f"🎯 *Ball:* {ball}/{max_ball} ({foiz}%)\n"
                f"⭐ *Baho:* {baho_text}"
                f"{izoh_qism}\n\n"
                f"👨‍🏫 {yozuv['domla']} domla | 📅 {yozuv['sana']}",
                parse_mode="Markdown")
        except: pass

# ============================================================
# DOMLA: BAHOLAR JURNALI
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📈 Baholar jurnali")
def baholar_jurnali(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    if not baholar:
        bot.send_message(message.chat.id,
            "📈 Hozircha hech qanday baho yo'q.", reply_markup=domla_menyu())
        return

    oq = [(s, i) for s, i in foydalanuvchilar.items()
          if i.get("rol") == "oquvchi" and i.get("holat") == "done"]

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("📋 Barcha baholar (oxirgi 20)", callback_data="jurnal_barchasi"))
    for sid, info in oq:
        n = sum(1 for b in baholar if b["uid"] == sid)
        if n > 0:
            markup.add(types.InlineKeyboardButton(
                f"👤 {info['ism']} ({info.get('sinf','—')}) — {n} ta baho",
                callback_data=f"jurnal_oquvchi_{sid}"))

    bot.send_message(message.chat.id,
        "📈 *Baholar jurnali*\n\nKimning baholarini ko'rmoqchisiz?",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "jurnal_barchasi")
def jurnal_barchasi(call):
    if not is_domla(call.from_user.id): return
    if not baholar:
        bot.answer_callback_query(call.id, "Baholar yo'q.")
        return
    text = f"📋 *Barcha baholar (oxirgi 20 ta):*\n\n"
    for b in reversed(baholar[-20:]):
        text += (f"👤 *{b['ism']}* ({b.get('sinf','—')})\n"
                 f"   {b['tur']} → *{b['ball']}/{b['max_ball']}* — {b['baho']}\n"
                 f"   📅 {b['sana']}\n\n")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("jurnal_oquvchi_"))
def jurnal_oquvchi(call):
    if not is_domla(call.from_user.id): return
    oquvchi_id = int(call.data.split("_")[2])
    u = get_user(oquvchi_id)
    mening = [b for b in baholar if b["uid"] == oquvchi_id]

    if not mening:
        bot.answer_callback_query(call.id, "Bu o'quvchining bahosi yo'q.")
        return

    foizlar = [b["ball"]/b["max_ball"]*100 for b in mening if b["max_ball"]>0]
    ort     = sum(foizlar)/len(foizlar) if foizlar else 0
    ort_baho = ball_baho(ort, 100)

    text = (f"👤 *{u.get('ism','—')}* ({u.get('sinf','—')})\n"
            f"📊 O'rtacha: *{ort:.1f}%* — {ort_baho}\n"
            f"📝 Jami baholar: *{len(mening)} ta*\n\n")

    for b in reversed(mening[-15:]):
        izoh = f"\n   💬 {b['izoh']}" if b.get("izoh") else ""
        text += (f"• *{b['tur']}*\n"
                 f"  🎯 {b['ball']}/{b['max_ball']} ({b['foiz']}%) — {b['baho']}"
                 f"{izoh}\n  📅 {b['sana']}\n\n")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)

# ============================================================
# 📊 DOMLA: DAVOMAT BELGILASH (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📊 Davomat belgilash")
def davomat_belgilash_boshlash(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    oq = [(sid, info) for sid, info in foydalanuvchilar.items()
          if info.get("rol") == "oquvchi" and info.get("holat") == "done"]

    if not oq:
        bot.send_message(message.chat.id,
            "👥 Hozircha ro'yxatdan o'tgan o'quvchi yo'q.", reply_markup=domla_menyu())
        return

    # Sinf tanlash
    sinflar = list(set(info.get("sinf", "—") for _, info in oq))
    sinflar.sort()

    markup = types.InlineKeyboardMarkup(row_width=2)
    for sinf in sinflar:
        markup.add(types.InlineKeyboardButton(
            f"🏫 {sinf}", callback_data=f"dav_sinf_{sinf}"))
    markup.add(types.InlineKeyboardButton("👥 Barcha o'quvchilar", callback_data="dav_sinf_BARCHASI"))

    today = datetime.date.today().strftime("%d-%m-%Y")
    bot.send_message(message.chat.id,
        f"📊 *Davomat belgilash*\n📅 Sana: *{today}*\n\nQaysi sinf uchun?",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("dav_sinf_"))
def dav_sinf_tanlandi(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    sinf_filter = call.data.replace("dav_sinf_", "")
    oq = [(sid, info) for sid, info in foydalanuvchilar.items()
          if info.get("rol") == "oquvchi" and info.get("holat") == "done"
          and (sinf_filter == "BARCHASI" or info.get("sinf") == sinf_filter)]

    if not oq:
        bot.send_message(call.message.chat.id,
            "Bu sinfda o'quvchi yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    davomat_temp[call.from_user.id] = {
        "sinf": sinf_filter,
        "oquvchilar": oq,
        "joriy": 0,
        "natijalar": [],
        "sana": str(datetime.date.today()),
    }

    bot.send_message(call.message.chat.id,
        f"📊 *Davomat belgilash* — {sinf_filter}\n"
        f"👥 Jami: {len(oq)} ta o'quvchi\n\n"
        f"Har bir o'quvchi uchun holatni tanlang 👇",
        parse_mode="Markdown")
    bot.answer_callback_query(call.id)
    _dav_keyingi_oquvchi(call.message.chat.id, call.from_user.id)

def _dav_keyingi_oquvchi(chat_id, domla_uid):
    temp = davomat_temp.get(domla_uid)
    if not temp: return
    idx = temp["joriy"]
    oq  = temp["oquvchilar"]

    if idx >= len(oq):
        _dav_yakunlash(chat_id, domla_uid)
        return

    sid, info = oq[idx]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Keldi",        callback_data=f"dav_hol_{domla_uid}_keldi"),
        types.InlineKeyboardButton("❌ Kelmadi",      callback_data=f"dav_hol_{domla_uid}_kelmadi"),
        types.InlineKeyboardButton("⏰ Kech keldi",   callback_data=f"dav_hol_{domla_uid}_kech"),
        types.InlineKeyboardButton("🤒 Sababli",      callback_data=f"dav_hol_{domla_uid}_sababli"),
    )
    bot.send_message(chat_id,
        f"👤 *{info['ism']}* ({info.get('sinf','—')})\n"
        f"📝 {idx+1}/{len(oq)} o'quvchi\n\nHolati?",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("dav_hol_"))
def dav_holat_belgilash(call):
    parts     = call.data.split("_")
    domla_uid = int(parts[2])
    holat     = parts[3]

    if call.from_user.id != domla_uid:
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    temp = davomat_temp.get(domla_uid)
    if not temp:
        bot.answer_callback_query(call.id, "Sessiya topilmadi.")
        return

    idx = temp["joriy"]
    sid, info = temp["oquvchilar"][idx]

    holat_nomi = {
        "keldi":   "✅ Keldi",
        "kelmadi": "❌ Kelmadi",
        "kech":    "⏰ Kech keldi",
        "sababli": "🤒 Sababli",
    }.get(holat, holat)

    yozuv = {
        "sana":      temp["sana"],
        "sinf":      info.get("sinf", "—"),
        "uid":       sid,
        "ism":       info.get("ism", "—"),
        "holat":     holat,
        "holat_nom": holat_nomi,
        "izoh":      "",
        "domla_uid": domla_uid,
    }
    temp["natijalar"].append(yozuv)
    temp["joriy"] += 1

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id,
        f"✅ *{info['ism']}* → {holat_nomi}", parse_mode="Markdown")
    bot.answer_callback_query(call.id)
    _dav_keyingi_oquvchi(call.message.chat.id, domla_uid)

def _dav_yakunlash(chat_id, domla_uid):
    temp = davomat_temp.pop(domla_uid, None)
    if not temp: return

    natijalar = temp["natijalar"]
    # Saqlash
    davomat_yozuvlari.extend(natijalar)

    keldi    = sum(1 for n in natijalar if n["holat"] == "keldi")
    kelmadi  = sum(1 for n in natijalar if n["holat"] == "kelmadi")
    kech     = sum(1 for n in natijalar if n["holat"] == "kech")
    sababli  = sum(1 for n in natijalar if n["holat"] == "sababli")

    text = (f"📊 *Davomat yakunlandi!*\n"
            f"📅 Sana: {temp['sana']} | Sinf: {temp['sinf']}\n\n"
            f"✅ Keldi:      *{keldi} ta*\n"
            f"❌ Kelmadi:    *{kelmadi} ta*\n"
            f"⏰ Kech keldi: *{kech} ta*\n"
            f"🤒 Sababli:   *{sababli} ta*\n"
            f"👥 Jami:       *{len(natijalar)} ta*\n\n")

    if kelmadi > 0 or kech > 0:
        text += "*Kelmagan/Kech kelganlar:*\n"
        for n in natijalar:
            if n["holat"] in ("kelmadi", "kech", "sababli"):
                text += f"• {n['ism']} — {n['holat_nom']}\n"

    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=domla_menyu())

    # Kelmagan o'quvchilarga xabar
    for n in natijalar:
        if n["holat"] == "kelmadi":
            try:
                bot.send_message(n["uid"],
                    f"⚠️ *Bugungi darsga kelmadingiz!*\n📅 Sana: {n['sana']}\n\n"
                    f"Sababini o'qituvchiga bildiring.", parse_mode="Markdown")
            except: pass

# ============================================================
# 🗓 DOMLA: DAVOMAT HISOBOTI (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🗓 Davomat hisoboti")
def davomat_hisoboti(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    if not davomat_yozuvlari:
        bot.send_message(message.chat.id,
            "📊 Hozircha davomat ma'lumoti yo'q.", reply_markup=domla_menyu())
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📋 Umumiy hisobot", callback_data="dav_hisobot_umumiy"),
        types.InlineKeyboardButton("👤 O'quvchi bo'yicha", callback_data="dav_hisobot_oquvchi"),
        types.InlineKeyboardButton("📅 Sana bo'yicha", callback_data="dav_hisobot_sana"),
    )
    bot.send_message(message.chat.id,
        "🗓 *Davomat hisoboti*\n\nQaysi ko'rinishda?",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "dav_hisobot_umumiy")
def dav_hisobot_umumiy(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    oq = [(sid, info) for sid, info in foydalanuvchilar.items()
          if info.get("rol") == "oquvchi" and info.get("holat") == "done"]

    text = "📋 *Umumiy davomat hisoboti:*\n\n"
    for sid, info in oq:
        mening = [d for d in davomat_yozuvlari if d["uid"] == sid]
        if not mening: continue
        keldi   = sum(1 for d in mening if d["holat"] == "keldi")
        jami    = len(mening)
        foiz    = int(keldi/jami*100) if jami else 0
        emoji   = "✅" if foiz >= 80 else ("⚠️" if foiz >= 60 else "❌")
        text += (f"{emoji} *{info['ism']}* ({info.get('sinf','—')})\n"
                 f"   📊 {keldi}/{jami} kun ({foiz}%)\n\n")

    if text == "📋 *Umumiy davomat hisoboti:*\n\n":
        text += "Ma'lumot yo'q."

    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "dav_hisobot_oquvchi")
def dav_hisobot_oquvchi_tanlash(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    oq = [(sid, info) for sid, info in foydalanuvchilar.items()
          if info.get("rol") == "oquvchi" and info.get("holat") == "done"]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for sid, info in oq:
        n = sum(1 for d in davomat_yozuvlari if d["uid"] == sid)
        if n > 0:
            markup.add(types.InlineKeyboardButton(
                f"👤 {info['ism']} ({info.get('sinf','—')}) — {n} kun",
                callback_data=f"dav_oquvchi_det_{sid}"))

    bot.send_message(call.message.chat.id,
        "O'quvchini tanlang:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("dav_oquvchi_det_"))
def dav_oquvchi_detail(call):
    if not is_domla(call.from_user.id): return
    uid = int(call.data.split("_")[3])
    u   = get_user(uid)
    mening = [d for d in davomat_yozuvlari if d["uid"] == uid]

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not mening:
        bot.send_message(call.message.chat.id, "Ma'lumot yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    keldi   = sum(1 for d in mening if d["holat"] == "keldi")
    kelmadi = sum(1 for d in mening if d["holat"] == "kelmadi")
    kech    = sum(1 for d in mening if d["holat"] == "kech")
    sababli = sum(1 for d in mening if d["holat"] == "sababli")
    jami    = len(mening)
    foiz    = int(keldi/jami*100) if jami else 0

    text = (f"👤 *{u.get('ism','—')}* ({u.get('sinf','—')})\n\n"
            f"📊 *Davomat:*\n"
            f"✅ Keldi:      {keldi} kun\n"
            f"❌ Kelmadi:    {kelmadi} kun\n"
            f"⏰ Kech keldi: {kech} kun\n"
            f"🤒 Sababli:   {sababli} kun\n"
            f"👥 Jami:       {jami} kun\n"
            f"📈 Foizi:      *{foiz}%*\n\n"
            f"*Oxirgi 10 kun:*\n")

    for d in reversed(mening[-10:]):
        text += f"📅 {d['sana']} — {d['holat_nom']}\n"

    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "dav_hisobot_sana")
def dav_hisobot_sana(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    # Noyob sanalar
    sanalar = sorted(set(d["sana"] for d in davomat_yozuvlari), reverse=True)[:10]

    if not sanalar:
        bot.send_message(call.message.chat.id, "Ma'lumot yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    for sana in sanalar:
        markup.add(types.InlineKeyboardButton(f"📅 {sana}", callback_data=f"dav_sana_det_{sana}"))

    bot.send_message(call.message.chat.id, "Sanani tanlang:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("dav_sana_det_"))
def dav_sana_detail(call):
    if not is_domla(call.from_user.id): return
    sana = call.data.replace("dav_sana_det_", "")
    kun_yozuvlari = [d for d in davomat_yozuvlari if d["sana"] == sana]

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    keldi   = [d for d in kun_yozuvlari if d["holat"] == "keldi"]
    kelmadi = [d for d in kun_yozuvlari if d["holat"] == "kelmadi"]
    kech    = [d for d in kun_yozuvlari if d["holat"] == "kech"]
    sababli = [d for d in kun_yozuvlari if d["holat"] == "sababli"]

    text = (f"📅 *{sana} — Davomat*\n\n"
            f"✅ Keldi ({len(keldi)} ta): {', '.join(d['ism'] for d in keldi) or '—'}\n\n"
            f"❌ Kelmadi ({len(kelmadi)} ta): {', '.join(d['ism'] for d in kelmadi) or '—'}\n\n"
            f"⏰ Kech keldi ({len(kech)} ta): {', '.join(d['ism'] for d in kech) or '—'}\n\n"
            f"🤒 Sababli ({len(sababli)} ta): {', '.join(d['ism'] for d in sababli) or '—'}\n")

    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)

# ============================================================
# 📅 DOMLA: DARS JADVALI BOSHQARUVI (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📅 Dars jadvali")
def dars_jadvali_menu(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ Yangi dars qo'shish",   callback_data="jadval_qosh"),
        types.InlineKeyboardButton("📋 Jadvalni ko'rish",      callback_data="jadval_kor"),
        types.InlineKeyboardButton("🗑 Darsni o'chirish",      callback_data="jadval_ochir"),
    )
    bot.send_message(message.chat.id,
        "📅 *Dars Jadvali*\n\nNima qilmoqchisiz?",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "jadval_qosh")
def jadval_dars_qosh(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    jadval_temp[call.from_user.id] = {}

    msg = bot.send_message(call.message.chat.id,
        "📅 *Yangi dars qo'shish*\n\n1️⃣ Sinf nomini kiriting:\n_(masalan: 9-A)_",
        parse_mode="Markdown", reply_markup=domla_menyu())
    bot.register_next_step_handler(msg, jadval_sinf_kirish)
    bot.answer_callback_query(call.id)

def jadval_sinf_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    jadval_temp[uid]["sinf"] = message.text.strip()

    # Kun tanlash
    markup = types.InlineKeyboardMarkup(row_width=3)
    for kun in KUNLAR:
        markup.add(types.InlineKeyboardButton(kun, callback_data=f"jadval_kun_{kun}_{uid}"))
    bot.send_message(message.chat.id,
        "2️⃣ Haftaning kunini tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: "jadval_kun_" in c.data)
def jadval_kun_tanlash(call):
    parts = call.data.split("_")
    kun   = parts[2]
    uid   = int(parts[3])
    if call.from_user.id != uid: return

    jadval_temp[uid]["kun"] = kun
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    msg = bot.send_message(call.message.chat.id,
        f"✅ Kun: *{kun}*\n\n3️⃣ Dars vaqtini kiriting:\n_(masalan: 08:00-09:30)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, jadval_soat_kirish)
    bot.answer_callback_query(call.id)

def jadval_soat_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    jadval_temp[uid]["soat"] = message.text.strip()

    msg = bot.send_message(message.chat.id,
        "4️⃣ Fan / Mavzu nomini kiriting:\n_(masalan: Nemis tili — Grammatika)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, jadval_fan_kirish)

def jadval_fan_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    jadval_temp[uid]["fan"] = message.text.strip()

    msg = bot.send_message(message.chat.id,
        "5️⃣ Xona raqamini kiriting _(ixtiyoriy, o'tkazish uchun — yozing)_:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, jadval_xona_saqlash)

def jadval_xona_saqlash(message):
    uid  = message.from_user.id
    if not is_domla(uid): return
    temp = jadval_temp.pop(uid, {})
    xona = "" if message.text.strip() == "—" else message.text.strip()

    sinf = temp.get("sinf", "—")
    dars = {
        "kun":  temp.get("kun", "—"),
        "soat": temp.get("soat", "—"),
        "fan":  temp.get("fan", "—"),
        "xona": xona,
    }

    if sinf not in dars_jadvali:
        dars_jadvali[sinf] = []
    dars_jadvali[sinf].append(dars)

    # Hafta tartibida saralash
    dars_jadvali[sinf].sort(key=lambda x: (KUNLAR.index(x["kun"]) if x["kun"] in KUNLAR else 99, x["soat"]))

    xona_text = f" | 🚪 {xona}" if xona else ""
    bot.send_message(message.chat.id,
        f"✅ *Dars qo'shildi!*\n\n"
        f"🏫 Sinf: *{sinf}*\n"
        f"📅 Kun: *{dars['kun']}*\n"
        f"⏰ Vaqt: *{dars['soat']}*\n"
        f"📚 Fan: *{dars['fan']}*"
        f"{xona_text}",
        parse_mode="Markdown", reply_markup=domla_menyu())

    # O'quvchilarga xabar
    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "oquvchi" and info.get("holat") == "done" and info.get("sinf") == sinf:
            try:
                bot.send_message(sid,
                    f"📅 *Dars jadvaliga yangi dars qo'shildi!*\n\n"
                    f"📅 *{dars['kun']}*, {dars['soat']}\n"
                    f"📚 {dars['fan']}"
                    f"{xona_text}",
                    parse_mode="Markdown")
            except: pass

@bot.callback_query_handler(func=lambda c: c.data == "jadval_kor")
def jadval_korsatish(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not dars_jadvali:
        bot.send_message(call.message.chat.id,
            "📅 Hozircha jadval yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    for sinf in sorted(dars_jadvali.keys()):
        n = len(dars_jadvali[sinf])
        markup.add(types.InlineKeyboardButton(
            f"🏫 {sinf} ({n} dars)", callback_data=f"jadval_sinf_kor_{sinf}"))

    bot.send_message(call.message.chat.id,
        "📅 Qaysi sinf jadvalini ko'rmoqchisiz?",
        reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("jadval_sinf_kor_"))
def jadval_sinf_detail(call):
    sinf = call.data.replace("jadval_sinf_kor_", "")
    darslar = dars_jadvali.get(sinf, [])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not darslar:
        bot.send_message(call.message.chat.id, "Bu sinf uchun jadval yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    text = f"📅 *{sinf} — Dars jadvali:*\n\n"
    joriy_kun = ""
    for d in darslar:
        if d["kun"] != joriy_kun:
            joriy_kun = d["kun"]
            text += f"\n📌 *{joriy_kun}*\n"
        xona = f" | 🚪 {d['xona']}" if d.get("xona") else ""
        text += f"   ⏰ {d['soat']} — {d['fan']}{xona}\n"

    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "jadval_ochir")
def jadval_ochirish(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not dars_jadvali:
        bot.send_message(call.message.chat.id, "Jadval bo'sh.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for sinf in sorted(dars_jadvali.keys()):
        for i, d in enumerate(dars_jadvali[sinf]):
            label = f"🗑 {sinf} | {d['kun']} {d['soat']} — {d['fan'][:20]}"
            markup.add(types.InlineKeyboardButton(label, callback_data=f"jadval_del_{sinf}_{i}"))

    bot.send_message(call.message.chat.id,
        "🗑 O'chirish uchun darsni tanlang:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("jadval_del_"))
def jadval_dars_ochir(call):
    if not is_domla(call.from_user.id): return
    parts = call.data.split("_")
    sinf  = parts[2]
    idx   = int(parts[3])

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if sinf in dars_jadvali and idx < len(dars_jadvali[sinf]):
        d = dars_jadvali[sinf].pop(idx)
        if not dars_jadvali[sinf]:
            del dars_jadvali[sinf]
        bot.send_message(call.message.chat.id,
            f"✅ *O'chirildi:*\n{sinf} | {d['kun']} {d['soat']} — {d['fan']}",
            parse_mode="Markdown", reply_markup=domla_menyu())
    else:
        bot.send_message(call.message.chat.id, "❌ Topilmadi.", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)

# ============================================================
# O'QUVCHI: DARS JADVALIM (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📅 Dars jadvalim")
def oquvchi_dars_jadvali(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return

    uid  = message.from_user.id
    u    = get_user(uid)
    sinf = u.get("sinf", "—")

    darslar = dars_jadvali.get(sinf, [])

    if not darslar:
        bot.send_message(message.chat.id,
            f"📅 *{sinf}* uchun jadval hali kiritilmagan.\n\nO'qituvchi jadval qo'shganda xabar keladi! 🔔",
            parse_mode="Markdown", reply_markup=oquvchi_menyu())
        return

    text = f"📅 *{sinf} — Dars jadvali:*\n\n"
    joriy_kun = ""
    for d in darslar:
        if d["kun"] != joriy_kun:
            joriy_kun = d["kun"]
            text += f"\n📌 *{joriy_kun}*\n"
        xona = f" | 🚪 {d['xona']}" if d.get("xona") else ""
        text += f"   ⏰ {d['soat']} — {d['fan']}{xona}\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())

# ============================================================
# O'QUVCHI: MENING DAVOMATIM (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📊 Mening davomatim")
def oquvchi_davomati(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return

    uid    = message.from_user.id
    mening = [d for d in davomat_yozuvlari if d["uid"] == uid]

    if not mening:
        bot.send_message(message.chat.id,
            "📊 Sizning davomatiz hali belgilanmagan.",
            reply_markup=oquvchi_menyu())
        return

    keldi   = sum(1 for d in mening if d["holat"] == "keldi")
    kelmadi = sum(1 for d in mening if d["holat"] == "kelmadi")
    kech    = sum(1 for d in mening if d["holat"] == "kech")
    sababli = sum(1 for d in mening if d["holat"] == "sababli")
    jami    = len(mening)
    foiz    = int(keldi / jami * 100) if jami else 0

    emoji = "✅" if foiz >= 80 else ("⚠️" if foiz >= 60 else "❌")

    text = (f"📊 *Mening davomatim*\n\n"
            f"{emoji} Davomat foizi: *{foiz}%*\n\n"
            f"✅ Keldi:       *{keldi} kun*\n"
            f"❌ Kelmadi:     *{kelmadi} kun*\n"
            f"⏰ Kech keldi:  *{kech} kun*\n"
            f"🤒 Sababli:    *{sababli} kun*\n"
            f"📅 Jami:        *{jami} kun*\n\n"
            f"*Oxirgi 10 kun:*\n")

    for d in reversed(mening[-10:]):
        text += f"📅 {d['sana']} — {d['holat_nom']}\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())

# ============================================================
# O'QUVCHI: BARCHA MAVJUD FUNKSIYALAR
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📚 Vazifalarni ko'rish")
def oquvchi_vazifalar(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    if not vazifalar:
        bot.send_message(message.chat.id,
            "📚 Hozircha vazifa yo'q. Kelganda xabar keladi! 🔔",
            reply_markup=oquvchi_menyu())
        return
    text = "📚 *Uy vazifalari:*\n\n"
    for v in reversed(vazifalar[-5:]):
        text += f"*№{v['id']}. {v['sarlavha']}*\n📝 {v['tavsif']}\n📅 {v['muddat']}\n─────────────────\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())

@bot.message_handler(func=lambda m: m.text == "📤 Vazifa topshirish")
def vazifa_topshirish_boshlash(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    if not vazifalar:
        bot.send_message(message.chat.id, "❌ Topshirish uchun vazifa yo'q.", reply_markup=oquvchi_menyu())
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for v in reversed(vazifalar[-5:]):
        markup.add(types.InlineKeyboardButton(
            f"📌 {v['sarlavha']}  |  ⏰ {v['muddat']}", callback_data=f"topshir_{v['id']}"))
    bot.send_message(message.chat.id, "📤 *Qaysi vazifani topshirmoqchisiz?*",
                     parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("topshir_"))
def vazifa_tanlandi(call):
    uid = call.from_user.id
    if not is_oquvchi(uid):
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return
    vazifa_id = int(call.data.split("_")[1])
    vazifa = next((v for v in vazifalar if v["id"] == vazifa_id), None)
    if not vazifa:
        bot.answer_callback_query(call.id, "Topilmadi.")
        return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    msg = bot.send_message(call.message.chat.id,
        f"📌 *{vazifa['sarlavha']}*\n📝 {vazifa['tavsif']}\n\n✍️ Javobingizni yozing:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: vazifa_javob_qabul(m, vazifa_id))
    bot.answer_callback_query(call.id)

def vazifa_javob_qabul(message, vazifa_id):
    uid  = message.from_user.id
    u    = get_user(uid)
    ism  = u.get("ism","Noma'lum") if u else "Noma'lum"
    sinf = u.get("sinf","—") if u else "—"
    vazifa = next((v for v in vazifalar if v["id"] == vazifa_id), None)
    t = {
        "vazifa_id":   vazifa_id,
        "vazifa_nomi": vazifa["sarlavha"] if vazifa else f"#{vazifa_id}",
        "oquvchi_id":  uid,
        "ism": ism, "sinf": sinf,
        "matn": message.text.strip(),
        "vaqt": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
        "baho": None, "izoh": None,
    }
    topshirishlar.append(t)
    bot.send_message(message.chat.id,
        f"✅ *Topshirildi!*\n📌 {t['vazifa_nomi']}\n🕐 {t['vaqt']}\n\n_Domla ko'rib chiqadi va baho qo'yadi._",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())
    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "domla" and info.get("holat") == "done":
            try:
                bot.send_message(sid,
                    f"📥 *Yangi topshirish!*\n👤 *{ism}* ({sinf})\n📌 {t['vazifa_nomi']}\n📝 {t['matn']}\n🕐 {t['vaqt']}",
                    parse_mode="Markdown")
            except: pass

@bot.message_handler(func=lambda m: m.text == "✅ Mening topshirishlarim")
def mening_topshirishlarim(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    uid = message.from_user.id
    mening = [t for t in topshirishlar if t["oquvchi_id"] == uid]
    if not mening:
        bot.send_message(message.chat.id, "📭 Hali topshirmagansiz.", reply_markup=oquvchi_menyu())
        return
    text = f"✅ *Mening topshirishlarim ({len(mening)} ta):*\n\n"
    for t in reversed(mening[-10:]):
        baho_text = t.get("baho") or "⏳ Baholanmagan"
        text += (f"📌 *{t['vazifa_nomi']}*\n"
                 f"📝 {t['matn'][:60]}...\n"
                 f"⭐ {baho_text}\n"
                 f"🕐 {t['vaqt']}\n─────────────────\n")
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())

@bot.message_handler(func=lambda m: m.text == "🧪 Testni boshlash")
def test_boshlash(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    uid = message.from_user.id
    if uid in aktiv_testlar:
        bot.send_message(message.chat.id,
            "⚠️ Siz allaqachon test yechmoqdasiz! Davom eting.", reply_markup=oquvchi_menyu())
        return
    if len(testlar) == 0:
        bot.send_message(message.chat.id,
            "❌ Hozircha savollar yo'q.", reply_markup=oquvchi_menyu())
        return
    tanlab = random.sample(testlar, min(10, len(testlar)))
    aktiv_testlar[uid] = {
        "savollar": tanlab, "joriy": 0, "ball": 0,
        "boshlanish": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
    }
    bot.send_message(message.chat.id,
        f"🧪 *Test boshlandi!*\n📝 {len(tanlab)} ta savol\nHar variantni tugmadan tanlang 👇",
        parse_mode="Markdown")
    test_savol_yuborish(message.chat.id, uid)

def test_savol_yuborish(chat_id, uid):
    sess = aktiv_testlar.get(uid)
    if not sess: return
    idx = sess["joriy"]
    if idx >= len(sess["savollar"]):
        test_yakunlash(chat_id, uid)
        return
    q = sess["savollar"][idx]
    harflar = ["A", "B", "C", "D"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i, v in enumerate(q["variantlar"]):
        markup.add(types.InlineKeyboardButton(
            f"{harflar[i]}) {v}", callback_data=f"test_jav_{i}_{uid}"))
    bot.send_message(chat_id,
        f"❓ *Savol {idx+1}/{len(sess['savollar'])}*\n\n{q['savol']}",
        parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("test_jav_"))
def test_javob(call):
    parts     = call.data.split("_")
    tanlangan = int(parts[2])
    uid       = int(parts[3])
    if call.from_user.id != uid:
        bot.answer_callback_query(call.id, "Bu sizning testingiz emas!")
        return
    sess = aktiv_testlar.get(uid)
    if not sess:
        bot.answer_callback_query(call.id, "Test topilmadi.")
        return
    q = sess["savollar"][sess["joriy"]]
    harflar = ["A", "B", "C", "D"]
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    if tanlangan == q["togri"]:
        sess["ball"] += 1
        fb = f"✅ *To'g'ri!* {harflar[tanlangan]}) {q['variantlar'][tanlangan]}"
    else:
        fb = (f"❌ *Noto'g'ri!*\n"
              f"Siz: {harflar[tanlangan]}) {q['variantlar'][tanlangan]}\n"
              f"To'g'ri: {harflar[q['togri']]}) {q['variantlar'][q['togri']]}")
    bot.send_message(call.message.chat.id, fb, parse_mode="Markdown")
    sess["joriy"] += 1
    bot.answer_callback_query(call.id)
    test_savol_yuborish(call.message.chat.id, uid)

def test_yakunlash(chat_id, uid):
    sess = aktiv_testlar.pop(uid, None)
    if not sess: return
    u    = get_user(uid)
    ism  = u.get("ism","—") if u else "—"
    sinf = u.get("sinf","—") if u else "—"
    ball = sess["ball"]
    jami = len(sess["savollar"])
    foiz = int(ball/jami*100) if jami else 0
    baho_text = test_baho(ball, jami)
    natija = {
        "uid": uid, "ism": ism, "sinf": sinf,
        "ball": ball, "jami": jami, "baho": baho_text,
        "vaqt": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
    }
    test_natijalari.append(natija)
    baholar.append({
        "uid": uid, "ism": ism, "sinf": sinf,
        "tur": "🧪 Test / Nazorat",
        "ball": ball, "max_ball": jami, "foiz": foiz,
        "baho": baho_text, "izoh": "Avtomatik test natijasi",
        "sana": str(datetime.date.today()),
        "domla": "Bot (avtomatik)",
    })
    bot.send_message(chat_id,
        f"🏁 *Test yakunlandi!*\n\n"
        f"👤 {ism} ({sinf})\n"
        f"🎯 Natija: *{ball}/{jami}* ({foiz}%)\n"
        f"📋 Baho: *{baho_text}*",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())
    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "domla" and info.get("holat") == "done":
            try:
                bot.send_message(sid,
                    f"📊 *Test natijasi!*\n👤 *{ism}* ({sinf})\n🎯 {ball}/{jami} ({foiz}%) — {baho_text}",
                    parse_mode="Markdown")
            except: pass

@bot.message_handler(func=lambda m: m.text == "🏆 Mening natijalarim")
def mening_natijalarim(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    uid    = message.from_user.id
    mening = [n for n in test_natijalari if n["uid"] == uid]
    if not mening:
        bot.send_message(message.chat.id,
            "🏆 Hali test yechmadingiz.", reply_markup=oquvchi_menyu())
        return
    eng_yaxshi = max(mening, key=lambda x: x["ball"])
    balllar = [n["ball"] for n in mening]
    jamilar = [n["jami"] for n in mening]
    ort = sum(b/j*100 for b,j in zip(balllar,jamilar))/len(mening)
    text = (f"🏆 *Test natijalarim*\n\n"
            f"📝 Urinishlar: *{len(mening)} ta*\n"
            f"📈 O'rtacha: *{ort:.1f}%*\n"
            f"🥇 Eng yaxshi: *{eng_yaxshi['ball']}/{eng_yaxshi['jami']}*\n\n"
            f"*Oxirgi 5 ta:*\n")
    for n in reversed(mening[-5:]):
        foiz = int(n['ball']/n['jami']*100) if n['jami'] else 0
        text += f"• {n['ball']}/{n['jami']} ({foiz}%) — {n['vaqt']}\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())

@bot.message_handler(func=lambda m: m.text == "📋 Mening baholarim")
def mening_baholarim(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    uid    = message.from_user.id
    mening = [b for b in baholar if b["uid"] == uid]
    if not mening:
        bot.send_message(message.chat.id,
            "📋 Sizda hali baho yo'q.\n\nVazifa topshiring yoki test yeching! 📝",
            reply_markup=oquvchi_menyu())
        return
    foizlar  = [b["ball"]/b["max_ball"]*100 for b in mening if b["max_ball"]>0]
    ort_foiz = sum(foizlar)/len(foizlar) if foizlar else 0
    vazifa_b  = [b for b in mening if "vazifa" in b["tur"].lower()]
    test_b    = [b for b in mening if "test" in b["tur"].lower()]
    dars_b    = [b for b in mening if "dars" in b["tur"].lower()]
    faollik_b = [b for b in mening if "faollik" in b["tur"].lower()]
    text = (f"📋 *Mening baholarim*\n\n"
            f"📊 *Umumiy statistika:*\n"
            f"   🔢 Jami baholar: *{len(mening)} ta*\n"
            f"   📈 O'rtacha: *{ort_foiz:.1f}%* — {ball_baho(ort_foiz, 100)}\n"
            f"   📝 Uy vazifasi: {len(vazifa_b)} ta\n"
            f"   🧪 Test: {len(test_b)} ta\n"
            f"   💬 Dars javobi: {len(dars_b)} ta\n"
            f"   🌟 Faollik: {len(faollik_b)} ta\n\n"
            f"*Oxirgi 10 ta baho:*\n\n")
    for b in reversed(mening[-10:]):
        izoh = f"\n   💬 {b['izoh']}" if b.get("izoh") else ""
        text += (f"{b['tur']}\n"
                 f"   🎯 *{b['ball']}/{b['max_ball']}* ({b['foiz']}%) — *{b['baho']}*"
                 f"{izoh}\n"
                 f"   📅 {b['sana']}\n\n")
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())

@bot.message_handler(func=lambda m: m.text == "👤 Mening profilim")
def mening_profilim(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    uid = message.from_user.id
    u   = get_user(uid)
    topsh_soni = sum(1 for t in topshirishlar if t["oquvchi_id"] == uid)
    nat_soni   = sum(1 for n in test_natijalari if n["uid"] == uid)
    baho_soni  = sum(1 for b in baholar if b["uid"] == uid)
    ort_baho   = _ortacha_baho(uid)
    # Davomat
    dav_mening = [d for d in davomat_yozuvlari if d["uid"] == uid]
    keldi_soni = sum(1 for d in dav_mening if d["holat"] == "keldi")
    dav_foiz   = f"{int(keldi_soni/len(dav_mening)*100)}%" if dav_mening else "—"
    bot.send_message(message.chat.id,
        f"👤 *Profil*\n\n"
        f"📛 Ism:  *{u.get('ism','—')}*\n"
        f"🏫 Sinf: *{u.get('sinf','—')}*\n"
        f"📅 Qo'shilgan: {u.get('qoshilgan','—')}\n\n"
        f"📊 *Statistika:*\n"
        f"   ✅ Topshirgan vazifalar: *{topsh_soni} ta*\n"
        f"   🧪 Yechilgan testlar: *{nat_soni} ta*\n"
        f"   ⭐ Jami baholar: *{baho_soni} ta*\n"
        f"   📈 O'rtacha baho: *{ort_baho}*\n"
        f"   📊 Davomat: *{dav_foiz}*",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())

# ============================================================
# 🎓 DOMLA: KURSLARNI BOSHQARISH (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🎓 Kurslarni boshqarish")
def kurslar_boshqarish(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ Yangi kurs yaratish",      callback_data="kurs_yarat"),
        types.InlineKeyboardButton("📋 Barcha kurslar",           callback_data="kurs_royxat"),
        types.InlineKeyboardButton("👥 Kurs a'zolari",            callback_data="kurs_azolar"),
        types.InlineKeyboardButton("🔴 Kursni yopish/ochish",     callback_data="kurs_togri"),
    )
    bot.send_message(message.chat.id,
        "🎓 *Kurslarni boshqarish*\n\nNima qilmoqchisiz?",
        parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == "kurs_yarat")
def kurs_yaratish_boshlash(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    kurs_temp[call.from_user.id] = {}
    msg = bot.send_message(call.message.chat.id,
        "➕ *Yangi kurs yaratish*\n\n1️⃣ Kurs nomini kiriting:\n_(masalan: Nemis tili — Boshlang'ich daraja)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, kurs_nom_kirish)
    bot.answer_callback_query(call.id)


def kurs_nom_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    kurs_temp[uid]["nomi"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "2️⃣ Kurs haqida qisqacha tavsif yozing:")
    bot.register_next_step_handler(msg, kurs_tavsif_kirish)


def kurs_tavsif_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    kurs_temp[uid]["tavsif"] = message.text.strip()
    msg = bot.send_message(message.chat.id,
        "3️⃣ Kurs narxini kiriting:\n_(masalan: 500 000 so'm yoki Bepul)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, kurs_narx_kirish)


def kurs_narx_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    kurs_temp[uid]["narx"] = message.text.strip()
    msg = bot.send_message(message.chat.id,
        "4️⃣ Kurs muddatini kiriting:\n_(masalan: 3 oy, 1 yil, Doimiy)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, kurs_muddat_kirish)


def kurs_muddat_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    kurs_temp[uid]["muddat"] = message.text.strip()
    msg = bot.send_message(message.chat.id,
        "5️⃣ Maksimal o'rinlar sonini kiriting:\n_(cheksiz bo'lsa: 0 yozing)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, kurs_joylar_kirish)


def kurs_joylar_kirish(message):
    uid  = message.from_user.id
    if not is_domla(uid): return
    try:
        joylar = int(message.text.strip())
    except:
        joylar = 0
    kurs_temp[uid]["joylar"] = joylar

    # Endi dars kunlarini tanlash
    kurs_temp[uid]["dars_kunlari"] = []
    _kurs_kun_tanlash_yuborish(message.chat.id, uid)


def _kurs_kun_tanlash_yuborish(chat_id, uid):
    """Hafta kunlarini tanlash - multiple select"""
    temp     = kurs_temp.get(uid, {})
    tanlangan = temp.get("dars_kunlari", [])

    KUNLAR_LIST = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    for kun in KUNLAR_LIST:
        check = "✅ " if kun in tanlangan else ""
        markup.add(types.InlineKeyboardButton(
            f"{check}{kun}", callback_data=f"kurskun_{kun}_{uid}"))
    markup.add(types.InlineKeyboardButton(
        "➡️ Davom etish", callback_data=f"kurskun_done_{uid}"))

    tanlangan_text = ", ".join(tanlangan) if tanlangan else "hali tanlanmagan"
    bot.send_message(chat_id,
        f"6️⃣ *Dars kunlarini tanlang* (bir nechta bo'lishi mumkin):\n\n"
        f"✅ Tanlangan: *{tanlangan_text}*\n\n"
        f"Tugatgandan so'ng ➡️ Davom etish ni bosing:",
        parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("kurskun_") and not c.data.startswith("kurskun_done_"))
def kurs_kun_toggle(call):
    parts = call.data.split("_")
    kun   = parts[1]
    uid   = int(parts[2])

    if call.from_user.id != uid:
        bot.answer_callback_query(call.id, "Ruxsat yo'q.")
        return

    temp = kurs_temp.get(uid)
    if not temp:
        bot.answer_callback_query(call.id, "Sessiya topilmadi.")
        return

    kunlar = temp.get("dars_kunlari", [])
    if kun in kunlar:
        kunlar.remove(kun)
    else:
        kunlar.append(kun)
    temp["dars_kunlari"] = kunlar

    # Xabarni yangilash
    KUNLAR_LIST = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    for k in KUNLAR_LIST:
        check = "✅ " if k in kunlar else ""
        markup.add(types.InlineKeyboardButton(
            f"{check}{k}", callback_data=f"kurskun_{k}_{uid}"))
    markup.add(types.InlineKeyboardButton(
        "➡️ Davom etish", callback_data=f"kurskun_done_{uid}"))

    tanlangan_text = ", ".join(kunlar) if kunlar else "hali tanlanmagan"
    try:
        bot.edit_message_text(
            f"6️⃣ *Dars kunlarini tanlang* (bir nechta bo'lishi mumkin):\n\n"
            f"✅ Tanlangan: *{tanlangan_text}*\n\n"
            f"Tugatgandan so'ng ➡️ Davom etish ni bosing:",
            call.message.chat.id, call.message.message_id,
            parse_mode="Markdown", reply_markup=markup)
    except: pass
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("kurskun_done_"))
def kurs_kun_done(call):
    uid  = int(call.data.split("_")[2])
    if call.from_user.id != uid: return

    temp = kurs_temp.get(uid)
    if not temp:
        bot.answer_callback_query(call.id, "Sessiya topilmadi.")
        return

    kunlar = temp.get("dars_kunlari", [])
    if not kunlar:
        bot.answer_callback_query(call.id, "⚠️ Kamida bitta kun tanlang!", show_alert=True)
        return

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    # Har bir kun uchun vaqt so'rash
    temp["kun_vaqtlari"] = {}
    temp["kunlar_queue"] = list(kunlar)  # navbat
    bot.answer_callback_query(call.id)
    _kurs_kun_vaqt_sorash(call.message.chat.id, uid)


def _kurs_kun_vaqt_sorash(chat_id, uid):
    """Navbatdagi kun uchun vaqt so'raydi"""
    temp  = kurs_temp.get(uid)
    queue = temp.get("kunlar_queue", [])

    if not queue:
        # Barchasi tugadi — kurs saqlash
        _kurs_saqlash(chat_id, uid)
        return

    kun = queue[0]
    msg = bot.send_message(chat_id,
        f"⏰ *{kun}* kuni uchun dars vaqtini kiriting:\n"
        f"_(masalan: 09:00-11:00 yoki 14:00-16:00)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: _kurs_vaqt_qabul(m, uid, kun))


def _kurs_vaqt_qabul(message, uid, kun):
    temp = kurs_temp.get(uid)
    if not temp: return

    vaqt = message.text.strip()
    temp["kun_vaqtlari"][kun] = vaqt
    temp["kunlar_queue"].pop(0)

    _kurs_kun_vaqt_sorash(message.chat.id, uid)


def _kurs_saqlash(chat_id, uid):
    """Kursni oxirida saqlaydi"""
    temp = kurs_temp.pop(uid, {})

    # Dars jadvali matnini shakllantirish
    kun_vaqtlari  = temp.get("kun_vaqtlari", {})
    jadval_qatorlar = []
    TARTIB = ["Dushanba","Seshanba","Chorshanba","Payshanba","Juma","Shanba","Yakshanba"]
    for k in TARTIB:
        if k in kun_vaqtlari:
            jadval_qatorlar.append({"kun": k, "vaqt": kun_vaqtlari[k]})

    joylar = temp.get("joylar", 0)
    kurs = {
        "id":        len(kurslar) + 1,
        "nomi":      temp.get("nomi", "—"),
        "tavsif":    temp.get("tavsif", "—"),
        "narx":      temp.get("narx", "—"),
        "muddat":    temp.get("muddat", "—"),
        "joylar":    joylar,
        "jadval":    jadval_qatorlar,   # [{kun, vaqt}]
        "sana":      str(datetime.date.today()),
        "aktiv":     True,
    }
    kurslar.append(kurs)

    joy_text    = f"{joylar} ta o'rin" if joylar > 0 else "Cheksiz"
    jadval_text = "\n".join(f"📅 {j['kun']}: ⏰ {j['vaqt']}" for j in jadval_qatorlar)

    bot.send_message(chat_id,
        f"✅ *Kurs yaratildi!*\n\n"
        f"🎓 *{kurs['nomi']}*\n"
        f"📝 {kurs['tavsif']}\n"
        f"💰 Narx: {kurs['narx']}\n"
        f"⏳ Muddat: {kurs['muddat']}\n"
        f"👥 O'rinlar: {joy_text}\n\n"
        f"*Dars jadvali:*\n{jadval_text}",
        parse_mode="Markdown", reply_markup=domla_menyu())

    # O'quvchilarga xabar
    sent = 0
    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "oquvchi" and info.get("holat") == "done":
            try:
                bot.send_message(sid,
                    f"🎓 *Yangi kurs ochildi!*\n\n"
                    f"📚 *{kurs['nomi']}*\n"
                    f"📝 {kurs['tavsif']}\n"
                    f"💰 Narx: {kurs['narx']}\n"
                    f"⏳ Muddat: {kurs['muddat']}\n\n"
                    f"*Dars jadvali:*\n{jadval_text}\n\n"
                    f"Yozilish uchun: *Kurslarga yozilish* tugmasini bosing! 👇",
                    parse_mode="Markdown")
                sent += 1
            except: pass
    if sent:
        bot.send_message(chat_id, f"📣 {sent} ta o'quvchiga xabar yuborildi.")


@bot.callback_query_handler(func=lambda c: c.data == "kurs_royxat")
def kurs_royxat_korsatish(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not kurslar:
        bot.send_message(call.message.chat.id,
            "🎓 Hozircha kurs yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    text = "📋 *Barcha kurslar:*\n\n"
    for k in kurslar:
        yozilganlar = sum(1 for a in kurs_arizalar
                          if a["kurs_id"] == k["id"] and a["holat"] == "tasdiqlandi")
        kutayotgan  = sum(1 for a in kurs_arizalar
                          if a["kurs_id"] == k["id"] and a["holat"] == "kutilmoqda")
        holat    = "🟢 Aktiv" if k["aktiv"] else "🔴 Yopiq"
        joy_text = f"{k['joylar']} ta" if k["joylar"] > 0 else "Cheksiz"
        jadval   = k.get("jadval", [])
        jadval_text = " | ".join(f"{j['kun']} {j['vaqt']}" for j in jadval) if jadval else "—"
        text += (f"*№{k['id']}. {k['nomi']}*\n"
                 f"📝 {k['tavsif']}\n"
                 f"💰 {k['narx']} | ⏳ {k['muddat']}\n"
                 f"📅 Jadval: {jadval_text}\n"
                 f"👥 O'rinlar: {joy_text} | ✅ Yozildi: {yozilganlar} | ⏳ Kutmoqda: {kutayotgan}\n"
                 f"📌 Holat: {holat}\n"
                 f"─────────────────\n")

    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "kurs_azolar")
def kurs_azolar_tanlash(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not kurslar:
        bot.send_message(call.message.chat.id, "Kurs yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for k in kurslar:
        n = sum(1 for a in kurs_arizalar if a["kurs_id"] == k["id"] and a["holat"] == "tasdiqlandi")
        markup.add(types.InlineKeyboardButton(
            f"🎓 {k['nomi']} — {n} a'zo", callback_data=f"kurs_azolar_det_{k['id']}"))

    bot.send_message(call.message.chat.id, "Kursni tanlang:", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("kurs_azolar_det_"))
def kurs_azolar_detail(call):
    if not is_domla(call.from_user.id): return
    kurs_id = int(call.data.split("_")[3])
    kurs    = next((k for k in kurslar if k["id"] == kurs_id), None)
    azolar  = [a for a in kurs_arizalar if a["kurs_id"] == kurs_id and a["holat"] == "tasdiqlandi"]
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not azolar:
        bot.send_message(call.message.chat.id,
            f"🎓 *{kurs['nomi']}*\n\nHali a'zo yo'q.", parse_mode="Markdown", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    text = f"👥 *{kurs['nomi']} — A'zolar ({len(azolar)} ta):*\n\n"
    for i, a in enumerate(azolar, 1):
        text += f"{i}. *{a['ism']}* ({a.get('sinf','—')}) — 📅 {a['vaqt']}\n"

    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "kurs_togri")
def kurs_togri_tanlash(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not kurslar:
        bot.send_message(call.message.chat.id, "Kurs yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for k in kurslar:
        holat = "🟢" if k["aktiv"] else "🔴"
        markup.add(types.InlineKeyboardButton(
            f"{holat} {k['nomi']}", callback_data=f"kurs_togri_switch_{k['id']}"))

    bot.send_message(call.message.chat.id,
        "Kursni tanlang (holati o'zgaradi):", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("kurs_togri_switch_"))
def kurs_holat_switch(call):
    if not is_domla(call.from_user.id): return
    kurs_id = int(call.data.split("_")[3])
    kurs    = next((k for k in kurslar if k["id"] == kurs_id), None)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if kurs:
        kurs["aktiv"] = not kurs["aktiv"]
        holat = "🟢 Aktiv" if kurs["aktiv"] else "🔴 Yopiq"
        bot.send_message(call.message.chat.id,
            f"✅ *{kurs['nomi']}* — {holat}",
            parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)


# ============================================================
# 📨 DOMLA: KURS ARIZALARI — TO'LOV TASDIQLASH (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📨 Kurs arizalari")
def kurs_arizalari_korsatish(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    kutayotganlar = [a for a in kurs_arizalar if a["holat"] == "kutilmoqda"]

    if not kutayotganlar:
        # Tarixni ko'rish imkoni
        jami = len(kurs_arizalar)
        bot.send_message(message.chat.id,
            f"📨 *Kurs arizalari*\n\n"
            f"⏳ Kutayotgan ariza yo'q.\n"
            f"📋 Jami arizalar: {jami} ta",
            parse_mode="Markdown", reply_markup=domla_menyu())
        return

    text = f"📨 *Kutayotgan arizalar ({len(kutayotganlar)} ta):*\n\n"
    markup = types.InlineKeyboardMarkup(row_width=2)

    for a in kutayotganlar[-10:]:
        text += (f"👤 *{a['ism']}* ({a.get('sinf','—')})\n"
                 f"🎓 {a['kurs_nomi']}\n"
                 f"🕐 {a['vaqt']}\n\n")
        markup.add(
            types.InlineKeyboardButton(f"✅ {a['ism'][:12]}", callback_data=f"ariza_tasd_{a['id']}"),
            types.InlineKeyboardButton(f"❌ Rad", callback_data=f"ariza_rad_{a['id']}"),
        )

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("ariza_tasd_"))
def ariza_tasdiqlash(call):
    if not is_domla(call.from_user.id): return
    ariza_id = int(call.data.split("_")[2])
    ariza    = next((a for a in kurs_arizalar if a["id"] == ariza_id), None)

    if not ariza:
        bot.answer_callback_query(call.id, "Ariza topilmadi.")
        return
    if ariza["holat"] != "kutilmoqda":
        bot.answer_callback_query(call.id, "Bu ariza allaqachon ko'rib chiqilgan.")
        return

    ariza["holat"] = "tasdiqlandi"
    ariza["izoh"]  = "Domla tomonidan tasdiqlandi"

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id,
        f"✅ *Tasdiqlandi!*\n"
        f"👤 {ariza['ism']} — 🎓 {ariza['kurs_nomi']}\n"
        f"📅 {ariza.get('kun','—')}  ⏰ {ariza.get('vaqt','—')}",
        parse_mode="Markdown", reply_markup=domla_menyu())

    # O'quvchiga xabar
    try:
        kurs = next((k for k in kurslar if k["id"] == ariza["kurs_id"]), None)
        bot.send_message(ariza["uid"],
            f"🎉 *Tabriklaymiz! Kursga qabul qilindingiz!*\n\n"
            f"🎓 *{ariza['kurs_nomi']}*\n"
            f"📅 Kun: *{ariza.get('kun','—')}*  ⏰ *{ariza.get('vaqt','—')}*\n"
            f"✅ Holat: Tasdiqlandi\n\n"
            f"Birinchi darsda ko'rishguncha! 👋",
            parse_mode="Markdown")
    except: pass
    bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")


@bot.callback_query_handler(func=lambda c: c.data.startswith("ariza_rad_"))
def ariza_rad_etish(call):
    if not is_domla(call.from_user.id): return
    ariza_id = int(call.data.split("_")[2])
    ariza    = next((a for a in kurs_arizalar if a["id"] == ariza_id), None)

    if not ariza:
        bot.answer_callback_query(call.id, "Ariza topilmadi.")
        return
    if ariza["holat"] != "kutilmoqda":
        bot.answer_callback_query(call.id, "Bu ariza allaqachon ko'rib chiqilgan.")
        return

    # Rad sababi so'rash
    msg = bot.send_message(call.message.chat.id,
        f"❌ *Rad etish*\n👤 {ariza['ism']} — {ariza['kurs_nomi']}\n\n"
        f"Rad etish sababini yozing _(ixtiyoriy, o'tkazish uchun — yozing)_:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: ariza_rad_sabab(m, ariza_id))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.answer_callback_query(call.id)


def ariza_rad_sabab(message, ariza_id):
    sabab = "" if message.text.strip() == "—" else message.text.strip()
    ariza = next((a for a in kurs_arizalar if a["id"] == ariza_id), None)
    if not ariza: return

    ariza["holat"] = "rad_etildi"
    ariza["izoh"]  = sabab or "Rad etildi"

    bot.send_message(message.chat.id,
        f"❌ *Rad etildi.*\n👤 {ariza['ism']} — {ariza['kurs_nomi']}",
        parse_mode="Markdown", reply_markup=domla_menyu())

    # O'quvchiga xabar
    try:
        sabab_qism = f"\n💬 Sabab: {sabab}" if sabab else ""
        bot.send_message(ariza["uid"],
            f"❌ *Afsuski, arizangiz rad etildi.*\n\n"
            f"🎓 {ariza['kurs_nomi']}"
            f"{sabab_qism}\n\n"
            f"Qo'shimcha ma'lumot uchun o'qituvchiga murojaat qiling.",
            parse_mode="Markdown")
    except: pass


# ============================================================
# 🎓 O'QUVCHI: KURSLARGA YOZILISH (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🎓 Kurslarga yozilish")
def oquvchi_kurslarga_yozilish(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return

    aktiv_kurslar = [k for k in kurslar if k["aktiv"]]
    if not aktiv_kurslar:
        bot.send_message(message.chat.id,
            "🎓 Hozircha ochiq kurs yo'q.\n\nYangi kurslar haqida xabar keladi! 🔔",
            reply_markup=oquvchi_menyu())
        return

    uid    = message.from_user.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    for k in aktiv_kurslar:
        mavjud = next((a for a in kurs_arizalar
                       if a["kurs_id"] == k["id"] and a["uid"] == uid), None)
        if mavjud:
            emoji = {"kutilmoqda": "⏳", "tasdiqlandi": "✅", "rad_etildi": "❌"}.get(mavjud["holat"], "?")
            markup.add(types.InlineKeyboardButton(
                f"{emoji} {k['nomi']} [{mavjud['holat']}]",
                callback_data=f"kurs_info_{k['id']}"))
        else:
            yozilganlar = sum(1 for a in kurs_arizalar
                              if a["kurs_id"] == k["id"] and a["holat"] == "tasdiqlandi")
            joy_ok = k["joylar"] == 0 or yozilganlar < k["joylar"]
            if joy_ok:
                markup.add(types.InlineKeyboardButton(
                    f"🎓 {k['nomi']} — {k['narx']}",
                    callback_data=f"kurs_yozil_{k['id']}"))
            else:
                markup.add(types.InlineKeyboardButton(
                    f"🔴 {k['nomi']} — To'lgan",
                    callback_data=f"kurs_info_{k['id']}"))

    bot.send_message(message.chat.id,
        "🎓 *Mavjud kurslar:*\n\nYozilmoqchi bo'lgan kursni tanlang 👇",
        parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("kurs_info_"))
def kurs_info_korsatish(call):
    kurs_id = int(call.data.split("_")[2])
    kurs    = next((k for k in kurslar if k["id"] == kurs_id), None)
    if not kurs:
        bot.answer_callback_query(call.id, "Topilmadi.")
        return
    uid    = call.from_user.id
    mavjud = next((a for a in kurs_arizalar
                   if a["kurs_id"] == kurs_id and a["uid"] == uid), None)
    holat_map = {
        "kutilmoqda":  "⏳ Arizangiz ko'rib chiqilmoqda",
        "tasdiqlandi": "✅ Qabul qilindingiz!",
        "rad_etildi":  "❌ Ariza rad etildi",
    }
    holat_text = holat_map.get(mavjud["holat"], "—") if mavjud else "—"
    jadval     = kurs.get("jadval", [])
    jadval_text = "\n".join(f"  📅 {j['kun']}: ⏰ {j['vaqt']}" for j in jadval) if jadval else "  —"
    bot.answer_callback_query(call.id,
        f"🎓 {kurs['nomi']}\n💰 {kurs['narx']}\n📌 Sizning holat: {holat_text}",
        show_alert=True)


@bot.callback_query_handler(func=lambda c: c.data.startswith("kurs_yozil_"))
def kurs_yozilish_boshlash(call):
    """Kurs tanlanganda — jadval kunlarini ko'rsatadi"""
    kurs_id = int(call.data.split("_")[2])
    kurs    = next((k for k in kurslar if k["id"] == kurs_id), None)
    uid     = call.from_user.id

    if not kurs:
        bot.answer_callback_query(call.id, "Kurs topilmadi.")
        return

    mavjud = next((a for a in kurs_arizalar
                   if a["kurs_id"] == kurs_id and a["uid"] == uid), None)
    if mavjud:
        bot.answer_callback_query(call.id,
            f"Allaqachon ariza bergansiz. Holat: {mavjud['holat']}", show_alert=True)
        return

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    jadval = kurs.get("jadval", [])
    yozilganlar = sum(1 for a in kurs_arizalar
                      if a["kurs_id"] == kurs_id and a["holat"] == "tasdiqlandi")
    joy_text    = f"{kurs['joylar'] - yozilganlar} ta bo'sh o'rin" if kurs["joylar"] > 0 else "Cheksiz"

    # Kurs haqida ma'lumot + dars kunlarini tugma sifatida ko'rsatish
    jadval_text = "\n".join(f"📅 {j['kun']}: ⏰ {j['vaqt']}" for j in jadval) if jadval else "—"

    markup = types.InlineKeyboardMarkup(row_width=1)
    for j in jadval:
        markup.add(types.InlineKeyboardButton(
            f"📅 {j['kun']}  ⏰ {j['vaqt']}",
            callback_data=f"kursvaxt_{kurs_id}_{j['kun']}"))
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="kurs_ariza_bekor"))

    bot.send_message(call.message.chat.id,
        f"🎓 *{kurs['nomi']}*\n\n"
        f"📝 {kurs['tavsif']}\n"
        f"💰 Narx: *{kurs['narx']}*\n"
        f"⏳ Muddat: *{kurs['muddat']}*\n"
        f"👥 Bo'sh o'rin: {joy_text}\n\n"
        f"*Dars kunlari va vaqtlari:*\n{jadval_text}\n\n"
        f"👇 Qaysi kunda qatnashmoqchisiz — tanlang:",
        parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("kursvaxt_"))
def kurs_kun_tanlandi(call):
    """O'quvchi kun/vaqt tanladi — telefon so'raydi"""
    parts   = call.data.split("_")
    kurs_id = int(parts[1])
    kun     = "_".join(parts[2:])   # kun nomi (masalan "Dushanba")
    uid     = call.from_user.id

    kurs = next((k for k in kurslar if k["id"] == kurs_id), None)
    if not kurs:
        bot.answer_callback_query(call.id, "Xatolik.")
        return

    # Tanlangan vaqtni topamiz
    jadval_entry = next((j for j in kurs.get("jadval", []) if j["kun"] == kun), None)
    vaqt = jadval_entry["vaqt"] if jadval_entry else "—"

    # Temp saqlaymiz
    kurs_temp[uid] = {
        "kurs_id":    kurs_id,
        "kurs_nomi":  kurs["nomi"],
        "tanlangan_kun":  kun,
        "tanlangan_vaqt": vaqt,
    }

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id,
        f"✅ Tanlangan: *{kun}* — ⏰ *{vaqt}*\n\n"
        f"📞 Endi telefon raqamingizni kiriting:\n"
        f"_(masalan: +998 90 123 45 67)_",
        parse_mode="Markdown")
    bot.answer_callback_query(call.id)

    # Keyingi qadam — telefon
    bot.register_next_step_handler(call.message, lambda m: kurs_telefon_qabul(m, uid))


def kurs_telefon_qabul(message, uid):
    """Telefon raqamini qabul qiladi va ariza yuboradi"""
    telefon = message.text.strip()

    # Oddiy tekshiruv
    if len(telefon) < 7:
        msg = bot.send_message(message.chat.id,
            "❌ Telefon raqam noto'g'ri. Qayta kiriting:\n_(masalan: +998901234567)_",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, lambda m: kurs_telefon_qabul(m, uid))
        return

    temp = kurs_temp.pop(uid, {})
    if not temp:
        bot.send_message(message.chat.id, "❌ Sessiya tugagan. Qaytadan bosing.",
                         reply_markup=oquvchi_menyu())
        return

    u       = get_user(uid)
    kurs_id = temp["kurs_id"]
    kurs    = next((k for k in kurslar if k["id"] == kurs_id), None)

    ariza = {
        "id":         len(kurs_arizalar) + 1,
        "kurs_id":    kurs_id,
        "kurs_nomi":  temp["kurs_nomi"],
        "uid":        uid,
        "ism":        u.get("ism", "—") if u else "—",
        "sinf":       u.get("sinf", "—") if u else "—",
        "telefon":    telefon,
        "kun":        temp.get("tanlangan_kun", "—"),
        "vaqt":       temp.get("tanlangan_vaqt", "—"),
        "holat":      "kutilmoqda",
        "izoh":       "",
        "vaqt_yuborildi": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
    }
    kurs_arizalar.append(ariza)

    bot.send_message(message.chat.id,
        f"📨 *Arizangiz yuborildi!*\n\n"
        f"🎓 *{ariza['kurs_nomi']}*\n"
        f"📅 Kun: *{ariza['kun']}*  ⏰ *{ariza['vaqt']}*\n"
        f"📞 Telefon: {telefon}\n"
        f"⏳ Holat: Ko'rib chiqilmoqda\n\n"
        f"O'qituvchi tasdiqlashi bilanoq xabar keladi. 🔔",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())

    # Domlaga xabar
    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "domla" and info.get("holat") == "done":
            try:
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ariza_tasd_{ariza['id']}"),
                    types.InlineKeyboardButton("❌ Rad etish",  callback_data=f"ariza_rad_{ariza['id']}"),
                )
                bot.send_message(sid,
                    f"📨 *Yangi kurs arizasi!*\n\n"
                    f"👤 *{ariza['ism']}* ({ariza['sinf']})\n"
                    f"📞 Tel: {telefon}\n"
                    f"🎓 {ariza['kurs_nomi']}\n"
                    f"📅 {ariza['kun']}  ⏰ {ariza['vaqt']}\n"
                    f"🕐 {ariza['vaqt_yuborildi']}",
                    parse_mode="Markdown", reply_markup=markup)
            except: pass


@bot.callback_query_handler(func=lambda c: c.data == "kurs_ariza_bekor")
def kurs_ariza_bekor(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, "Bekor qilindi.", reply_markup=oquvchi_menyu())
    bot.answer_callback_query(call.id)


# compat stub — eski callback bo'lsa ishlaydi
@bot.callback_query_handler(func=lambda c: c.data.startswith("kurs_ariza_jo_"))
def kurs_ariza_jo_eski(call):
    bot.answer_callback_query(call.id, "Iltimos, qaytadan kursni tanlang.")
    bot.send_message(call.message.chat.id,
        "⚠️ Sessiya tugagan. *Kurslarga yozilish* tugmasini qayta bosing.",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())


# ============================================================
# 📜 O'QUVCHI: MENING KURSLARIM (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📜 Mening kurslarim")
def oquvchi_mening_kurslari(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return

    uid    = message.from_user.id
    mening = [a for a in kurs_arizalar if a["uid"] == uid]

    if not mening:
        bot.send_message(message.chat.id,
            "📜 Siz hali hech qanday kursga ariza bermagansiz.\n\n"
            "Kurslarga yozilish uchun *Kurslarga yozilish* tugmasini bosing! 🎓",
            parse_mode="Markdown", reply_markup=oquvchi_menyu())
        return

    holat_map = {
        "kutilmoqda":  "⏳ Ko'rib chiqilmoqda",
        "tasdiqlandi": "✅ Qabul qilindi",
        "rad_etildi":  "❌ Rad etildi",
    }

    text = f"📜 *Mening kurslarim ({len(mening)} ta ariza):*\n\n"
    for a in reversed(mening):
        holat = holat_map.get(a["holat"], a["holat"])
        izoh  = f"\n   💬 {a['izoh']}" if a.get("izoh") else ""
        kun_vaqt = f"\n   📅 {a.get('kun','—')}  ⏰ {a.get('vaqt','—')}" if a.get("kun") else ""
        tel = f"\n   📞 {a.get('telefon','—')}" if a.get("telefon") else ""
        text += (f"🎓 *{a['kurs_nomi']}*\n"
                 f"   📌 {holat}{kun_vaqt}{tel}{izoh}\n"
                 f"   🕐 {a.get('vaqt_yuborildi', a.get('vaqt','—'))}\n\n")

    # Kursdan chiqish imkoni (faqat kutilmoqdalar uchun)
    kutayotgan = [a for a in mening if a["holat"] == "kutilmoqda"]
    if kutayotgan:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for a in kutayotgan:
            markup.add(types.InlineKeyboardButton(
                f"🚫 {a['kurs_nomi'][:30]} — Arizani bekor qilish",
                callback_data=f"kurs_chiq_{a['id']}"))
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())


@bot.callback_query_handler(func=lambda c: c.data.startswith("kurs_chiq_"))
def kurs_arizani_bekor(call):
    ariza_id = int(call.data.split("_")[2])
    uid      = call.from_user.id
    ariza    = next((a for a in kurs_arizalar
                     if a["id"] == ariza_id and a["uid"] == uid), None)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    if not ariza or ariza["holat"] != "kutilmoqda":
        bot.send_message(call.message.chat.id,
            "❌ Ariza topilmadi yoki allaqachon ko'rib chiqilgan.",
            reply_markup=oquvchi_menyu())
        bot.answer_callback_query(call.id)
        return

    ariza["holat"] = "rad_etildi"
    ariza["izoh"]  = "O'quvchi tomonidan bekor qilindi"

    bot.send_message(call.message.chat.id,
        f"✅ *{ariza['kurs_nomi']}* kursiga ariza bekor qilindi.",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())
    bot.answer_callback_query(call.id)


# ============================================================


# ============================================================
# 💰 DOMLA: TO'LOVLARNI BOSHQARISH (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "💰 To'lovlarni boshqarish")
def tolov_boshqarish(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ To'lov qo'shish",      callback_data="tolov_qosh"),
        types.InlineKeyboardButton("📋 Barcha to'lovlar",     callback_data="tolov_barchasi"),
        types.InlineKeyboardButton("⏳ Kutayotgan to'lovlar", callback_data="tolov_kutayotgan"),
        types.InlineKeyboardButton("👤 O'quvchi bo'yicha",    callback_data="tolov_oquvchi"),
    )
    bot.send_message(message.chat.id,
        "💰 *To'lovlarni boshqarish*\n\nNima qilmoqchisiz?",
        parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == "tolov_qosh")
def tolov_qosh_boshlash(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    oq = [(sid, info) for sid, info in foydalanuvchilar.items()
          if info.get("rol") == "oquvchi" and info.get("holat") == "done"]
    if not oq:
        bot.send_message(call.message.chat.id, "O'quvchi yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for sid, info in oq:
        markup.add(types.InlineKeyboardButton(
            f"👤 {info['ism']} ({info.get('sinf','—')})",
            callback_data=f"tolov_uid_{sid}"))
    bot.send_message(call.message.chat.id,
        "➕ *To'lov qo'shish*\n\nO'quvchini tanlang:",
        parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tolov_uid_"))
def tolov_oquvchi_tanlandi(call):
    if not is_domla(call.from_user.id): return
    uid_oquvchi = int(call.data.split("_")[2])
    tolov_temp[call.from_user.id] = {"oquvchi_id": uid_oquvchi}
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💵 Kurs to'lovi",      callback_data="tolov_tur_kurs"),
        types.InlineKeyboardButton("📚 Kitob/material",    callback_data="tolov_tur_material"),
        types.InlineKeyboardButton("📝 Ro'yxatdan o'tish", callback_data="tolov_tur_royxat"),
        types.InlineKeyboardButton("🔄 Qayta to'lov",      callback_data="tolov_tur_qayta"),
        types.InlineKeyboardButton("💡 Boshqa",            callback_data="tolov_tur_boshqa"),
    )
    u = get_user(uid_oquvchi)
    bot.send_message(call.message.chat.id,
        f"👤 *{u.get('ism','—')}*\n\nTo'lov turini tanlang:",
        parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tolov_tur_"))
def tolov_tur_tanlandi(call):
    if not is_domla(call.from_user.id): return
    tur_map = {
        "tolov_tur_kurs":     "💵 Kurs to'lovi",
        "tolov_tur_material": "📚 Kitob/material",
        "tolov_tur_royxat":   "📝 Ro'yxatdan o'tish",
        "tolov_tur_qayta":    "🔄 Qayta to'lov",
        "tolov_tur_boshqa":   "💡 Boshqa",
    }
    tur = tur_map.get(call.data, "Boshqa")
    tolov_temp[call.from_user.id]["tur"] = tur
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    msg = bot.send_message(call.message.chat.id,
        f"Tur: *{tur}*\n\nTo'lov summasini kiriting:\n_(masalan: 500 000 so'm)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, tolov_summa_kirish)
    bot.answer_callback_query(call.id)


def tolov_summa_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    tolov_temp[uid]["summa"] = message.text.strip()
    msg = bot.send_message(message.chat.id,
        "💬 Izoh yozing _(ixtiyoriy, o'tkazish uchun — yozing)_:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, tolov_izoh_saqlash)


def tolov_izoh_saqlash(message):
    uid  = message.from_user.id
    if not is_domla(uid): return
    temp = tolov_temp.pop(uid, {})
    izoh = "" if message.text.strip() == "—" else message.text.strip()

    oquvchi_id = temp.get("oquvchi_id")
    oquvchi    = get_user(oquvchi_id)
    domla      = get_user(uid)

    yozuv = {
        "id":    len(tolov_tarix) + 1,
        "uid":   oquvchi_id,
        "ism":   oquvchi.get("ism", "—") if oquvchi else "—",
        "sinf":  oquvchi.get("sinf", "—") if oquvchi else "—",
        "summa": temp.get("summa", "—"),
        "tur":   temp.get("tur", "—"),
        "izoh":  izoh,
        "holat": "tasdiqlandi",
        "sana":  str(datetime.date.today()),
        "domla": domla.get("ism", "Domla") if domla else "Domla",
    }
    tolov_tarix.append(yozuv)

    bot.send_message(message.chat.id,
        f"✅ *To'lov qo'shildi!*\n\n"
        f"👤 {yozuv['ism']} ({yozuv['sinf']})\n"
        f"💰 {yozuv['summa']}\n"
        f"📂 {yozuv['tur']}\n"
        f"📅 {yozuv['sana']}",
        parse_mode="Markdown", reply_markup=domla_menyu())

    try:
        izoh_qism = f"\n💬 {izoh}" if izoh else ""
        bot.send_message(oquvchi_id,
            f"✅ *To'lovingiz tasdiqlandi!*\n\n"
            f"💰 Summa: *{yozuv['summa']}*\n"
            f"📂 Tur: {yozuv['tur']}"
            f"{izoh_qism}\n"
            f"📅 {yozuv['sana']}",
            parse_mode="Markdown")
    except: pass


@bot.callback_query_handler(func=lambda c: c.data == "tolov_barchasi")
def tolov_barchasi_korsatish(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    if not tolov_tarix:
        bot.send_message(call.message.chat.id, "💰 Hozircha to'lov yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return
    text = "💰 *Barcha to'lovlar (oxirgi 20 ta):*\n\n"
    for t in reversed(tolov_tarix[-20:]):
        text += (f"👤 *{t['ism']}* ({t.get('sinf','—')})\n"
                 f"   💵 {t['summa']} | {t['tur']}\n"
                 f"   📅 {t['sana']}\n\n")
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "tolov_kutayotgan")
def tolov_kutayotgan_korsatish(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    kutayotgan = [t for t in tolov_tarix if t["holat"] == "kutilmoqda"]
    if not kutayotgan:
        bot.send_message(call.message.chat.id, "⏳ Kutayotgan to'lov yo'q.", reply_markup=domla_menyu())
        bot.answer_callback_query(call.id)
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    text = f"⏳ *Kutayotgan to'lovlar ({len(kutayotgan)} ta):*\n\n"
    for t in kutayotgan:
        text += f"👤 *{t['ism']}* — {t['summa']}\n"
        markup.add(
            types.InlineKeyboardButton(f"✅ {t['ism'][:12]}", callback_data=f"tolov_tasd_{t['id']}"),
            types.InlineKeyboardButton("❌ Rad",               callback_data=f"tolov_rad_{t['id']}"),
        )
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tolov_tasd_"))
def tolov_tasdiqlash(call):
    if not is_domla(call.from_user.id): return
    tolov_id = int(call.data.split("_")[2])
    t = next((x for x in tolov_tarix if x["id"] == tolov_id), None)
    if t:
        t["holat"] = "tasdiqlandi"
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id,
            f"✅ To'lov tasdiqlandi: *{t['ism']}* — {t['summa']}",
            parse_mode="Markdown", reply_markup=domla_menyu())
        try:
            bot.send_message(t["uid"],
                f"✅ *To'lovingiz tasdiqlandi!*\n💰 {t['summa']}\n📅 {t['sana']}",
                parse_mode="Markdown")
        except: pass
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tolov_rad_"))
def tolov_rad(call):
    if not is_domla(call.from_user.id): return
    tolov_id = int(call.data.split("_")[2])
    t = next((x for x in tolov_tarix if x["id"] == tolov_id), None)
    if t:
        t["holat"] = "rad_etildi"
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id,
            f"❌ Rad etildi: *{t['ism']}*", parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "tolov_oquvchi")
def tolov_oquvchi_tanlash(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    oq = [(sid, info) for sid, info in foydalanuvchilar.items()
          if info.get("rol") == "oquvchi" and info.get("holat") == "done"]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for sid, info in oq:
        n = sum(1 for t in tolov_tarix if t["uid"] == sid)
        if n > 0:
            markup.add(types.InlineKeyboardButton(
                f"👤 {info['ism']} ({info.get('sinf','—')}) — {n} ta to'lov",
                callback_data=f"tolov_oquvchi_det_{sid}"))
    if not markup.keyboard:
        bot.send_message(call.message.chat.id, "To'lov yozilmagan.", reply_markup=domla_menyu())
    else:
        bot.send_message(call.message.chat.id, "O'quvchini tanlang:", reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("tolov_oquvchi_det_"))
def tolov_oquvchi_detail(call):
    if not is_domla(call.from_user.id): return
    uid_oq = int(call.data.split("_")[3])
    u      = get_user(uid_oq)
    mening = [t for t in tolov_tarix if t["uid"] == uid_oq]
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    text = f"👤 *{u.get('ism','—')}* ({u.get('sinf','—')}) — To'lov tarixi\n\n"
    for t in reversed(mening):
        text += f"💵 *{t['summa']}* | {t['tur']} | 📅 {t['sana']}\n"
        if t.get("izoh"):
            text += f"   💬 {t['izoh']}\n"
        text += "\n"
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=domla_menyu())
    bot.answer_callback_query(call.id)


# ============================================================
# 💳 O'QUVCHI: TO'LOV TARIXI (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "💳 To'lov tarixim")
def oquvchi_tolov_tarixi(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    uid    = message.from_user.id
    mening = [t for t in tolov_tarix if t["uid"] == uid]
    if not mening:
        bot.send_message(message.chat.id,
            "💳 Sizda hali to'lov tarixi yo'q.", reply_markup=oquvchi_menyu())
        return
    text = f"💳 *To'lov tarixim ({len(mening)} ta):*\n\n"
    for t in reversed(mening[-15:]):
        holat_emoji = {"tasdiqlandi": "✅", "kutilmoqda": "⏳", "rad_etildi": "❌"}.get(t["holat"], "•")
        izoh = f"\n   💬 {t['izoh']}" if t.get("izoh") else ""
        text += (f"{holat_emoji} *{t['summa']}*\n"
                 f"   📂 {t['tur']}\n"
                 f"   📅 {t['sana']}{izoh}\n\n")
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())


# ============================================================
# 📣 DOMLA: E'LON YUBORISH (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📣 E'lon yuborish")
def elon_yuborish_boshlash(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return
    elon_temp[message.from_user.id] = {}
    msg = bot.send_message(message.chat.id,
        "📣 *Yangi e'lon*\n\n1️⃣ E'lon sarlavhasini yozing:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, elon_sarlavha_kirish)


def elon_sarlavha_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    elon_temp[uid]["sarlavha"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "2️⃣ E'lon matnini yozing:")
    bot.register_next_step_handler(msg, elon_matn_kirish)


def elon_matn_kirish(message):
    uid = message.from_user.id
    if not is_domla(uid): return
    elon_temp[uid]["matn"] = message.text.strip()
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔴 Ha, muhim!", callback_data="elon_muhim_ha"),
        types.InlineKeyboardButton("⚪ Oddiy",      callback_data="elon_muhim_yoq"),
    )
    bot.send_message(message.chat.id, "3️⃣ Bu e'lon muhimmi?", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data.startswith("elon_muhim_"))
def elon_muhim_tanlash(call):
    if not is_domla(call.from_user.id): return
    uid   = call.from_user.id
    muhim = call.data == "elon_muhim_ha"
    temp  = elon_temp.pop(uid, {})
    domla = get_user(uid)

    elon = {
        "id":       len(elonlar) + 1,
        "sarlavha": temp.get("sarlavha", "—"),
        "matn":     temp.get("matn", "—"),
        "domla":    domla.get("ism", "Domla") if domla else "Domla",
        "sana":     str(datetime.date.today()),
        "vaqt":     datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
        "muhim":    muhim,
    }
    elonlar.append(elon)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    muhim_text = "🔴 MUHIM" if muhim else "📣"
    bot.send_message(call.message.chat.id,
        f"✅ *E'lon yuborildi!*\n\n{muhim_text} *{elon['sarlavha']}*",
        parse_mode="Markdown", reply_markup=domla_menyu())

    sent = 0
    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "oquvchi" and info.get("holat") == "done":
            try:
                prefix = "🔴 *MUHIM E'LON!*" if muhim else "📣 *Yangi e'lon*"
                bot.send_message(sid,
                    f"{prefix}\n\n📌 *{elon['sarlavha']}*\n\n{elon['matn']}\n\n"
                    f"👨‍🏫 {elon['domla']} | 📅 {elon['vaqt']}",
                    parse_mode="Markdown")
                sent += 1
            except: pass
    if sent:
        bot.send_message(call.message.chat.id, f"📣 {sent} ta o'quvchiga yuborildi.")
    bot.answer_callback_query(call.id, "✅ E'lon yuborildi!")


# ============================================================
# 📣 O'QUVCHI: E'LONLAR (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📣 E'lonlar")
def oquvchi_elonlar(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    if not elonlar:
        bot.send_message(message.chat.id, "📣 Hozircha e'lon yo'q.", reply_markup=oquvchi_menyu())
        return
    text = "📣 *So'nggi e'lonlar:*\n\n"
    for e in reversed(elonlar[-10:]):
        muhim_prefix = "🔴 *MUHIM!* " if e.get("muhim") else ""
        text += (f"{muhim_prefix}*{e['sarlavha']}*\n"
                 f"{e['matn']}\n"
                 f"📅 {e['vaqt']}\n"
                 f"─────────────────\n")
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=oquvchi_menyu())


# ============================================================
# 🏅 REYTING (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🏅 Reyting")
def reyting_korsatish(message):
    if require_auth(message): return

    oq = [(sid, info) for sid, info in foydalanuvchilar.items()
          if info.get("rol") == "oquvchi" and info.get("holat") == "done"]

    menyu = domla_menyu() if is_domla(message.from_user.id) else oquvchi_menyu()

    if not oq:
        bot.send_message(message.chat.id, "🏅 Hozircha o'quvchi yo'q.", reply_markup=menyu)
        return

    natijalar = []
    for sid, info in oq:
        test_n   = [n for n in test_natijalari if n["uid"] == sid]
        test_ort = sum(n["ball"]/n["jami"]*100 for n in test_n if n["jami"]) / len(test_n) if test_n else 0

        baholar_n = [b for b in baholar if b["uid"] == sid and b["max_ball"] > 0]
        baho_ort  = sum(b["ball"]/b["max_ball"]*100 for b in baholar_n) / len(baholar_n) if baholar_n else 0

        dav_n    = [d for d in davomat_yozuvlari if d["uid"] == sid]
        keldi    = sum(1 for d in dav_n if d["holat"] == "keldi")
        dav_foiz = keldi / len(dav_n) * 100 if dav_n else 0

        umumiy = test_ort * 0.4 + baho_ort * 0.4 + dav_foiz * 0.2
        natijalar.append({
            "sid":      sid,
            "ism":      info["ism"],
            "sinf":     info.get("sinf", "—"),
            "test_ort": round(test_ort, 1),
            "baho_ort": round(baho_ort, 1),
            "dav_foiz": round(dav_foiz, 1),
            "umumiy":   round(umumiy, 1),
        })

    natijalar.sort(key=lambda x: x["umumiy"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    text   = "🏅 *OQUV MARKAZI REYTINGI*\n\n"

    for i, n in enumerate(natijalar[:10], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        me    = " ◀️ Sen" if n["sid"] == message.from_user.id else ""
        text += (f"{medal} *{n['ism']}* ({n['sinf']}){me}\n"
                 f"   🎯 Umumiy: *{n['umumiy']}%*\n"
                 f"   🧪 {n['test_ort']}% | ⭐ {n['baho_ort']}% | 📊 {n['dav_foiz']}%\n\n")

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=menyu)


# ============================================================
# 📞 O'QUVCHI: ADMIN BILAN BOG'LANISH (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📞 Admin bilan bog'lanish")
def admin_boglanish(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    msg = bot.send_message(message.chat.id,
        "📞 *Admin bilan bog'lanish*\n\n"
        "Savolingiz yoki muammoingizni yozing.\n"
        "O'qituvchi imkon qadar tez javob beradi 👇",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, admin_xabar_yuborish)


def admin_xabar_yuborish(message):
    uid = message.from_user.id
    u   = get_user(uid)
    xabar = {
        "id":         len(admin_xabarlar) + 1,
        "uid":        uid,
        "ism":        u.get("ism", "—") if u else "—",
        "sinf":       u.get("sinf", "—") if u else "—",
        "matn":       message.text.strip(),
        "javob":      None,
        "vaqt":       datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
        "javob_vaqt": None,
    }
    admin_xabarlar.append(xabar)
    bot.send_message(message.chat.id,
        "✅ *Xabaringiz yuborildi!*\n\nO'qituvchi javob berganda xabar keladi. 🔔",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())

    for sid, info in foydalanuvchilar.items():
        if info.get("rol") == "domla" and info.get("holat") == "done":
            try:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    "💬 Javob berish", callback_data=f"admin_javob_{xabar['id']}"))
                bot.send_message(sid,
                    f"📬 *Yangi xabar!*\n\n"
                    f"👤 *{xabar['ism']}* ({xabar['sinf']})\n"
                    f"💬 {xabar['matn']}\n"
                    f"🕐 {xabar['vaqt']}",
                    parse_mode="Markdown", reply_markup=markup)
            except: pass


# ============================================================
# 📬 DOMLA: ADMIN XABARLARI (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "📬 Admin xabarlari")
def admin_xabarlar_korsatish(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    if not admin_xabarlar:
        bot.send_message(message.chat.id, "📬 Hozircha xabar yo'q.", reply_markup=domla_menyu())
        return

    javobsiz = [x for x in admin_xabarlar if not x["javob"]]
    javobli  = [x for x in admin_xabarlar if x["javob"]]

    text   = (f"📬 *Admin xabarlari*\n\n"
              f"⏳ Javobsiz: {len(javobsiz)} ta | ✅ Javob berilgan: {len(javobli)} ta\n\n")
    markup = types.InlineKeyboardMarkup(row_width=1)

    for x in reversed(admin_xabarlar[-15:]):
        holat = "✅" if x["javob"] else "⏳"
        text += (f"{holat} *{x['ism']}* ({x['sinf']})\n"
                 f"   💬 {x['matn'][:60]}{'...' if len(x['matn'])>60 else ''}\n"
                 f"   🕐 {x['vaqt']}\n\n")
        if not x["javob"]:
            markup.add(types.InlineKeyboardButton(
                f"💬 Javob → {x['ism'][:15]}", callback_data=f"admin_javob_{x['id']}"))

    bot.send_message(message.chat.id, text, parse_mode="Markdown",
                     reply_markup=markup if markup.keyboard else domla_menyu())


@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_javob_"))
def admin_javob_boshlash(call):
    if not is_domla(call.from_user.id): return
    xabar_id = int(call.data.split("_")[2])
    xabar    = next((x for x in admin_xabarlar if x["id"] == xabar_id), None)
    if not xabar:
        bot.answer_callback_query(call.id, "Xabar topilmadi.")
        return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    msg = bot.send_message(call.message.chat.id,
        f"💬 *Javob yozish*\n\n"
        f"👤 {xabar['ism']}: _{xabar['matn']}_\n\n"
        f"Javobingizni yozing:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: admin_javob_yuborish(m, xabar_id))
    bot.answer_callback_query(call.id)


def admin_javob_yuborish(message, xabar_id):
    uid   = message.from_user.id
    if not is_domla(uid): return
    xabar = next((x for x in admin_xabarlar if x["id"] == xabar_id), None)
    if not xabar: return

    xabar["javob"]      = message.text.strip()
    xabar["javob_vaqt"] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    domla = get_user(uid)

    bot.send_message(message.chat.id,
        f"✅ *Javob yuborildi!*\n👤 {xabar['ism']}",
        parse_mode="Markdown", reply_markup=domla_menyu())
    try:
        bot.send_message(xabar["uid"],
            f"📬 *O'qituvchidan javob!*\n\n"
            f"Sizning savolingiz:\n_{xabar['matn']}_\n\n"
            f"✅ *Javob:*\n{xabar['javob']}\n\n"
            f"👨‍🏫 {domla.get('ism','Domla') if domla else 'Domla'} | 📅 {xabar['javob_vaqt']}",
            parse_mode="Markdown")
    except: pass


# ============================================================
# 🔑 O'QUVCHI: PAROLNI O'ZGARTIRISH
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🔑 Parolni o'zgartirish")
def oquvchi_parol_ozgartirish(message):
    if require_auth(message): return
    if not is_oquvchi(message.from_user.id): return
    msg = bot.send_message(message.chat.id,
        "🔑 *Parolni o'zgartirish*\n\n"
        "Avval *joriy parolingizni* kiriting:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, oquvchi_eski_parol_tekshir)


def oquvchi_eski_parol_tekshir(message):
    uid = message.from_user.id
    u   = get_user(uid)
    if message.text.strip() != u.get("parol", ""):
        bot.send_message(message.chat.id,
            "❌ *Joriy parol noto'g'ri!*",
            parse_mode="Markdown", reply_markup=oquvchi_menyu())
        return
    msg = bot.send_message(message.chat.id,
        "✅ To'g'ri!\n\n🔐 *Yangi parolingizni* kiriting:\n_(kamida 4 ta belgi)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, oquvchi_yangi_parol_kirish)


def oquvchi_yangi_parol_kirish(message):
    uid   = message.from_user.id
    parol = message.text.strip()
    if len(parol) < 4:
        msg = bot.send_message(message.chat.id,
            "❌ Kamida 4 ta belgi kiriting:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, oquvchi_yangi_parol_kirish)
        return
    foydalanuvchilar[uid]["parol_temp"] = parol
    msg = bot.send_message(message.chat.id,
        "🔐 Yangi parolni *qayta kiriting* _(tasdiqlash)_:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, oquvchi_yangi_parol_tasdiqlash)


def oquvchi_yangi_parol_tasdiqlash(message):
    uid   = message.from_user.id
    u     = foydalanuvchilar.get(uid, {})
    parol = message.text.strip()
    if parol != u.get("parol_temp", ""):
        msg = bot.send_message(message.chat.id,
            "❌ *Parollar mos kelmadi!* Qayta kiriting:",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, oquvchi_yangi_parol_kirish)
        return
    foydalanuvchilar[uid]["parol"] = parol
    foydalanuvchilar[uid].pop("parol_temp", None)
    bot.send_message(message.chat.id,
        f"✅ *Parol muvaffaqiyatli o'zgartirildi!*\n\n"
        f"🔐 Yangi parol: `{parol}`\n\n"
        f"⚠️ _Parolingizni yodda saqlang!_",
        parse_mode="Markdown", reply_markup=oquvchi_menyu())


# ============================================================
# 🔑 DOMLA: PAROLLARNI SOZLASH (YANGI)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🔑 Parollarni sozlash")
def parol_sozlash(message):
    if require_auth(message): return
    if not is_domla(message.from_user.id): return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            f"👨‍🏫 O'qituvchi paroli: [{DOMLA_PAROLI}]",
            callback_data="parol_domla"),
        types.InlineKeyboardButton(
            f"👨‍🎓 O'quvchi paroli: [{OQUVCHI_PAROLI}]",
            callback_data="parol_oquvchi"),
    )
    bot.send_message(message.chat.id,
        "🔑 *Parollarni sozlash*\n\n"
        "Qaysi parolni o'zgartirmoqchisiz?\n\n"
        "⚠️ _Parol o'zgartirilgandan so'ng eski parol ishlamaydi!_",
        parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda c: c.data == "parol_domla")
def parol_domla_ozgartir(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    msg = bot.send_message(call.message.chat.id,
        "👨‍🏫 *O'qituvchi uchun yangi parol kiriting:*\n_(kamida 6 ta belgi)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, _saqlash_domla_parol)
    bot.answer_callback_query(call.id)


def _saqlash_domla_parol(message):
    if not is_domla(message.from_user.id): return
    global DOMLA_PAROLI
    yangi = message.text.strip()
    if len(yangi) < 4:
        msg = bot.send_message(message.chat.id,
            "❌ Parol juda qisqa. Kamida 4 ta belgi kiriting:")
        bot.register_next_step_handler(msg, _saqlash_domla_parol)
        return
    DOMLA_PAROLI = yangi
    bot.send_message(message.chat.id,
        f"✅ *O'qituvchi paroli yangilandi!*\n\n🔐 Yangi parol: `{DOMLA_PAROLI}`\n\n"
        f"⚠️ Ushbu parolni o'qituvchilarga xabar qiling.",
        parse_mode="Markdown", reply_markup=domla_menyu())


@bot.callback_query_handler(func=lambda c: c.data == "parol_oquvchi")
def parol_oquvchi_ozgartir(call):
    if not is_domla(call.from_user.id): return
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    msg = bot.send_message(call.message.chat.id,
        "👨‍🎓 *O'quvchi uchun yangi parol kiriting:*\n_(kamida 4 ta belgi)_",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, _saqlash_oquvchi_parol)
    bot.answer_callback_query(call.id)


def _saqlash_oquvchi_parol(message):
    if not is_domla(message.from_user.id): return
    global OQUVCHI_PAROLI
    yangi = message.text.strip()
    if len(yangi) < 4:
        msg = bot.send_message(message.chat.id,
            "❌ Parol juda qisqa. Kamida 4 ta belgi kiriting:")
        bot.register_next_step_handler(msg, _saqlash_oquvchi_parol)
        return
    OQUVCHI_PAROLI = yangi
    bot.send_message(message.chat.id,
        f"✅ *O'quvchi paroli yangilandi!*\n\n🔐 Yangi parol: `{OQUVCHI_PAROLI}`\n\n"
        f"⚠️ Ushbu parolni o'quvchilarga xabar qiling.",
        parse_mode="Markdown", reply_markup=domla_menyu())


# ============================================================
# NOMA'LUM XABAR
# ============================================================


@bot.message_handler(func=lambda m: True)
def noma_lum(message):
    uid = message.from_user.id
    if not is_registered(uid):
        bot.send_message(message.chat.id, "👋 /start bosing.",
                         reply_markup=types.ReplyKeyboardRemove())
    elif is_domla(uid):
        bot.send_message(message.chat.id, "❓ Menyudan tanlang.", reply_markup=domla_menyu())
    else:
        bot.send_message(message.chat.id, "❓ Menyudan tanlang.", reply_markup=oquvchi_menyu())

# ============================================================
# ISHGA TUSHIRISH
# ============================================================

if __name__ == "__main__":
    print("🏫 OQUV MARKAZI BOTI ishga tushdi!")
    print(f"🔐 O'qituvchi paroli : {DOMLA_PAROLI}")
    print(f"🔐 O'quvchi paroli   : {OQUVCHI_PAROLI}")
    print("✅ Barcha funksiyalar faol")
    print("🛑 To'xtatish: Ctrl+C\n")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)