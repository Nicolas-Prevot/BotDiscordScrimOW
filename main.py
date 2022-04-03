import os
from io import BytesIO

import discord
from discord.ext import commands
from discord.ui import InputText, Modal

from discord_scrim import *


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!")
        self.main_message = None
        self.guild_ids = []
        self.dict_emojis = {}  # {0:emoji, ...}
        self.elo_options = []
        self.register_message = ""
        self.priority_emojis = {3: "🟠", 2: "🟡", 1: "🟢"}
        self.role_emojis = {"tank": "🛡", "dps": "⚔", "heal": "❤"}
        self.discrim = Discord_scrim()
        self.__get_guilds_id()

    def __get_guilds_id(self, name_file_guilds_id="guilds_id"):
        with open(name_file_guilds_id, "r") as file:
            for line in file:
                if line.startswith("#"):
                    continue
                self.guild_ids.append(int(line))

    def fill_dict_emojis(self):
        temp_dict = {'bronze': 6,
                     'silver': 5,
                     'gold': 4,
                     'platine': 3,
                     'diamant': 2,
                     'master': 1,
                     'grand_master': 0}
        for emoji in self.emojis:
            if emoji.name in list(temp_dict.keys()):
                self.dict_emojis[temp_dict[emoji.name]] = emoji
        self.__set_elo_options()

    def __set_elo_options(self):
        self.elo_options = [
            discord.SelectOption(label="0-1499", value=6,
                                 emoji=self.dict_emojis[6]),
            discord.SelectOption(label="1500-1999", value=5,
                                 emoji=self.dict_emojis[5]),
            discord.SelectOption(label="2000-2499", value=4,
                                 emoji=self.dict_emojis[4]),
            discord.SelectOption(label="2500-2999", value=3,
                                 emoji=self.dict_emojis[3]),
            discord.SelectOption(label="3000-3499", value=2,
                                 emoji=self.dict_emojis[2]),
            discord.SelectOption(label="3500-3999", value=1,
                                 emoji=self.dict_emojis[1]),
            discord.SelectOption(label="4000+", value=0,
                                 emoji=self.dict_emojis[0])]

    async def send_main_msg(self, ctx, content=None):
        if bot.discrim.can_register():
            embed = get_main_embed()
            view = View_register_button()
            content = self.register_message
            try:
                await self.main_message.edit(embed=None)
                await self.main_message.edit(content=content,
                                             embed=embed,
                                             view=view)
            except:
                self.main_message = await ctx.channel.send(content=content,
                                                           embed=embed,
                                                           view=view)
        elif bot.discrim.is_registration_over():
            embeds = get_teams_embeds()
            view = View_register_after_team()
            if content is None:
                content = "Panneau des équipes ! "
            else:
                content = "Panneau des équipes ! " + content
            try:
                await self.main_message.edit(embed=None)
                await self.main_message.edit(content=content,
                                             embeds=embeds,
                                             view=view)
            except:
                self.main_message = await ctx.channel.send(content=content,
                                                           embeds=embeds,
                                                           view=view)




bot = Bot()


async def load_emojis():
    list_name = []
    for emoji in bot.emojis:
        list_name.append(emoji.name)
    print("emoji already loaded in this guild :", list_name)
    for name in os.listdir("assets"):
        if name[:-4] in list_name:
            continue
        with open("assets/"+name, "rb") as image:
            imgb = BytesIO(image.read()).getvalue()
            emoji = await bot.get_guild(bot.guild_ids[0]).create_custom_emoji(
                                                            name=name[:-4],
                                                            image=imgb)
            print("new emoji created in this guild :", emoji)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await load_emojis()
    bot.fill_dict_emojis()
    print("Emojis loaded")
    print("--------------------------")


CHANNEL_BOT = "annonce-scrim"


############################### COMMANDS #####################################



##############################################################################
######### Function to open buttons to change things ##########################
##############################################################################

@bot.slash_command(name="scrim_fonctions", guild_ids=bot.guild_ids)
async def get_panel_scrim(ctx):
    print("panel")
    # Check autorisations
    if not ctx.author.guild_permissions.administrator:
        await ctx.interaction.response.send_message(
                                    content="Tu n'as pas les droits",
                                    ephemeral=True)
        return
    if not CHANNEL_BOT in ctx.channel.name:
        await ctx.interaction.response.send_message(
                                    content=f"Utilise {CHANNEL_BOT}",
                                    ephemeral=True)
        return

    await bot.send_main_msg(ctx)
    # Check what can be done
    if bot.discrim.can_begin_registration():  # Start the registration process
        view = View_panel_begin_registration()
        await ctx.interaction.response.send_message(view=view, ephemeral=True)

    elif bot.discrim.can_register():  # End the register process
        view = View_panel_end_registration()
        await ctx.interaction.response.send_message(view=view, ephemeral=True)

    elif bot.discrim.is_registration_over():
        view = View_panel_registration_over()
        await ctx.interaction.response.send_message(view=view, ephemeral=True)



############################### FUNCTIONS ####################################



##############################################################################
############# Function to get the main embed from scratch ####################
##############################################################################

def get_main_embed():
    nb_register, nb_tank, nb_dps, nb_heal = bot.discrim.get_nb_players_roles()
    embed = discord.Embed(
        title="Scrim Intercommunautaire Pug",
        description="Bonjour à tous !!! Pour faciliter la participation au "\
                    "SCRIM on vous propose de vous inscrire avec cette toute"\
                    " nouvelle interface. Choisissez les rôles que vous "\
                    "voulez dans l'ordre que vous voulez !!! waouh !!",
        color=0x432cb5)
    embed.add_field(name="📜 Inscriptions ✒️", value=nb_register, inline=False)
    embed.add_field(name=bot.role_emojis["tank"], value=nb_tank, inline=True)
    embed.add_field(name=bot.role_emojis["dps"], value=nb_dps, inline=True)
    embed.add_field(name=bot.role_emojis["heal"], value=nb_heal, inline=True)
    return embed



##############################################################################
##### Function to get an embed summurazing user selections ###################
##############################################################################

def get_sum_up_selections_embed(discord_id):
    [is_tank, prority_tank, elo_tank, is_dps, prority_dps, elo_dps, is_heal,
        prority_heal, elo_heal] = bot.discrim.get_sum_up_player(discord_id)
    indices_embed = []
    embed = discord.Embed(title="Inscription terminée",
                          color=discord.Color.random())
    if is_tank:
        indices_embed.append(prority_tank)
        indices_embed.sort()
        index = indices_embed.index(prority_tank)
        embed.insert_field_at(index=index,
                              name=bot.role_emojis["tank"],
                              value=f"{bot.priority_emojis[prority_tank]}"\
                                    f"{bot.dict_emojis[elo_tank]}➖")
    if is_dps:
        indices_embed.append(prority_dps)
        indices_embed.sort()
        index = indices_embed.index(prority_dps)
        embed.insert_field_at(index=index,
                              name=bot.role_emojis["dps"],
                              value=f"{bot.priority_emojis[prority_dps]}"\
                                    f"{bot.dict_emojis[elo_dps]}➖")
    if is_heal:
        indices_embed.append(prority_heal)
        indices_embed.sort()
        index = indices_embed.index(prority_heal)
        embed.insert_field_at(index=index,
                              name=bot.role_emojis["heal"],
                              value=f"{bot.priority_emojis[prority_heal]}"\
                                    f"{bot.dict_emojis[elo_heal]}➖")
    return embed



##############################################################################
######## Function to get an embed summurazing the teams ######################
##############################################################################

def get_teams_embeds():
    embeds = []
    nb_teams = bot.discrim.get_nb_teams()
    is_bench_team = bot.discrim.is_bench_team()
    dict_order_role = {"tank": 0, "dps": 2, "heal": 4}
    for i in range(nb_teams):
        if ((i+1) == nb_teams) and is_bench_team:
            embed = discord.Embed(title="~  🪑  ~ LE BANC (cheh) ~  🪑  ~",
                                  color=discord.Color.random())
            for info in bot.discrim.get_bench_players_info():
                name_player = info["name"]
                [is_tank, prority_tank, elo_tank, is_dps, prority_dps,
                    elo_dps, is_heal, prority_heal, elo_heal] = info["info"]
                value = ""
                if is_tank:
                    value += f'{bot.role_emojis["tank"]}'\
                             f'{bot.priority_emojis[prority_tank]}'\
                             f'{bot.dict_emojis[elo_tank]}➖'
                if is_dps:
                    value += f'{bot.role_emojis["dps"]}'\
                             f'{bot.priority_emojis[prority_dps]}'\
                             f'{bot.dict_emojis[elo_dps]}➖'
                if is_heal:
                    value += f'{bot.role_emojis["heal"]}'\
                             f'{bot.priority_emojis[prority_heal]}'\
                             f'{bot.dict_emojis[elo_heal]}➖'
                embed.add_field(name=name_player,
                                value=value[:-1], inline=False)
        else:
            embed = discord.Embed(
                        title=f"~  ✨  ~  ✨  ~ Equipe {i+1} ~  ✨  ~  ✨  ~",
                        color=discord.Color.random())
            for t in range(6):
                embed.add_field(name="absent", value="😴")
            for info in bot.discrim.get_team_players_info(i):
                name_player = info["name"]
                role_player = info["role"][:-1]
                rank_role_player = int(info["role"][-1])-1
                [is_tank, prority_tank, elo_tank, is_dps, prority_dps,
                    elo_dps, is_heal, prority_heal, elo_heal] = info["info"]
                value = " ➖ "
                if is_tank:
                    value += f'{bot.role_emojis["tank"]}'\
                             f'{bot.dict_emojis[elo_tank]}➖'
                if is_dps:
                    value += f'{bot.role_emojis["dps"]}'\
                             f'{bot.dict_emojis[elo_dps]}➖'
                if is_heal:
                    value += f'{bot.role_emojis["heal"]}'\
                             f'{bot.dict_emojis[elo_heal]}➖'
                embed.set_field_at(index=dict_order_role[role_player]
                                         +rank_role_player,
                                   name=bot.role_emojis[role_player]
                                        +"  "+name_player,
                                   value=value[:-1]+" ➖",
                                   inline=False)
        embeds.append(embed)
    return embeds



##############################  CLASSES ######################################



##############################################################################
################ Class to begin the registration #############################
##############################################################################

class View_panel_begin_registration(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Démarrer un Scrim",
                       style=discord.ButtonStyle.green,
                       custom_id="start_scrim")
    async def btn_register_callback(self, button, interaction):
        class Mymodal(Modal):
            def __init__(self):
                super().__init__("Formulaire de lancement du Scrim")
                self.add_item(InputText(
                    label="Description/heure",
                    value="Le Scrim commence ce samedi à 21h30",
                    style=discord.InputTextStyle.long)
                )

            async def callback(self, interaction):
                bot.discrim.begin_registration()
                ctx = await bot.get_application_context(interaction)
                await ctx.channel.purge()
                bot.register_message = self.children[0].value+" @everyone"
                await bot.send_main_msg(ctx)
                view = View_panel_end_registration()
                await interaction.response.send_message(view=view,
                                                        ephemeral=True)
        if bot.discrim.can_begin_registration():  # use case
            modal = Mymodal()
            ctx = await bot.get_application_context(interaction)
            await ctx.send_modal(modal)
        elif bot.discrim.can_register():
            view = View_panel_end_registration()
            await interaction.response.edit_message(view=view)
        elif bot.discrim.is_registration_over():
            view = View_panel_registration_over()
            await interaction.response.edit_message(view=view)



##############################################################################
################# Class to end the registration ##############################
##############################################################################

class View_panel_end_registration(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Création des équipes",
                       style=discord.ButtonStyle.green,
                       custom_id="create_teams")
    async def btn_create_teams_callback(self, button, interaction):
        if bot.discrim.can_begin_registration():
            view = View_panel_begin_registration()
        elif bot.discrim.can_register():  # use case
            bot.discrim.start_scrim()
            ctx = await bot.get_application_context(interaction)
            await bot.send_main_msg(ctx)
            view = View_panel_registration_over()
        elif bot.discrim.is_registration_over():
            view = View_panel_registration_over()
        await interaction.response.edit_message(view=view)

    @discord.ui.button(label="Liste joueurs",
                       style=discord.ButtonStyle.blurple,
                       custom_id="get_list_players")
    async def btn_get_list_player_callback(self, button, interaction):
        content = "Liste des joueurs inscrits : \n"
        for player in bot.discrim.get_list_player():
            [is_tank, priority_tank, elo_tank,
             is_dps, priority_dps, elo_dps, is_heal,
             priority_heal, elo_heal] = bot.discrim.get_sum_up_player2(player)
            content += f"{player} "
            if is_tank:
                content += f'{bot.role_emojis["tank"]}'\
                           f"{bot.priority_emojis[priority_tank]}"\
                           f"{bot.dict_emojis[elo_tank]}➖"
            else:
                content += "➖➖➖➖"
            if is_dps:
                content += f'{bot.role_emojis["dps"]}'\
                           f"{bot.priority_emojis[priority_dps]}"\
                           f"{bot.dict_emojis[elo_dps]}➖"
            else:
                content += "➖➖➖➖"
            if is_heal:
                content += f'{bot.role_emojis["heal"]}'\
                           f"{bot.priority_emojis[priority_heal]}"\
                           f"{bot.dict_emojis[elo_heal]}"
            else:
                content += "➖➖➖"
            content += "\n"
        await interaction.response.send_message(content=content, 
                                                ephemeral=True)

    @discord.ui.button(label="Annuler le Scrim",
                       style=discord.ButtonStyle.red,
                       custom_id="stop_scrim")
    async def btn_stop_callback(self, button, interaction):
        if bot.discrim.can_begin_registration():
            view = View_panel_begin_registration()
        else:
            view = View_panel_stop()
        await interaction.response.edit_message(view=view)



##############################################################################
############ Class for the register and unregister buttons ###################
##############################################################################

class View_register_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="S'inscire", style=discord.ButtonStyle.green,
                       custom_id="initialisation_register")
    async def btn_register_callback(self, button, interaction):
        if bot.discrim.can_register():
            if bot.discrim.is_registered(interaction.user):
                await interaction.response.send_message(
                                content="Vous êtes déjà inscrit !",
                                ephemeral=True)
            else:
                print(f"{interaction.user} register")
                view = View_register_request()
                await interaction.response.send_message(
                                content="",
                                view=view,
                                ephemeral=True)
        else:
            await interaction.response.send_message(
                            content="Les inscriptions sont terminées !",
                            ephemeral=True)

    @discord.ui.button(label="Se désinscrire", style=discord.ButtonStyle.red,
                       custom_id="initialisation_unregister")
    async def btn_unregister_callback(self, button, interaction):
        if bot.discrim.can_register():
            if bot.discrim.is_registered(interaction.user):
                bot.discrim.remove_register_player(interaction.user)
                print(f"{interaction.user} unregister")
                ctx = await bot.get_application_context(interaction)
                await bot.send_main_msg(ctx)
                await interaction.response.send_message(
                                content="Vous avez quitté le SCRM, coward ..",
                                ephemeral=True)
            else:
                await interaction.response.send_message(
                                content="Vous n'êtes même pas inscrit",
                                ephemeral=True)
        else:
            await interaction.response.send_message(
                            content="Les inscriptions sont terminées !",
                            ephemeral=True)



##############################################################################
############# Class for the register request #################################
##############################################################################

class View_register_request(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(custom_id="role_selection",
                       min_values=1,
                       max_values=3,
                       placeholder="Choisis un rôle",
                       options=[
        discord.SelectOption(label="Tank",
                             value='tank',
                             emoji=bot.role_emojis["tank"]),
        discord.SelectOption(label="DPS",
                             value='dps',
                             emoji=bot.role_emojis["dps"]),
        discord.SelectOption(label="Heal",
                             value='heal',
                             emoji=bot.role_emojis["heal"])])
    async def select_role_callback(self, select, interaction):
        tank = False
        dps = False
        heal = False
        if "tank" in select.values:
            tank = True
        if "dps" in select.values:
            dps = True
        if "heal" in select.values:
            heal = True
        bot.discrim.add_register_player(interaction.user, tank, dps, heal)

    @discord.ui.button(custom_id="suivant", label="Suivant",
                       style=discord.ButtonStyle.green)
    async def button_suivant_callback(self, button, interaction):
        if bot.discrim.get_is_choosen(interaction.user, "tank"):
            view = get_view_tank_request()
        elif bot.discrim.get_is_choosen(interaction.user, "dps"):
            view = get_view_dps_request()
        elif bot.discrim.get_is_choosen(interaction.user, "heal"):
            view = get_view_heal_request()
        else:
            view = self
        await interaction.response.edit_message(view=view)



##############################################################################
############# Class for the tank register request ############################
##############################################################################

def get_view_tank_request():
    class View_tank_request(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.select(custom_id=f"priority_selection_tank",
                           min_values=1,
                           max_values=1,
                           placeholder=f"Choisis ta priorité pour le tank",
                           options=[
            discord.SelectOption(label=f"{bot.priority_emojis[1]} J'ai "\
                                       f"vraiment envie de jouer tank",
                                 value=1),
            discord.SelectOption(label=f"{bot.priority_emojis[2]} Je peux "\
                                       f"jouer tank",
                                 value=2),
            discord.SelectOption(label=f"{bot.priority_emojis[3]} Je joue "\
                                       f"tank seulement si nécessaire",
                                 value=3)])
        async def select_temp1_callback(self, select, interaction):
            bot.discrim.set_priority_register(interaction.user, "tank",
                                              int(select.values[0]))

        @discord.ui.select(custom_id=f"elo_selection_tank",
                           min_values=1,
                           max_values=1,
                           placeholder=f"Choisis ton elo tank",
                           options=bot.elo_options)
        async def select_temp2_callback(self, select, interaction):
            bot.discrim.set_elo_register(interaction.user, "tank",
                                         int(select.values[0]))

        @discord.ui.button(custom_id="retour", label="Retour",
                           style=discord.ButtonStyle.red)
        async def button_retour_callback(self, button, interaction):
            view = View_register_request()
            await interaction.response.edit_message(view=view)

        @discord.ui.button(custom_id="suivant", label="Suivant",
                           style=discord.ButtonStyle.green)
        async def button_suivant_callback(self, button, interaction):
            embed = None
            if bot.discrim.get_is_choosen(interaction.user, "dps"):
                view = get_view_dps_request()
            elif bot.discrim.get_is_choosen(interaction.user, "heal"):
                view = get_view_heal_request()
            else:
                view = View_sum_up_request()
                embed = get_sum_up_selections_embed(interaction.user)
            await interaction.response.edit_message(embed=embed, view=view)
    return View_tank_request()



##############################################################################
############# Class for the dps register request #############################
##############################################################################

def get_view_dps_request():
    class View_dps_request(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.select(custom_id=f"priority_selection_dps",
                           min_values=1,
                           max_values=1,
                           placeholder=f"Choisis ta priorité pour le dps",
                           options=[
            discord.SelectOption(label=f"{bot.priority_emojis[1]} J'ai "\
                                       f"vraiment envie de jouer dps",
                                 value=1),
            discord.SelectOption(label=f"{bot.priority_emojis[2]} Je "\
                                       f"peux jouer dps",
                                 value=2),
            discord.SelectOption(label=f"{bot.priority_emojis[3]} Je joue "\
                                       f"dps seulement si nécessaire",
                                 value=3)])
        async def select_temp3_callback(self, select, interaction):
            bot.discrim.set_priority_register(interaction.user, "dps",
                                              int(select.values[0]))

        @discord.ui.select(custom_id=f"elo_selection_dps",
                           min_values=1,
                           max_values=1,
                           placeholder=f"Choisis ton elo dps",
                           options=bot.elo_options)
        async def select_temp4_callback(self, select, interaction):
            bot.discrim.set_elo_register(interaction.user, "dps",
                                         int(select.values[0]))

        @discord.ui.button(custom_id="retour", label="Retour",
                           style=discord.ButtonStyle.red)
        async def button_retour_callback(self, button, interaction):
            if bot.discrim.get_is_choosen(interaction.user, "tank"):
                view = get_view_tank_request()
            else:
                view = View_register_request()
            await interaction.response.edit_message(view=view)

        @discord.ui.button(custom_id="suivant", label="Suivant",
                           style=discord.ButtonStyle.green)
        async def button_suivant_callback(self, button, interaction):
            embed = None
            if bot.discrim.get_is_choosen(interaction.user, "heal"):
                view = get_view_heal_request()
            else:
                view = View_sum_up_request()
                embed = get_sum_up_selections_embed(interaction.user)
            await interaction.response.edit_message(embed=embed, view=view)
    return View_dps_request()



##############################################################################
############# Class for the heal register request ############################
##############################################################################

def get_view_heal_request():
    class View_heal_request(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.select(custom_id=f"priority_selection_heal",
                           min_values=1,
                           max_values=1,
                           placeholder=f"Choisis ta priorité pour le heal",
                           options=[
            discord.SelectOption(label=f"{bot.priority_emojis[1]} J'ai "\
                                       f"vraiment envie de jouer heal",
                                 value=1),
            discord.SelectOption(label=f"{bot.priority_emojis[2]} Je peux "\
                                       f"jouer heal",
                                 value=2),
            discord.SelectOption(label=f"{bot.priority_emojis[3]} Je joue "\
                                       f"heal seulement si nécessaire",
                                 value=3)])
        async def select_temp5_callback(self, select, interaction):
            bot.discrim.set_priority_register(interaction.user, "heal",
                                              int(select.values[0]))

        @discord.ui.select(custom_id=f"elo_selection_heal",
                           min_values=1,
                           max_values=1,
                           placeholder=f"Choisis ton elo heal",
                           options=bot.elo_options)
        async def select_temp6_callback(self, select, interaction):
            bot.discrim.set_elo_register(interaction.user, "heal",
                                         int(select.values[0]))

        @discord.ui.button(custom_id="retour", label="Retour",
                           style=discord.ButtonStyle.red)
        async def button_retour_callback(self, button, interaction):
            if bot.discrim.get_is_choosen(interaction.user, "dps"):
                view = get_view_dps_request()
            elif bot.discrim.get_is_choosen(interaction.user, "tank"):
                view = get_view_tank_request()
            else:
                view = View_register_request()
            await interaction.response.edit_message(view=view)

        @discord.ui.button(custom_id="suivant", label="Suivant",
                           style=discord.ButtonStyle.green)
        async def button_suivant_callback(self, button, interaction):
            view = View_sum_up_request()
            embed = get_sum_up_selections_embed(interaction.user)
            await interaction.response.edit_message(embed=embed, view=view)
    return View_heal_request()



##############################################################################
############# Class for the sum up  register request #########################
##############################################################################

class View_sum_up_request(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(custom_id="retour", label="Retour",
                       style=discord.ButtonStyle.red)
    async def button_retour_callback(self, button, interaction):
        if bot.discrim.get_is_choosen(interaction.user, "heal"):
            view = get_view_heal_request()
        elif bot.discrim.get_is_choosen(interaction.user, "dps"):
            view = get_view_dps_request()
        elif bot.discrim.get_is_choosen(interaction.user, "tank"):
            view = get_view_tank_request()
        else:
            view = View_register_request()
        await interaction.response.edit_message(embed=None, view=view)

    @discord.ui.button(custom_id="validate_selection", label="Valider",
                       style=discord.ButtonStyle.green)
    async def button_validate_callback(self, button, interaction):
        bot.discrim.validate_registration(interaction.user)
        ctx = await bot.get_application_context(interaction)
        if bot.discrim.can_register():
            await bot.send_main_msg(ctx)
        else:
            await bot.send_main_msg(ctx)
        await interaction.response.edit_message(view=None)



##############################################################################
########### Class for to access a panel of commands ##########################
##############################################################################

class View_panel_registration_over(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def __get_view(self, view, content):
        if bot.discrim.can_begin_registration():
            view = View_panel_begin_registration()
            content = ""
        elif bot.discrim.can_register():
            view = View_panel_end_registration()
            content = ""
        return view, content

    @discord.ui.button(custom_id="removeplayer", label="Remove player",
                       style=discord.ButtonStyle.red)
    async def button_removeplayer_callback(self, button, interaction):
        view, _ = self.__get_view(get_view_panel_removeplayer(), "")
        await interaction.response.edit_message(view=view)

    @discord.ui.button(custom_id="switch2player", label="Switch 2 players",
                       style=discord.ButtonStyle.blurple)
    async def button_switch2player_callback(self, button, interaction):
        view, _ = self.__get_view(get_view_panel_switch2player(), "")
        await interaction.response.edit_message(view=view)

    @discord.ui.button(custom_id="redoTeams", label="Recreate teams (auto)",
                       style=discord.ButtonStyle.blurple)
    async def button_redoTeams_callback(self, button, interaction):
        content = "Toutes les équipes peuvent être changées entierement"
        view, content = self.__get_view(View_panel_redoTeams(), content)
        await interaction.response.edit_message(content=content, view=view)

    @discord.ui.button(custom_id="ping", label="Ping @everyone",
                       style=discord.ButtonStyle.green)
    async def button_ping_callback(self, button, interaction):
        ctx = await bot.get_application_context(interaction)
        content = "@everyone"
        await bot.send_main_msg(ctx, content)

    @discord.ui.button(custom_id="stop", label="Stop Scrim",
                       style=discord.ButtonStyle.red)
    async def button_stop_callback(self, button, interaction):
        content = "Toutes les informations des joueurs vont être "\
                  "définitivement perdues"
        view, content = self.__get_view(View_panel_stop(), content)
        await interaction.response.edit_message(content=content, view=view)



##############################################################################
################ Class for to remove a player ################################
##############################################################################

def get_view_panel_removeplayer():
    nb_teams = bot.discrim.get_nb_teams()
    res = []
    if bot.discrim.is_bench_team():
        res.append(discord.SelectOption(label="Bench", value="bench"))
        nb_teams -= 1
    for i in range(nb_teams):
        res.append(discord.SelectOption(label=f"Equipe {i+1}", value=i))
    options_team = res
    team_id = bot.discrim.get_panel_info("removeplayer", "team")
    # Is the team of the player to delete already selected ?
    if team_id is None:
        options_player = [discord.SelectOption(label="test", value="test")]
        select_disable = True
        validate_disable = True
        select_placeholder_team = "Choisis la team du joueur à supprimer"
        select_placeholder_player = "Choisis le joueur à supprimer"
    else:
        dict_players = bot.discrim.get_panel_namesanddiscordid_team(team_id)
        options_player = []
        for discord_id in dict_players.keys():
            options_player.append(discord.SelectOption(
                label=dict_players[discord_id], value=discord_id))
        select_disable = False
        if team_id == "bench":
            select_placeholder_team = "Bench"
        else:
            select_placeholder_team = f"Equipe {int(team_id)+1}"

        player_selected = bot.discrim.get_panel_info(
            "removeplayer", "discord_id")
        # Is the player to delete already selected ?
        if player_selected is None:
            select_placeholder_player = "Choisis le joueur à supprimer"
            validate_disable = True
        else:
            select_placeholder_player = player_selected
            validate_disable = False

    class View_panel_removeplayer(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.select(custom_id="team",
                           min_values=1,
                           max_values=1,
                           placeholder=select_placeholder_team,
                           options=options_team)
        async def select_team_callback(self, select, interaction):
            bot.discrim.set_panel_info(
                "removeplayer", "team", select.values[0])
            view = get_view_panel_removeplayer()
            await interaction.response.edit_message(view=view)

        @discord.ui.select(custom_id="player",
                           min_values=1,
                           max_values=1,
                           placeholder=select_placeholder_player,
                           options=options_player,
                           disabled=select_disable)
        async def select_player_callback(self, select, interaction):
            bot.discrim.set_panel_info("removeplayer",
                                       "discord_id",
                                       select.values[0])
            view = get_view_panel_removeplayer()
            await interaction.response.edit_message(view=view)

        @discord.ui.button(custom_id="retour", label="Retour",
                           style=discord.ButtonStyle.red)
        async def button_retour_callback(self, button, interaction):
            bot.discrim.create_fresh_panel()
            view = View_panel_registration_over()
            await interaction.response.edit_message(view=view)

        @discord.ui.button(custom_id="validate_selection",
                           label="Valider",
                           style=discord.ButtonStyle.green,
                           disabled=validate_disable)
        async def button_validate_callback(self, button, interaction):
            bot.discrim.panel_removeplayer()
            ctx = await bot.get_application_context(interaction)
            await bot.send_main_msg(ctx)
            view = View_panel_registration_over()
            await interaction.response.edit_message(view=view)

    return View_panel_removeplayer()



##############################################################################
################ Class for to switch 2 player ################################
##############################################################################

def get_view_panel_switch2player():
    nb_teams = bot.discrim.get_nb_teams()
    res = []
    if bot.discrim.is_bench_team():
        res.append(discord.SelectOption(label="Bench", value="bench"))
        nb_teams -= 1
    for i in range(nb_teams):
        res.append(discord.SelectOption(label=f"Equipe {i+1}", value=i))
    options_team = res
    team1_id = bot.discrim.get_panel_info("switch2player", "team1")
    team2_id = bot.discrim.get_panel_info("switch2player", "team2")
    # Is the team of the player 1 already selected ?
    if team1_id is None:
        options_player1 = [discord.SelectOption(label="test", value="test")]
        select1_disable = True
        validate1_disable = True
        select1_placeholder_team = "Choisis l'équipe de joueur 1 à échanger"
        select1_placeholder_player = "Choisis le joueur 1 à échanger"
    else:
        dict_players = bot.discrim.get_panel_namesanddiscordidrole_team(
            team1_id)
        options_player1 = []
        for discord_id in dict_players.keys():
            options_player1.append(discord.SelectOption(
                label=dict_players[discord_id], value=discord_id))
        select1_disable = False
        if team1_id == "bench":
            select1_placeholder_team = "Bench"
        else:
            select1_placeholder_team = f"Equipe {int(team1_id)+1}"

        player1_selected = bot.discrim.get_panel_info(
            "switch2player", "discord_id1")
        # Is the player 1 already selected ?
        if player1_selected is None:
            select1_placeholder_player = "Choisis le joueur 1 à échanger"
            validate1_disable = True
        else:
            select1_placeholder_player = player1_selected
            validate1_disable = False

    # Is the team of the player 2 already selected ?
    if team2_id is None:
        options_player2 = [discord.SelectOption(label="test", value="test")]
        select2_disable = True
        validate2_disable = True
        select2_placeholder_team = "Choisis l'équipe de joueur 2 à échanger"
        select2_placeholder_player = "Choisis le joueur 2 à échanger"
    else:
        dict_players = bot.discrim.get_panel_namesanddiscordidrole_team(
            team2_id)
        options_player2 = []
        for discord_id in dict_players.keys():
            options_player2.append(discord.SelectOption(
                label=dict_players[discord_id],
                value=discord_id))
        select2_disable = False
        if team2_id == "bench":
            select2_placeholder_team = "Bench"
        else:
            select2_placeholder_team = f"Equipe {int(team2_id)+1}"

        player2_selected = bot.discrim.get_panel_info("switch2player",
                                                      "discord_id2")
        # Is the player 2 already selected ?
        if player2_selected is None:
            select2_placeholder_player = "Choisis le joueur 2 à échanger"
            validate2_disable = True
        else:
            select2_placeholder_player = player2_selected
            validate2_disable = False

    validate_disable = validate1_disable or validate2_disable

    class View_panel_switch2player(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.select(custom_id="team1",
                           min_values=1,
                           max_values=1,
                           placeholder=select1_placeholder_team,
                           options=options_team)
        async def select_team1_callback(self, select, interaction):
            bot.discrim.set_panel_info("switch2player",
                                       "team1",
                                       select.values[0])
            view = get_view_panel_switch2player()
            await interaction.response.edit_message(view=view)

        @discord.ui.select(custom_id="player1",
                           min_values=1,
                           max_values=1,
                           placeholder=select1_placeholder_player,
                           options=options_player1,
                           disabled=select1_disable)
        async def select_player1_callback(self, select, interaction):
            bot.discrim.set_panel_info("switch2player",
                                       "discord_id1",
                                       select.values[0])
            view = get_view_panel_switch2player()
            await interaction.response.edit_message(view=view)

        @discord.ui.select(custom_id="team2",
                           min_values=1,
                           max_values=1,
                           placeholder=select2_placeholder_team,
                           options=options_team)
        async def select_team2_callback(self, select, interaction):
            bot.discrim.set_panel_info("switch2player",
                                       "team2",
                                       select.values[0])
            view = get_view_panel_switch2player()
            await interaction.response.edit_message(view=view)

        @discord.ui.select(custom_id="player2",
                           min_values=1,
                           max_values=1,
                           placeholder=select2_placeholder_player,
                           options=options_player2,
                           disabled=select2_disable)
        async def select_player2_callback(self, select, interaction):
            bot.discrim.set_panel_info("switch2player",
                                       "discord_id2",
                                       select.values[0])
            view = get_view_panel_switch2player()
            await interaction.response.edit_message(view=view)

        @discord.ui.button(custom_id="retour", label="Retour",
                           style=discord.ButtonStyle.red)
        async def button_retour_callback(self, button, interaction):
            bot.discrim.create_fresh_panel()
            view = View_panel_registration_over()
            await interaction.response.edit_message(view=view)

        @discord.ui.button(custom_id="validate_selection",
                           label="Valider",
                           style=discord.ButtonStyle.green,
                           disabled=validate_disable)
        async def button_validate_callback(self, button, interaction):
            bot.discrim.panel_switch2player()
            ctx = await bot.get_application_context(interaction)
            await bot.send_main_msg(ctx)
            view = View_panel_registration_over()
            await interaction.response.edit_message(view=view)

    return View_panel_switch2player()



##############################################################################
################### Class for to redo teams ##################################
##############################################################################

class View_panel_redoTeams(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(custom_id="retour", label="Retour",
                       style=discord.ButtonStyle.red)
    async def button_retour_callback(self, button, interaction):
        view = View_panel_registration_over()
        await interaction.response.edit_message(content="", view=view)

    @discord.ui.button(custom_id="validate_selection", label="Valider",
                       style=discord.ButtonStyle.green)
    async def button_validate_callback(self, button, interaction):
        bot.discrim.panel_reset_teams()
        ctx = await bot.get_application_context(interaction)
        await bot.send_main_msg(ctx)
        view = View_panel_registration_over()
        await interaction.response.edit_message(content="", view=view)



##############################################################################
##### Class for the register button after teams are formed ###################
##############################################################################

class View_register_after_team(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(custom_id="initialisation_register", label="S'inscire",
                       style=discord.ButtonStyle.green, )
    async def btn_register_callback(self, button, interaction):
        if bot.discrim.is_registered(interaction.user):
            await interaction.response.send_message(
                                content="Vous êtes déjà inscrit !",
                                ephemeral=True)
        else:
            print(f"{interaction.user} register")
            view = View_register_request()
            await interaction.response.send_message(content="",
                                                    view=view,
                                                    ephemeral=True)



##############################################################################
################# Class to stop the scrim ####################################
##############################################################################

class View_panel_stop(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(custom_id="retour", label="Retour",
                       style=discord.ButtonStyle.red)
    async def button_retour_callback(self, button, interaction):
        if bot.discrim.can_register():
            view = View_panel_end_registration()
        elif bot.discrim.is_registration_over():
            view = View_panel_registration_over()
        await interaction.response.edit_message(content="", view=view)

    @discord.ui.button(custom_id="validate_selection", label="Valider",
                       style=discord.ButtonStyle.green)
    async def button_validate_callback(self, button, interaction):
        bot.discrim = Discord_scrim()
        ctx = await bot.get_application_context(interaction)
        await ctx.channel.purge()
        view = View_panel_begin_registration()
        await interaction.response.edit_message(content="", view=view)






def get_token(name_file_token="token"):
    with open(name_file_token, "r") as file:
        for line in file:
            if line.startswith("#"):
                continue
            return line


if __name__ == "__main__":
    token = get_token()
    bot.run(token)