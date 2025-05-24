import logging
import random
from typing import List

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)
from telegram.ext import ContextTypes

from bot.handlers import db_helpers, utils
from bot.handlers.static_data import STICKERS

logger = logging.getLogger(__name__)


async def get_incorrect_answers(
        current_question, all_names: List[str], num_answers: int) -> List[str]:
    """Возвращает случайные неправильные ответы для текущего вопроса."""

    logger.info(
        'Возвращает случайные неправильные ответы для текущего вопроса.'
    )

    return random.sample(all_names, k=min(num_answers, len(all_names)))


async def create_keyboard(options: List[str]) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора ответа."""

    logger.info('Создание клавиатуры для выбора ответа.')

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            option, callback_data=option)] for option in options
    ] + [
        [InlineKeyboardButton('⛔ Завершить викторину ⛔', callback_data='end')]
    ])


async def send_question_message(
    update: Update, current_question,
        remaining_questions: int,
        keyboard: InlineKeyboardMarkup
) -> None:
    """Отправляет сообщение с вопросом и вариантами ответа."""

    logger.info('Отправка сообщения с вопросом и вариантами ответа.')

    message = update.message or (
        update.callback_query.message if update.callback_query else None)

    if isinstance(message, Message):
        await message.reply_text(
            text=(
                f'Осталось вопросов: {remaining_questions}\n\n'
                'Описание функции:\n\n'
                f'{current_question.description}\n\n'
                'Выберите правильный ответ:'
            ),
            reply_markup=keyboard,
        )


async def send_hard_question_message(
    update: Update, current_question,
        remaining_questions: int,
        keyboard: InlineKeyboardMarkup
) -> None:
    """Отправляет сообщение с вопросом для Hard режима."""

    logger.info('Отправка сообщения с вопросом для Hard режима.')

    message = update.message or (
        update.callback_query.message if update.callback_query else None)

    if isinstance(message, Message):
        await message.reply_text(
            text=(
                f'Осталось вопросов: {remaining_questions}\n\n'
                'Описание функции:\n\n'
                f'{current_question.description}\n\n'
                '👇 Введите ваш ответ в чат. 👇\n\n'
                '✔️ Например: pop()'
            ),
            reply_markup=keyboard,
        )


async def ask_next_question(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Выводит следующий вопрос.
    В режиме Easy – отправляет вопрос с вариантами ответа.
    В режиме Hard – отправляет вопрос без вариантов и
    просит ввести ответ текстом.
    """

    logger.info('Вывод следующего вопроса. В режиме Easy и Hard')

    if context.user_data is None:
        logger.warning('context.user_data отсутствует.')
        return

    current_question = context.user_data.get('current_question')
    if not current_question:
        logger.warning('Попытка задать вопрос, но вопрос не найден.')
        if update.message:
            await update.message.reply_text(
                'Вопрос не найден. Викторина завершена.'
            )
        return

    if update.effective_user is None:
        logger.warning('update.effective_user отсутствует.')
        return

    user_id = update.effective_user.id
    user_settings, _ = await db_helpers.get_user_settings(user_id)

    if isinstance(user_settings, dict):
        difficulty = user_settings.get('difficulty', 'easy')
    else:
        difficulty = user_settings.difficulty if user_settings else 'easy'

    if difficulty == 'easy':
        all_names = await utils.get_all_names_except(current_question.id)
        num_incorrect_answers = min(3, len(all_names))
        if num_incorrect_answers < 3:
            logger.warning(
                f'Недостаточно неправильных вариантов для вопроса {
                    current_question.id}.'
            )
        incorrect_answers = await get_incorrect_answers(
            current_question, all_names, num_incorrect_answers
        )
        # Собираем правильный и неправильные варианты, перемешиваем
        options = [current_question.name] + incorrect_answers
        random.shuffle(options)
        keyboard = await create_keyboard(options)
        remaining_questions = len(context.user_data.get('quiz_questions', []))
        await send_question_message(
            update, current_question, remaining_questions, keyboard
        )
    elif difficulty == 'hard':
        logger.info(f'Режим викторины: {difficulty} в обработке.')
        remaining_questions = len(context.user_data.get('quiz_questions', []))

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                '⛔ Завершить викторину ⛔', callback_data='end')]
        ])
        await send_hard_question_message(
            update, current_question,
            remaining_questions, keyboard
        )

    else:
        logger.warning(
            f'Неизвестный режим: {difficulty}. Используем режим Easy.'
        )
        # Если режим неизвестен – используем логику Easy
        all_names = await utils.get_all_names_except(current_question.id)
        num_incorrect_answers = min(3, len(all_names))
        if num_incorrect_answers < 3:
            logger.warning(
                f'Недостаточно неправильных вариантов для вопроса {
                    current_question.id}.'
            )
        incorrect_answers = await get_incorrect_answers(
            current_question, all_names, num_incorrect_answers
        )
        options = [current_question.name] + incorrect_answers
        random.shuffle(options)
        keyboard = await create_keyboard(options)
        remaining_questions = len(context.user_data.get('quiz_questions', []))
        await send_question_message(
            update, current_question, remaining_questions, keyboard
        )


async def finish_quiz(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает завершение викторины:
    вывод результата и отправка стикера.
    """

    logger.info('Завершение викторины.')

    if context.user_data is None:
        logger.warning('context.user_data отсутствует.')
        return

    correct_answers = context.user_data.get('correct_answers', 0)

    message = update.message or (
        update.callback_query.message if update.callback_query else None)
    if isinstance(message, Message):
        await message.reply_text(
            '🎉 Викторина завершена!\n\n'
            f'🎯 Правильных ответов: {correct_answers} из 10.'
        )
        await send_sticker(message, correct_answers)
        await message.reply_text(
            'Чтобы начать сначала, нажмите на кнопку ✨ "Викторина" ✨'
        )

    context.user_data.clear()


async def send_sticker(message: Message, correct_answers: int) -> None:
    """Выбирает и отправляет стикер в зависимости от результата викторины."""

    logger.info('Отправка стикера в зависимости от результата викторины.')

    if correct_answers == 10:
        sticker = random.choice(STICKERS['perfect'])
    elif 7 <= correct_answers <= 9:
        sticker = random.choice(STICKERS['great'])
    else:
        sticker = random.choice(STICKERS['good'])

    await message.reply_sticker(sticker)
