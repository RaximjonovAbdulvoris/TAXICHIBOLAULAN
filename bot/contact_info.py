"""Public TAXICHI BOLA details, shared by menu and applicant notifications."""
import os
from html import escape

PHONE = os.environ.get('CONTACT_PHONE', '').strip() or '+998 90 546 88 66'
ADMIN = os.environ.get('CONTACT_TELEGRAM', '').strip().lstrip('@') or 'Wbtaxichibola'
CHANNEL = os.environ.get('CONTACT_CHANNEL', '').strip().lstrip('@') or 'wb_taxichibola'
ADDRESS = os.environ.get('OFFICE_ADDRESS', '').strip() or 'Farg‘ona shahri, Sohibqiron Temur ko‘chasi, 36-uy'
MAP_URL = os.environ.get('OFFICE_MAP_URL', '').strip() or 'https://yandex.uz/maps/-/CXvPuAK9'
CONTACT_FOOTER = f'📞 Aloqa: {PHONE}\n✉️ Telegram: @{ADMIN}'
CONTACT_FOOTER_HTML = escape(CONTACT_FOOTER)
