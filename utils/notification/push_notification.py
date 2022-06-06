from django.conf import settings

from notifications.actions import push_notification
from categories.models import Category


def send_push_notification(
    template,
    has_custom_user_target=True,
    persons=None,
    is_personalised=False,
    person=None,
    web_onclick_url='',
    send_only_to_subscribed_users=False,
):
    """
    :param template: template message
    :return:
    """

    service = settings.DISCOVERY.get_app_configuration(
        'bhawan_app'
    )
    category, _ = Category.objects.get_or_create(
        name=service.nomenclature.verbose_name,
        slug=service.nomenclature.name,
    )
    push_notification(
        template=template,
        category=category,
        web_onclick_url=web_onclick_url,
        android_onclick_activity='',
        ios_onclick_action='',
        is_personalised=is_personalised,
        person=person,
        has_custom_users_target=has_custom_user_target,
        persons=persons,
        send_only_to_subscribed_users=send_only_to_subscribed_users,
    )