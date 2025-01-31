from telegram import Update


async def send_no_questions_message(update: Update) -> None:
    """Отправляет сообщение о том, что вопросов нет."""

    await update.message.reply_text(
        'К сожалению, в этой теме вопросов нет. 😔\n'
        'Выберите пожалуйста другую тему'
    )


async def send_error_message(update: Update) -> None:
    """Отправляет сообщение об ошибке."""

    await update.message.reply_text('Что-то пошло не так. Вопросы отсутствуют.')
