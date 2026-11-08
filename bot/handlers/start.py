"""Single-city TAXICHI BOLA menu and configurable public information."""
import os
import re
from html import escape
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from bot.presentation import menu_button

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
    "🚖 <b>TAXICHI BOLA</b>\nHaydovchilar uchun ariza markazi\n\n"
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
    lines = ['📞 <b>TAXICHI BOLA — Bog‘lanish</b>']
    phone = os.environ.get('CONTACT_PHONE', '').strip()
    username = os.environ.get('CONTACT_TELEGRAM', '').strip().lstrip('@')
    if phone:
        lines.append('Telefon: ' + escape(phone))
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{4,31}', username):
        lines.append('Telegram: @' + escape(username))
    if len(lines) == 1:
        lines.append('Aloqa ma’lumotlari tez orada qo‘shiladi.')
    await update.effective_message.reply_text('\n\n'.join(lines), parse_mode='HTML', reply_markup=main_keyboard())
    return ConversationHandler.END


async def show_office(update, context):
    context.user_data.clear()
    address = os.environ.get('OFFICE_ADDRESS', '').strip()
    url = os.environ.get('OFFICE_MAP_URL', '').strip()
    text = '📍 <b>TAXICHI BOLA — Ofis manzili</b>\n\n' + escape(address or 'Ofis manzili tez orada qo‘shiladi.')
    markup = InlineKeyboardMarkup([[InlineKeyboardButton('🗺 Xaritada ochish', url=url)]]) if re.fullmatch(r'https://(?:yandex\.(?:uz|ru|com)|maps\.app\.goo\.gl|maps\.google\.com)/[^\s]+', url) else main_keyboard()
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
