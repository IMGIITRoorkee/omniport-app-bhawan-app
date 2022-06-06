from django.conf import settings
from emails.actions import email_push

from categories.models import Category

def send_email(
    subject_text,
    body_text,
    persons=None,
    has_custom_user_target=True,
    by=None,
    check_if_primary_email_verified=True,
    send_only_to_subscribed_users=False,
):
    """
    Utility to send an email
    :param subject_text: the subject of the e-mail
    :param body_text: the body of the e-mail
    :param persons: the list of ids of persons
    :param has_custom_user_target: whether to e-mail specified persons or not
    :param by: id of the person who is posting the mail
    """

    service = settings.DISCOVERY.get_app_configuration(
        'bhawan_app'
    )
    category, _ = Category.objects.get_or_create(
        name=service.nomenclature.verbose_name,
        slug=service.nomenclature.name,
    )
    app_verbose_name = service.nomenclature.verbose_name
    app_slug = service.nomenclature.name

    full_path = f'https://internet.channeli.in/{app_slug}'
    
    relative_url_resolver = (
        '<base href="https://internet.channeli.in/" target="_blank">'
    )
    body_text = f'{relative_url_resolver}{body_text}'
    email_push(
        subject_text=subject_text,
        body_text=body_text,
        category=category,
        has_custom_user_target=has_custom_user_target,
        persons=persons,
        by=by,
        target_app_name=app_verbose_name,
        target_app_url=full_path,
        send_only_to_subscribed_users=send_only_to_subscribed_users,
    )