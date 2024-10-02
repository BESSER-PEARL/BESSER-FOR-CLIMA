from besser.bot.core.bot import Bot
from besser.bot.nlp import HF_API_KEY
from besser.bot.nlp.llm.llm_huggingface_api import LLMHuggingFaceAPI

bot = Bot('bot')
bot.load_properties('config.ini')
print(bot.get_property(HF_API_KEY))
llama = LLMHuggingFaceAPI(bot, 'google/gemma-2b-it', {})
answer = llama.predict('How can I cook a chicken?')
print(answer)