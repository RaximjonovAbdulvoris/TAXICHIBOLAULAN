"""Internal routing adapter for one LIDER park. No region choice or fallback."""
from bot.route_settings import destination

PARK = 'taxichibola'


def get_region(context):
    return PARK


def region_name(region):
    return 'TAXICHI BOLA'


def clear_application(context):
    context.user_data.clear()


def driver_groups(region=PARK):
    if region != PARK:
        return []
    return [value] if (value := destination('DRIVER_GROUP_1')) else []


def application_group(region, kind):
    return destination('BRAND_GROUP') if region == PARK and kind == 'brand' else ''


def archive_group(region=PARK):
    return destination('ARCHIVE_GROUP') if region == PARK else ''
