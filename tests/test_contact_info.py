"""Public office/contact details and a failed photo must remain usable."""
import tempfile
from pathlib import Path
from types import SimpleNamespace as N
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from telegram.error import BadRequest
from bot.handlers import start, operator

class ContactTests(IsolatedAsyncioTestCase):
    async def test_contact_has_correct_phone_admin_channel_and_buttons(self):
        message = N(reply_text=AsyncMock())
        await start.show_contact(N(effective_message=message), N(user_data={}, bot_data={}))
        sent=message.reply_text.await_args.kwargs
        text=message.reply_text.await_args.args[0]
        self.assertIn('+998 90 546 88 66', text)
        self.assertIn('@Wbtaxichibola', text)
        self.assertIn('@wb_taxichibola', text)
        urls=[b.url for row in sent['reply_markup'].inline_keyboard for b in row]
        self.assertEqual(urls,['https://t.me/Wbtaxichibola','https://t.me/wb_taxichibola'])
    async def test_photo_failure_still_delivers_office_and_map(self):
        message=N(reply_photo=AsyncMock(side_effect=BadRequest('Image_process_failed')), reply_text=AsyncMock())
        ctx=N(user_data={},bot_data={})
        with tempfile.TemporaryDirectory() as directory:
            photo=Path(directory)/'office.jpg'; photo.write_bytes(b'synthetic')
            with patch.object(start,'OFFICE_PHOTO',photo):
                await start.show_office(N(effective_message=message),ctx)
        message.reply_text.assert_awaited_once()
        sent=message.reply_text.await_args
        self.assertIn('36-uy',sent.args[0])
        self.assertEqual(sent.kwargs['reply_markup'].inline_keyboard[0][0].url,'https://yandex.uz/maps/-/CXvPuAK9')
    async def test_photo_file_id_is_cached_after_success(self):
        message=N(reply_photo=AsyncMock(return_value=N(photo=[N(file_id='cached-office')])),reply_text=AsyncMock())
        ctx=N(user_data={},bot_data={})
        with tempfile.TemporaryDirectory() as directory:
            photo=Path(directory)/'office.jpg';photo.write_bytes(b'synthetic')
            with patch.object(start,'OFFICE_PHOTO',photo):
                await start.show_office(N(effective_message=message),ctx)
                await start.show_office(N(effective_message=message),ctx)
        self.assertEqual(message.reply_photo.await_args.kwargs['photo'],'cached-office')
        message.reply_text.assert_not_awaited()
    def test_all_operator_notices_use_this_park_contacts(self):
        for text in (operator.READY_TEXT,operator.INCOMPLETE_TEXT,operator.OTHER_PARK_TEXT):
            self.assertIn('+998 90 546 88 66',text)
            self.assertIn('@Wbtaxichibola',text)
            self.assertNotIn('LIDER',text)
