"""Single-city TAXICHI BOLA menu and configurable public information."""
import re
import logging
from pathlib import Path
from hashlib import sha256
from html import escape
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from bot.presentation import menu_button
from bot.contact_info import PHONE, ADMIN, CHANNEL, ADDRESS, MAP_URL

logger = logging.getLogger(__name__)
OFFICE_PHOTO = Path(__file__).resolve().parents[1] / 'templates' / 'office.jpg'

MENU_DRIVER = "📝 Ulanish uchun Ariza"
MENU_BRAND = "🎨 Brend Ariza"
MENU_OFFICE = "📍 Ofis manzili"
MENU_CONTACT = "📞 Bog‘lanish"


def main_keyboard(region=None):
    return ReplyKeyboardMarkup([
        [menu_button(MENU_DRIVER, icon='DRIVER')],
        [menu_button(MENU_BRAND, icon='BRAND')],
        [menu_button(MENU_OFFICE, icon='LOCATION'), menu_button(MENU_CONTACT, icon='CONTACT')],
    ], resize_keyboard=True)


MAIN_KEYBOARD = main_keyboard()
WELCOME_TEXT = (
    "🚖 <b>TAXICHI BOLA’ga xush kelibsiz!</b>\n\n"
    "Wildberries Taxi’da ishlash uchun arizangizni shu yerda qoldiring. "
    "Hujjatlarni yuboring — operatorlarimiz murojaatingizni ko‘rib chiqadi.\n\n"
    "📝 <b>Ulanish uchun ariza</b> — hujjatlaringizni yuborib, ro‘yxatdan o‘tish.\n"
    "🎨 <b>Brend ariza</b> — avtomobilni brendlash uchun murojaat.\n"
    "📍 <b>Ofis manzili</b> — manzil va xarita.\n"
    "📞 <b>Bog‘lanish</b> — operator bilan aloqa.\n\nKerakli bo‘limni tanlang:"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_chat.type != 'private':
        return ConversationHandler.END
    context.user_data.clear()
    await update.effective_message.reply_text(WELCOME_TEXT, parse_mode='HTML', reply_markup=main_keyboard())
    return ConversationHandler.END


async def show_contact(update, context):
    context.user_data.clear()
    text = ('📞 <b>TAXICHI BOLA — Bog‘lanish</b>\n\n'
            'Ulanish, hujjatlar yoki arizangiz bo‘yicha savolingiz bormi? '
            'Biz bilan bog‘laning — yordam beramiz.\n\n'
            f'☎️ <b>Park telefoni:</b> {escape(PHONE)}\n'
            f'✉️ <b>Telegram operator:</b> @{escape(ADMIN)}\n'
            f'📢 <b>Rasmiy kanal:</b> @{escape(CHANNEL)}')
    rows = []
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{4,31}', ADMIN):
        rows.append([InlineKeyboardButton('✉️ Operatorga yozish', url=f'https://t.me/{ADMIN}')])
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{4,31}', CHANNEL):
        rows.append([InlineKeyboardButton('📢 Rasmiy kanal', url=f'https://t.me/{CHANNEL}')])
    await update.effective_message.reply_text(text, parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(rows) if rows else main_keyboard(), disable_web_page_preview=True)
    return ConversationHandler.END


async def show_office(update, context):
    context.user_data.clear()
    url = MAP_URL
    text = ('📍 <b>TAXICHI BOLA — Farg‘ona ofisi</b>\n\n'
            f'<b>Manzil:</b> {escape(ADDRESS)}\n\n'
            'Taksoparkka ulanish yoki hujjatlar bo‘yicha yordam olish uchun '
            'ofisimizga tashrif buyuring.\n\n'
            f'📞 <b>Telefon:</b> {escape(PHONE)}\n'
            f'✉️ <b>Telegram:</b> @{escape(ADMIN)}\n\n'
            'Yo‘lni topish uchun quyidagi «Xaritada ochish» tugmasini bosing.')
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('🗺 Xaritada ochish', url=url)]]) if re.fullmatch(r'https://(?:yandex\.(?:uz|ru|com)|maps\.app\.goo\.gl|maps\.google\.com)/[^\s]+', url) else main_keyboard()
    if OFFICE_PHOTO.is_file():
        photo_hash = sha256(OFFICE_PHOTO.read_bytes()).hexdigest()
        cached = context.bot_data.get('office_photo_cache', {})
        try:
            if cached.get('hash') == photo_hash and cached.get('file_id'):
                sent = await update.effective_message.reply_photo(photo=cached['file_id'], caption=text,
                    parse_mode='HTML', reply_markup=markup, read_timeout=30, write_timeout=30)
            else:
                with OFFICE_PHOTO.open('rb') as photo:
                    sent = await update.effective_message.reply_photo(photo=photo, caption=text,
                        parse_mode='HTML', reply_markup=markup, read_timeout=30, write_timeout=30)
            if getattr(sent, 'photo', None):
                context.bot_data['office_photo_cache'] = {'hash': photo_hash, 'file_id': sent.photo[-1].file_id}
            return ConversationHandler.END
        except Exception as error:
            context.bot_data.pop('office_photo_cache', None)
            logger.warning('Office photo unavailable (%s); address sent as text.', type(error).__name__)
    await update.effective_message.reply_text(text, parse_mode='HTML', reply_markup=markup)
    return ConversationHandler.END


def build_contact_handler():
    return MessageHandler(filters.ChatType.PRIVATE & filters.Regex(r"^(?:📞 )?Bog[‘’']lanish$"), show_contact)


def build_office_handler():
    return MessageHandler(filters.ChatType.PRIVATE & filters.Regex(r'^(?:📍 )?Ofis manzili$'), show_office)


async def cancel(update, context):
    context.user_data.clear()
    await update.effective_message.reply_text('Ariza bekor qilindi. Kerakli bo‘limni tanlang:', reply_markup=main_keyboard())
    return ConversationHandler.END


async def require_region(update, context, allowed_regions=None):
    return update.effective_chat.type == 'private'
