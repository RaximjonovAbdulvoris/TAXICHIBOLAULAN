"""All new menu labels must survive premium rendering and reach handlers."""
from datetime import datetime, timezone
import os
import unittest
from unittest.mock import patch
from telegram import Chat, Message, Update
from bot.handlers import start, driver, brand
from bot.premium_emoji import premium_keyboard

class MenuTests(unittest.TestCase):
    def test_all_menu_handlers_accept_premium_and_original_labels(self):
        from bot.presentation import menu_button
        from telegram import ReplyKeyboardMarkup
        labels = [(start.MENU_DRIVER, 'DRIVER'), (start.MENU_BRAND, 'BRAND'),
                  (start.MENU_OFFICE, 'LOCATION'), (start.MENU_CONTACT, 'CONTACT')]
        handlers = [driver.build_driver_conversation().entry_points[0],
                    brand.build_brand_conversation().entry_points[0],
                    start.build_office_handler(), start.build_contact_handler()]
        with patch.dict(os.environ, {f'PREMIUM_ICON_{icon}':'12345' for _,icon in labels}):
            keyboard = ReplyKeyboardMarkup([[menu_button(label,icon=icon)] for label,icon in labels])
            rendered = premium_keyboard(keyboard)['keyboard']
        for (label,_), row, handler in zip(labels, rendered, handlers):
            for text in (label,row[0]['text']):
                msg=Message(1,datetime.now(timezone.utc),Chat(123,'private'),text=text)
                self.assertTrue(handler.check_update(Update(1,message=msg)))
    def test_no_distribution_or_payout(self):
        from bot.regions import driver_groups
        from bot.route_settings import ROUTE_KEYS
        with patch('bot.regions.destination', return_value='-1001') as destination:
            self.assertEqual(driver_groups(),['-1001'])
            destination.assert_called_once_with('DRIVER_GROUP_1')
        self.assertNotIn('DRIVER_GROUP_2',ROUTE_KEYS)
        self.assertNotIn('PUL YECHISH', start.WELCOME_TEXT)
    def test_startup(self):
        from telegram.ext import Application, DictPersistence
        from bot.main import register_handlers
        from bot.premium_emoji import PremiumEmojiBot
        app=Application.builder().bot(PremiumEmojiBot('123:offline')).persistence(DictPersistence()).build()
        register_handlers(app)
        self.assertTrue(app.handlers)


class PremiumAssetsTests(unittest.IsolatedAsyncioTestCase):
    async def test_loaded_premium_icons_reach_menu_operator_and_text(self):
        from types import SimpleNamespace as N
        from unittest.mock import AsyncMock
        from bot import presentation
        from bot.handlers.operator import build_operator_keyboard
        from bot.premium_emoji import premium_html
        sets = {
            'logowbtg': [('🚕', '1001')],
            'FinanceEmoji': [('🎨', '1002')],
            'NewsEmoji': [('📍', '1003'), ('✔️', '1004')],
            'ApplicationEmoji': [('📦', '1005'), ('📄', '1006')],
        }
        async def get_pack(name):
            return N(stickers=[N(emoji=e, custom_emoji_id=i) for e, i in sets.get(name, [])])
        try:
            await presentation.load_emoji_packs(N(bot=N(get_sticker_set=AsyncMock(side_effect=get_pack)),bot_data={}))
            keyboard = start.main_keyboard().keyboard
            self.assertEqual(keyboard[0][0].api_kwargs['icon_custom_emoji_id'], '1001')
            self.assertEqual(keyboard[1][0].api_kwargs['icon_custom_emoji_id'], '1002')
            self.assertEqual(keyboard[2][0].api_kwargs['icon_custom_emoji_id'], '1003')
            self.assertEqual(keyboard[2][1].api_kwargs['icon_custom_emoji_id'], presentation.CONTACT_EMOJI_ID)
            operator = build_operator_keyboard(42).inline_keyboard
            self.assertEqual(operator[-1][0].api_kwargs['icon_custom_emoji_id'], '1005')
            self.assertIn('emoji-id="1006"', premium_html('📄 Hujjatlar'))
        finally:
            presentation._PACK_ICONS.clear()
            presentation._PACK_EMOJIS.clear()
            presentation._PACK_GLYPHS.clear()
