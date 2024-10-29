from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from services.currency_converter import convert_currency, convert_currency_from_openapi
from database import get_previous_requests, save_conversion

class CurrencyConversionStates(StatesGroup):
    main_menu = State()
    waiting_for_currency_from = State()
    waiting_for_currency_to = State()
    waiting_for_amount = State()
    waiting_for_history_period = State()  

router = Router()

@router.message(Command("start"))
async def command_start_handler(message: types.Message, state: FSMContext):
    convert_button = KeyboardButton(text="Конвертировать валюту")
    history_button = KeyboardButton(text="История конвертаций")
    markup = ReplyKeyboardMarkup(keyboard=[[convert_button], [history_button]], resize_keyboard=True)
    
    await message.answer(
        "Привет! Я помогу тебе с валютными операциями. Чтобы начать, нажми кнопку ниже:",
        reply_markup=markup
    )
    await state.set_state(CurrencyConversionStates.main_menu)

@router.message(lambda message: message.text == "Конвертировать валюту")
async def button_convert_handler(message: types.Message, state: FSMContext):
    await command_convert_handler(message, state)

@router.message(Command("convert"))
async def command_convert_handler(message: types.Message, state: FSMContext):
    markup = await get_currency_buttons()
    
    await message.answer(
        "Пожалуйста, выберите валюту, которую вы хотите конвертировать:",
        reply_markup=markup
    )
    await state.set_state(CurrencyConversionStates.waiting_for_currency_from)

async def get_currency_buttons() -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(text=currency) for currency in 
               ["USD", "EUR", "RUB", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD", "SEK", "SGD", "NOK", "MXN"]]
    
    markup = ReplyKeyboardMarkup(
        keyboard=[[btn] for btn in buttons] + [[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    return markup

@router.message(lambda message: message.text == "Назад")
async def back_handler(message: types.Message, state: FSMContext):
    await command_start_handler(message, state)  # Вернуться в главное меню

@router.message(CurrencyConversionStates.waiting_for_currency_from)
async def currency_from_choice_handler(message: types.Message, state: FSMContext):
    selected_currency_from = message.text.strip().upper()
    valid_currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD", "SEK", "SGD", "NOK", "MXN"]

    if selected_currency_from not in valid_currencies:
        await message.answer("Пожалуйста, выберите корректную валюту для конвертации.")
        return

    await state.update_data(currency_from=selected_currency_from)
    
    await message.answer(
        f"Вы выбрали {selected_currency_from}. Пожалуйста, введите валюту, в которую вы хотите конвертировать:"
    )
    
    await state.set_state(CurrencyConversionStates.waiting_for_currency_to)

@router.message(CurrencyConversionStates.waiting_for_currency_to)
async def currency_to_choice_handler(message: types.Message, state: FSMContext):
    selected_currency_to = message.text.strip().upper()
    
    data = await state.get_data()
    valid_currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD", "SEK", "SGD", "NOK", "MXN"]

    if selected_currency_to not in valid_currencies:
        await message.answer("Пожалуйста, выберите корректную валюту для конвертации.")
        return

    await state.update_data(currency_to=selected_currency_to)
    
    await message.answer(f"Вы выбрали {selected_currency_to}. Введите сумму для конвертации:")
    await state.set_state(CurrencyConversionStates.waiting_for_amount)

@router.message(CurrencyConversionStates.waiting_for_amount)
async def amount_input_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if 'currency_from' in data and 'currency_to' in data:
        input_text = message.text.strip().replace(',', '.')

        if input_text.replace('.', '', 1).isdigit():
            amount = float(input_text)

            try:
                result_yahoo_finance = convert_currency(amount, data['currency_from'], data['currency_to'])
                result_free_api = convert_currency_from_openapi(amount, data['currency_from'], data['currency_to'])
                
                user_id = message.from_user.id  
                save_conversion(user_id, data['currency_from'], data['currency_to'], amount, result_yahoo_finance, result_free_api)

                await message.answer(
                    f"Yahoo Finance: {amount} {data['currency_from']} = {result_yahoo_finance} {data['currency_to']}\n"
                    f"Free API: {amount} {data['currency_from']} = {result_free_api} {data['currency_to']}"
                )
                await state.clear() 
                await command_start_handler(message, state)  
            except Exception as e:
                await message.answer(f"Произошла ошибка при запросе конвертации: {e}")
        else:
            await message.answer(f"Ошибка: '{input_text}' не является числом.")
            await message.answer("Пожалуйста, введите корректное число для конвертации.")
    else:
        await message.answer("Сначала выберите валюты для конвертации.")

@router.message(lambda message: message.text == "История конвертаций")
async def history_button_handler(message: types.Message, state: FSMContext):
    period_buttons = [
        KeyboardButton(text="1 день"),
        KeyboardButton(text="1 неделя"),
        KeyboardButton(text="1 месяц"),
        KeyboardButton(text="Назад")
    ]
    markup = ReplyKeyboardMarkup(keyboard=[[btn] for btn in period_buttons], resize_keyboard=True)

    await message.answer("Выберите период для просмотра истории конвертаций:", reply_markup=markup)
    await state.set_state(CurrencyConversionStates.waiting_for_history_period)

@router.message(CurrencyConversionStates.waiting_for_history_period)
async def history_period_choice_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    period = message.text.strip()

    if period == "Назад":
        await command_start_handler(message, state)  

    days_mapping = {
        "1 день": "-1 day",
        "1 неделя": "-7 days",
        "1 месяц": "-30 days"
    }

    if period in days_mapping:
        days = days_mapping[period]
        conversions = get_previous_requests(user_id, days)
        
        if conversions:
            history_message = "\n".join(
                [f"{row['created_at']}: {row['amount']} {row['currency_from']} = {row['result_yahoo']} {row['currency_to']} (Yahoo Finance)\n"
                 f"{row['amount']} {row['currency_from']} = {row['result_openapi']} {row['currency_to']} (Free API)" for row in conversions]
            )
            await message.answer(f"История конвертаций за {period}:\n{history_message}")
        else:
            await message.answer(f"У вас нет конвертаций за {period}.")
        
        await state.clear() 
        await command_start_handler(message, state)  
    else:
        await message.answer("Пожалуйста, выберите корректный период.")
