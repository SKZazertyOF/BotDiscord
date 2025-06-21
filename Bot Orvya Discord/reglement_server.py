import discord
from discord.ui import Button, View

# Configuration
ID_SALON_REGLE_SERVEUR = 1385973950114168994
ID_ROLE_ACCEPTE_SERVEUR = 1385975960494407862

class BoutonAcceptationServeur(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="✅ J'accepte les règles du serveur", 
                      style=discord.ButtonStyle.green,
                      custom_id="accept_rules_server")
    async def callback(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(ID_ROLE_ACCEPTE_SERVEUR)
        if role:
            if role not in interaction.user.roles:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "✅ Vous avez accès au serveur Minecraft ! Bon jeu !",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "⚠️ Vous avez déjà accepté les règles du serveur !",
                    ephemeral=True
                )

async def envoyer_regles_serveur(bot):
    print("Envoi des règles du serveur Minecraft...")
    salon = bot.get_channel(ID_SALON_REGLE_SERVEUR)
    if not salon:
        return print("Erreur: Salon des règles serveur introuvable")

    # Nettoyage des anciens messages
    async for message in salon.history(limit=10):
        if message.author == bot.user:
            await message.delete()

    # Création de l'embed
    embed = discord.Embed(
        title="📜 Règles Officielles du Serveur Minecraft",
        description="**Lisez attentivement avant de jouer !**\n"
                  "Le non-respect entraîne des sanctions.",
        color=discord.Color.green()
    )
    
    # Liste des règles
    regles = [
        ("1️⃣ **Respect mutuel**", 
         "Vous pouvez vous taquiner mais restez dans les limites du raisonnable. "
         "Pas de harcèlement ou discriminations."),
        
        ("2️⃣ **Triche (Cheat)**",
         "Si vous êtes pris à tricher (hack client, macro, etc.) :\n"
         "- **1ère fois** : Retrait d'argent\n"
         "- **2ème fois** : Débuffs permanents\n"
         "- **3ème fois** : Bannissement\n"
         "*« Si vous continuez après ça, vous êtes juste chiant »*"),
        
        ("3️⃣ **X-Ray - Règles spéciales**",
         "✅ **Autorisé UNIQUEMENT** :\n"
         "- Pendant les **2 premiers jours**\n"
         "- Pour localiser des dungeons\n\n"
         "❌ **Interdit après** :\n"
         "- Pour miner des diamants/anciennes débris"),
        
        ("4️⃣ **Grief & Vol**",
         "Tout vol ou destruction sera sanctionné par :\n"
         "- Remboursement des dégâts\n"
         "- Bannissement temporaire"),
        
        ("5️⃣ **Constructions**",
         "Pas de builds NSFW/racistes. Les builds trolls doivent :\n"
         "- Être identifiés comme tels\n"
         "- Être loin des zones principales")
    ]
    
    for titre, description in regles:
        embed.add_field(name=titre, value=description, inline=False)
    
    embed.set_footer(text="Les modérateurs ont le dernier mot | Bon jeu !")
    
    await salon.send(embed=embed, view=BoutonAcceptationServeur())