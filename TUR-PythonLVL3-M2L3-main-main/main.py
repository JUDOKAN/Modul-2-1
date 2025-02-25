import discord
from discord.ext import commands
from logic import quiz_questions
from collections import defaultdict  # Görev 7 - defaultdict komutunu içe aktar
from config import token

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

user_responses = {}
user_scores = defaultdict(int)  # Görev 8 - Kullanıcı puanlarını kaydetmek için puan sözlüğünü oluşturun

async def send_question(ctx_or_interaction, user_id):
    question = quiz_questions[user_responses[user_id]]
    buttons = question.gen_buttons()
    view = discord.ui.View()
    for button in buttons:
        view.add_item(button)

    if isinstance(ctx_or_interaction, commands.Context):
        await ctx_or_interaction.send(question.text, view=view)
    else:
        await ctx_or_interaction.followup.send(question.text, view=view)

@bot.event
async def on_ready():
    print(f'Yeni giriş: {bot.user}!')

@bot.event
async def on_interaction(interaction):
    user_id = interaction.user.id
    if user_id not in user_responses:
        await interaction.response.send_message("Lütfen !start komutunu yazarak testi başlatın")
        return

    custom_id = interaction.data["custom_id"]
    
    if custom_id.startswith("correct"):
        await interaction.response.send_message("Doğru cevap!")
        user_scores[user_id] += 1  # Görev 9 - Doğru cevap için kullanıcıya puan ekle
    elif custom_id.startswith("wrong"):
        await interaction.response.send_message("Yanlış cevap!")
    
    user_responses[user_id] += 1  # Görev 5 - Soru sayacını uygula
    
    if user_responses[user_id] >= len(quiz_questions):  # Görev 6 - Kullanıcı tüm soruları yanıtladıysa sonucu gönder
        await interaction.followup.send(f"Test tamamlandı! Toplam puanınız: {user_scores[user_id]}")
        del user_responses[user_id]  # Kullanıcının testini sıfırla
        del user_scores[user_id]
    else:
        await send_question(interaction, user_id)

@bot.command()
async def start(ctx):
    user_id = ctx.author.id
    if user_id not in user_responses:
        user_responses[user_id] = 0
        user_scores[user_id] = 0  # Kullanıcının başlangıç puanını sıfırla
        await send_question(ctx, user_id)

bot.run(token)