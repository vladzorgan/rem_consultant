def pluralize_reviews(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "отзыв"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return "отзыва"
    else:
        return "отзывов"

def format_service_center_message(center):
    """Форматирует сообщение с информацией о сервисном центре"""

    message = (
        f"🏢 <b>{center['name']}</b>\n\n"
        f"⭐️ <b>Рейтинг:</b> {center['avg_rating']} ({center['reviews_count']} {pluralize_reviews(center['reviews_count'])})\n\n"
        f"📍 <b>Адрес:</b> {center['address']}\n\n"
        f"📞 <b>Телефон:</b> {center['phone']}\n\n"
    )

    # Добавляем линии-разделители для улучшения восприятия
    message += "\n" + "─" * 10 + "\n"

    # Проверяем, есть ли ссылки, и добавляем их
    links = center.get('links', [])

    if links:
        message += "<b>Ссылки:</b>\n\n"
        for link in links:
            if link['type'] == 'vk':
                message += f"🔗 <b>ВКонтакте:</b> <a href='{link['link']}'>Перейти</a>\n\n"
            elif link['type'] == 'instagram':
                message += f"📸 <b>Instagram:</b> <a href='{link['link']}'>Перейти</a>\n\n"
            elif link['type'] == 'telegram':
                message += f"📱 <b>Telegram:</b> <a href='{link['link']}'>Перейти</a>\n\n"
            elif link['type'] == 'website':
                message += f"🌐 <b>Сайт:</b> <a href='{link['link']}'>Перейти</a>\n\n"
    else:
        message += "<i>Нет доступных ссылок</i>\n"

    # Добавляем линии-разделители для улучшения восприятия
    message += "\n" + "─" * 10 + "\n"

    # Заключительная часть с призывом к действию
    message += "<b>Не нашли нужную информацию?</b> Напишите нам, и мы поможем!"

    return message


def format_manage_service_center_message(center):
    """Форматирует сообщение с информацией о сервисном центре"""

    message = (
        f"🏢 <b>{center['name']}</b>\n\n"
        f"⭐️ <b>Рейтинг:</b> {center['avg_rating']} ({center['reviews_count']} {pluralize_reviews(center['reviews_count'])})\n\n"
        f"📍 <b>Адрес:</b> {center['address']}\n\n"
        f"📞 <b>Телефон:</b> {center['phone']}\n\n"
    )

    # Добавляем линии-разделители для улучшения восприятия
    message += "\n" + "─" * 10 + "\n"

    # Проверяем, есть ли ссылки, и добавляем их
    links = center.get('links', [])

    if links:
        message += "<b>Ссылки:</b>\n\n"
        for link in links:
            if link['type'] == 'vk':
                message += f"🔗 <b>ВКонтакте:</b> <a href='{link['link']}'>Перейти</a>\n\n"
            elif link['type'] == 'instagram':
                message += f"📸 <b>Instagram:</b> <a href='{link['link']}'>Перейти</a>\n\n"
            elif link['type'] == 'telegram':
                message += f"📱 <b>Telegram:</b> <a href='{link['link']}'>Перейти</a>\n\n"
            elif link['type'] == 'website':
                message += f"🌐 <b>Сайт:</b> <a href='{link['link']}'>Перейти</a>\n\n"
    else:
        message += "<i>Нет доступных ссылок</i>\n"

    # Добавляем линии-разделители для улучшения восприятия
    message += "\n" + "─" * 10 + "\n"

    # Заключительная часть с призывом к действию
    message += "<b>Не нашли нужную информацию?</b> Напишите нам, и мы поможем!"

    return message

