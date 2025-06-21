import discord
from discord.ext import commands
from discord import app_commands
from var import TOKEN
from reglement_server import envoyer_regles_serveur, BoutonAcceptationServeur
from reglement_discord import envoyer_regles_discord

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

class EtatServeur:
    OUVERT = "ouvert"
    MAINTENANCE = "maintenance"
    FERME = "ferme"

# Configuration
SERVEUR_ETAT = EtatServeur.FERME  # État initial
MAINTENANCE_RAISON = "Maintenance programmée"
OUVERTURE_PREVUE = "Prochainement"
MODPACK_CODE = "TSbrNblG (si ce code n'est plus disponible veuillez le dire au staff)"
SALON_ANNONCES_ID = 1385975846275256420  # Salon pour les annonces

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté")
    
    # Initialisation des vues persistantes
    bot.add_view(BoutonAcceptationServeur())
    
    try:
        synced = await bot.tree.sync()
        print(f"Commandes synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur synchronisation : {e}")

@bot.tree.command(name="ip", description="Affiche l'état et l'IP du serveur")
async def ip(interaction: discord.Interaction):
    embed = discord.Embed(title="🌍 État du Serveur Minecraft")
    
    etat_config = {
        EtatServeur.OUVERT: {
            "color": discord.Color.green(),
            "emoji": "🟢",
            "title": "Serveur ouvert !",
            "fields": [
                ("IP", "`orvya.fr`", True),
                ("Version", "1.20.1", True),
                ("Statut", "En ligne - Connectez-vous !", False)
            ]
        },
        EtatServeur.MAINTENANCE: {
            "color": discord.Color.orange(),
            "emoji": "🟠", 
            "title": "Maintenance en cours",
            "fields": [
                ("Raison", MAINTENANCE_RAISON, False),
                ("IP", "`orvya.fr`", True),
                ("Statut", "Indisponible - Merci de patienter", False)
            ]
        },
        EtatServeur.FERME: {
            "color": discord.Color.red(),
            "emoji": "🔴",
            "title": "Serveur fermé",
            "fields": [
                ("Prochaine ouverture", OUVERTURE_PREVUE, False),
                ("Information", "Revenez plus tard pour jouer !", False)
            ]
        }
    }
    
    config = etat_config[SERVEUR_ETAT]
    embed.color = config["color"]
    embed.description = f"{config['emoji']} **{config['title']}**"
    
    for name, value, inline in config["fields"]:
        embed.add_field(name=name, value=value, inline=inline)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mod", description="Installer le modpack")
async def mod(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔧 Modpack du serveur",
        description=f"Code du modpack : `{MODPACK_CODE}`",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Comment installer", 
        value="1. Ouvrez CurseForge\n"
             "2. Insérez ce code dans IMPORT\n"
             "3. Installez et lancez",
        inline=False
    )
    embed.add_field(
        name="Mods inclus", 
        value="• OptiFine\n• JEI\n• Simple Voice Chat\n• WorldEdit\n• Légendary Tooltips\n• Curios API\n• Biomes O' Plenty\n• Et quelques API",
        inline=False
    )
    embed.set_footer(text="Le modpack est obligatoire pour jouer")
    await interaction.response.send_message(embed=embed)

async def etat_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    etats = [EtatServeur.OUVERT, EtatServeur.MAINTENANCE, EtatServeur.FERME]
    return [
        app_commands.Choice(name=etat.capitalize(), value=etat)
        for etat in etats
        if current.lower() in etat.lower()
    ]

@bot.tree.command(name="maintenance", description="Gère l'état du serveur (Staff)")
@app_commands.autocomplete(etat=etat_autocomplete)
@app_commands.describe(
    etat="Nouvel état du serveur",
    raison="Raison du changement (optionnel)",
    heure="Heure de réouverture (optionnel)"
)
@commands.has_permissions(administrator=True)
async def maintenance(
    interaction: discord.Interaction,
    etat: str,
    raison: str = None,
    heure: str = None
):
    global SERVEUR_ETAT, MAINTENANCE_RAISON, OUVERTURE_PREVUE
    
    ancien_etat = SERVEUR_ETAT
    SERVEUR_ETAT = etat
    
    if raison:
        MAINTENANCE_RAISON = raison
    if heure:
        OUVERTURE_PREVUE = heure

    # Préparation de l'embed d'annonce
    embed = discord.Embed()
    embed.color = {
        EtatServeur.OUVERT: discord.Color.green(),
        EtatServeur.MAINTENANCE: discord.Color.orange(),
        EtatServeur.FERME: discord.Color.red()
    }[etat]
    
    embed.title = {
        EtatServeur.OUVERT: "🟢 Serveur ouvert !",
        EtatServeur.MAINTENANCE: "🟠 Maintenance en cours",
        EtatServeur.FERME: "🔴 Serveur fermé"
    }[etat]
    
    if etat == EtatServeur.MAINTENANCE:
        embed.add_field(name="Raison", value=MAINTENANCE_RAISON, inline=False)
        if heure:
            embed.add_field(name="Réouverture prévue", value=heure, inline=False)
    elif etat == EtatServeur.FERME and heure:
        embed.add_field(name="Réouverture prévue", value=heure, inline=False)
    
    embed.set_footer(text=f"Modifié par {interaction.user.display_name}")
    
    # Envoi dans le salon d'annonces
    salon = bot.get_channel(SALON_ANNONCES_ID)
    if salon:
        mention = "@everyone" if ancien_etat != etat else ""
        await salon.send(mention, embed=embed)
    
    await interaction.response.send_message(
        f"État du serveur mis à jour : **{etat.capitalize()}**",
        ephemeral=True
    )

@bot.tree.command(name="annonce", description="Poste une annonce stylisée (Staff)")
@app_commands.describe(
    titre="Titre de l'annonce",
    message="Contenu de l'annonce",
    importance="Niveau d'importance (faible/normal/urgent)"
)
@commands.has_permissions(administrator=True)
async def annonce(
    interaction: discord.Interaction,
    titre: str,
    message: str,
    importance: str = "normal"
):
    importance_config = {
        "faible": {"color": discord.Color.blue(), "emoji": "ℹ️"},
        "normal": {"color": discord.Color.gold(), "emoji": "📢"},
        "urgent": {"color": discord.Color.red(), "emoji": "🚨"}
    }
    
    config = importance_config.get(importance.lower(), importance_config["normal"])
    
    embed = discord.Embed(
        title=f"{config['emoji']} {titre}",
        description=message,
        color=config["color"]
    )
    
    if interaction.guild.icon:
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
    else:
        embed.set_author(name=interaction.guild.name)
    
    embed.set_footer(text=f"Annonce postée par {interaction.user.display_name}")
    
    # Menu déroulant pour choisir le type de mention
    class MentionView(discord.ui.View):
        @discord.ui.select(
            placeholder="Qui mentionner ?",
            options=[
                discord.SelectOption(label="Tout le monde", emoji="👥", value="everyone"),
                discord.SelectOption(label="Seulement les membres", emoji="👤", value="members"),
                discord.SelectOption(label="Personne", emoji="🔇", value="none")
            ]
        )
        async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
            mention = {
                "everyone": "@everyone",
                "members": "@here", 
                "none": ""
            }[select.values[0]]
            
            salon = bot.get_channel(SALON_ANNONCES_ID)
            if salon:
                try:
                    await salon.send(mention, embed=embed)
                    await interaction.response.send_message("✅ Annonce envoyée !", ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message("❌ Je n'ai pas la permission d'envoyer des messages dans ce salon", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Salon d'annonces introuvable", ephemeral=True)
    
    await interaction.response.send_message(
        "Choisissez qui mentionner :",
        view=MentionView(),
        ephemeral=True
    )

bot.run(TOKEN)