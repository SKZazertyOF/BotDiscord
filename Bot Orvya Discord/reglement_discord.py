import discord
from discord.ui import View

# Configuration
ID_SALON_REGLE_DISCORD = 1385974170705199165

async def envoyer_regles_discord(bot):
    print("Envoi des règles Discord...")
    salon = bot.get_channel(ID_SALON_REGLE_DISCORD)
    if not salon:
        return print("Erreur: Salon des règles Discord introuvable")

    # Nettoyage des anciens messages
    async for message in salon.history(limit=10):
        if message.author == bot.user:
            await message.delete()

    # Création de l'embed
    embed = discord.Embed(
        title="📜 Règles Officielles du Discord",
        description="**Lisez attentivement avant de participer !**\n"
                  "Ces règles complètent celles du serveur Minecraft.",
        color=discord.Color.blue()
    )
    
    # Liste des règles
    regles = [
        ("1️⃣ **Communication**",
         "• Respectez tous les membres\n"
         "• Pas d'insultes ou contenus choquants\n"
         "• Évitez les sujets sensibles (politique, religion)"),
        
        ("2️⃣ **Salons vocaux**",
         "• Pas de son parasite\n"
         "• Musique uniquement dans #musique\n"
         "• Respectez les discussions en cours"),
        
        ("3️⃣ **Spam & Mentions**",
         "• Pas de flood de messages\n"
         "• Pas de mentions abusives\n"
         "• Utilisez les bons salons"),
        
        ("4️⃣ **Contenu interdit**",
         "• Pas de NSFW/18+\n"
         "• Pas de liens suspects\n"
         "• Pas de publicité non autorisée"),
        
        ("5️⃣ **Modération**",
         "• Les staffs ont toujours raison\n"
         "• Les sanctions sont à leur discrétion\n"
         "• En cas de problème, MP un modérateur")
    ]
    
    for titre, description in regles:
        embed.add_field(name=titre, value=description, inline=False)
    
    embed.set_footer(text="Merci de faire de ce Discord un espace agréable !")
    
    await salon.send(embed=embed)