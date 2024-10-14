



# async def test_cmd_start(dp, bot):                           # [1]
#     bot.add_result_for(                                      # [2]
#         method=SendMessage,
#         ok=True,
#         # result сейчас можно пропустить
#     )
#     chat = Chat(id=1234567, type=ChatType.PRIVATE)           # [3]
#     user = User(id=1234567, is_bot=False, first_name="User") # [3]
#     message = Message(                                       # [3]
#         message_id=1,
#         chat=chat, 
#         from_user=user, 
#         text="/start", 
#         date=datetime.now()
#     )
#     result = await dp.feed_update(                      # [4]
#         bot, 
#         Update(message=message, update_id=1)
#     )
#     assert result is not UNHANDLED                      # [5]
#     outgoing_message: TelegramType = bot.get_request()  # [6]
#     assert isinstance(outgoing_message, SendMessage)    # [7]
#     assert outgoing_message.text == "Привет!"           # [8]