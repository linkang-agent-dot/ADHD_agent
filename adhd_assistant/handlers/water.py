"""Water reminder response handler."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import ai_engine as ai


async def handle_water_response(query, context, response: str):
    if response == "done":
        praise = await ai.water_praise()
        await query.edit_message_text(praise)
    elif response == "soda":
        scold = await ai.water_scold()
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ 好，去喝水了", callback_data="water:done"),
        ]])
        await query.edit_message_text(scold, reply_markup=buttons)
