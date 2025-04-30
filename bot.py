import discord
import os
import requests
import aiohttp  # non blocking post rq
import json
import base64
import jwt
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
from discord.ext import commands
from discord import Interaction, ui

API_URL = os.getenv("URL_API")
FRONT_URL = os.getenv("URL_FRONT")
SECRET_TOKEN = os.getenv("TOKEN_SECRET")

WEAPON_CHOICES = [
    "cannon",
    "deck_cannon",
    "emp_missiles",
    "flak_battery",
    "he_missiles",
    "large_cannon",
    "mines",
    "nukes",
    "railgun",
    "disruptors",
    "heavy_laser",
    "ion_beam",
    "ion_prism",
    "laser",
    "mining_laser",
    "point_defense",
    "chaingun",
]
USER_TAGS = [
    "mono_thrust",
    "multi_thrust",
    "omni_thrust",
    "no_thrust",
    "armor_defenses",
    "mixed_defenses",
    "shield_defenses",
    "no_defenses",
    "kiter",
    "spinner",
    "avoider",
    "rammer",
    "orbiter",
    "scout/racer",
    "broadsider",
    "splitter",
    "diagonal",
    "domination_ship",
    "elimination_ship",
    "campaign_ship",
    "waste_ship",  #
    "debugging_tool",
    "sundiver",
    "cargo_ship",
]
UTILITY_TAGS = [
    "ammo_factory",
    "emp_factory",
    "he_factory",
    "mine_factory",
    "nuke_factory",
    "boost_thruster",
    "airlock",
    "campaign_factories",
    "explosive_charges",
    "fire_extinguisher",
    "no_fire_extinguishers",
    "large_reactor",
    "large_shield",
    "medium_reactor",
    "sensor",
    "small_hyperdrive",
    "small_reactor",
    "small_shield",
    "tractor_beams",
    "hyperdrive_relay",
    "large_hyperdrive",
    "rocket_thruster",
]
ORDER_CHOICES = ["pop", "fav", "new"]
BRAND_CHOICES = ["exl", "all"]

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


class TagSelect(ui.Select):
    def __init__(self, label, options, callback_attr):
        super().__init__(
            placeholder=f"{label} (Multi-Select)",
            min_values=0,
            max_values=len(options),
            options=[discord.SelectOption(label=o) for o in options],
        )
        self.callback_attr = callback_attr

    async def callback(self, interaction: Interaction):
        setattr(self.view, self.callback_attr, self.values)
        await interaction.response.defer()


class SingleTagSelect(ui.Select):
    def __init__(self, label, options, callback_attr):
        super().__init__(
            placeholder=f"{label} (Multi-Select)",
            min_values=0,
            max_values=1,
            options=[discord.SelectOption(label=o) for o in options],
        )
        self.callback_attr = callback_attr

    async def callback(self, interaction: Interaction):
        setattr(self.view, self.callback_attr, self.values)
        await interaction.response.defer()


class SearchView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.weapon_include = []
        self.weapon_exclude = []
        self.user_include = []
        self.user_exclude = []
        self.util_include = []
        self.util_exclude = []
        self.minprice = None
        self.maxprice = None
        self.author = None
        self.crew = None
        self.order = None
        self.brand = None

    async def interaction_check(self, interaction: Interaction):
        return True  # optionally restrict to user

    @ui.button(label="1. Weapon Tags", style=discord.ButtonStyle.primary)
    async def weapon_tags(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Select weapon tag filters:", view=WeaponTagView(self)
        )

    @ui.button(label="2. User Tags", style=discord.ButtonStyle.primary)
    async def user_tags(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Select user tag filters:", view=UserTagView(self)
        )

    @ui.button(label="3. Utility Tags", style=discord.ButtonStyle.primary)
    async def utility_tags(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Select utility tag filters:", view=UtilityTagView(self)
        )

    @ui.button(label="4. Other Filters", style=discord.ButtonStyle.secondary)
    async def other_filters(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(OtherTagsModal(self))

    @ui.button(label="5. Submit search", style=discord.ButtonStyle.primary)
    async def submit_search(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Submit search:", view=ValidSearchView(self), delete_after=5
        )


class WeaponTagView(ui.View):
    def __init__(self, parent_view: SearchView):
        super().__init__(timeout=None)
        self.parent_view = parent_view
        self.include = []
        self.exclude = []

        self.add_item(TagSelect("Include Weapon Tags", WEAPON_CHOICES, "include"))
        self.add_item(TagSelect("Exclude Weapon Tags", WEAPON_CHOICES, "exclude"))
        # self.add_item(ui.Button(label="Back", style=discord.ButtonStyle.secondary, custom_id="confirm_weapon"))

    async def interaction_check(self, interaction: Interaction):
        return True

    @ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Returned to main view.", view=self.parent_view
        )

    @ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        self.parent_view.weapon_include = self.include
        self.parent_view.weapon_exclude = self.exclude
        await interaction.response.edit_message(
            content="Returned to main view.", view=self.parent_view
        )


class UserTagView(ui.View):
    def __init__(self, parent_view: SearchView):
        super().__init__(timeout=None)
        self.parent_view = parent_view
        self.include = []
        self.exclude = []

        self.add_item(TagSelect("Include User Tags", USER_TAGS, "include"))
        self.add_item(TagSelect("Exclude User Tags", USER_TAGS, "exclude"))
        # self.add_item(ui.Button(label="Back", style=discord.ButtonStyle.secondary, custom_id="confirm_usertag"))

    async def interaction_check(self, interaction: Interaction):
        return True

    @ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Returned to main view.", view=self.parent_view
        )

    @ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        self.parent_view.user_include = self.include
        self.parent_view.user_exclude = self.exclude
        await interaction.response.edit_message(
            content="Returned to main view.", view=self.parent_view
        )


class UtilityTagView(ui.View):
    def __init__(self, parent_view: SearchView):
        super().__init__(timeout=None)
        self.parent_view = parent_view
        self.include = []
        self.exclude = []

        self.add_item(TagSelect("Include Utility Tags", UTILITY_TAGS, "include"))
        self.add_item(TagSelect("Exclude Utility Tags", UTILITY_TAGS, "exclude"))
        # self.add_item(ui.Button(label="Back", style=discord.ButtonStyle.secondary, custom_id="confirm_utiltag"))

    async def interaction_check(self, interaction: Interaction):
        return True

    @ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Returned to main view.", view=self.parent_view
        )

    @ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        self.parent_view.util_include = self.include
        self.parent_view.util_exclude = self.exclude
        await interaction.response.edit_message(
            content="Returned to main view.", view=self.parent_view
        )


class OtherTagsModal(ui.Modal, title="Other Filters"):
    author = ui.TextInput(label="Author", required=False)
    crew = ui.TextInput(label="Crew", required=False)
    minprice = ui.TextInput(label="Min price", required=False)
    maxprice = ui.TextInput(label="Max price", required=False)

    def __init__(self, parent_view: SearchView):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: Interaction):
        # Save inputs to parent view
        self.parent_view.author = self.author.value
        self.parent_view.crew = int(self.crew.value) if self.crew.value.isdigit() else None
        self.parent_view.minprice = (
            int(self.minprice.value) if self.minprice.value.isdigit() else None
        )
        self.parent_view.maxprice = (
            int(self.maxprice.value) if self.maxprice.value.isdigit() else None
        )

        await interaction.response.edit_message(
            content="Returned to main view.", view=self.parent_view
        )


class ValidSearchView(ui.View):
    def __init__(self, parent_view: SearchView):
        super().__init__(timeout=None)
        self.parent_view = parent_view
        self.order = None
        self.brand = None

        self.add_item(SingleTagSelect("Result order", ORDER_CHOICES, "order"))
        self.add_item(TagSelect("Library filter", BRAND_CHOICES, "brand"))
        # self.add_item(ui.Button(label="Back", style=discord.ButtonStyle.secondary, custom_id="confirm_searchtag"))

    async def interaction_check(self, interaction: Interaction):
        return True

    @ui.button(label="Back", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="Returned to main view.", view=self.parent_view
        )

    @ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: Interaction, button: ui.Button):
        self.parent_view.order = self.order
        self.parent_view.brand = self.brand
        params = {}

        for w in self.parent_view.weapon_include:
            params[w] = 1
        for w in self.parent_view.weapon_exclude:
            params[w] = 0
        for w in self.parent_view.user_include:
            params[w] = 1
        for w in self.parent_view.user_exclude:
            params[w] = 0
        for w in self.parent_view.util_include:
            params[w] = 1
        for w in self.parent_view.util_exclude:
            params[w] = 0
        if self.parent_view.minprice:
            params["minprice"] = self.parent_view.minprice
        if self.parent_view.maxprice is not None:
            params["maxprice"] = self.parent_view.maxprice
        if self.parent_view.crew is not None:
            params["max-crew"] = self.parent_view.crew
        if self.parent_view.order:
            params["order"] = self.parent_view.order[0]
        if self.parent_view.brand:
            params["brand"] = self.parent_view.brand[0]

        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{API_URL}/search?{query}"
        response = requests.get(url=url)
        data = json.loads(response.content)

        ships = data["data"][:5]  # First 5 ships

        embeds = []

        for ship in ships:
            ship_url = f"{FRONT_URL}/ship/{ship['ship_id']}"  # Optional, adjust as needed
            embed = discord.Embed(
                title=ship["ship_name"],
                url=ship_url,
                description=f"By **{ship['ship_author']}** | Tags: `{', '.join(ship['ship_tags'])}`",
                color=discord.Color.blue(),
            )
            embed.set_image(url=ship["ship_png"])
            embed.add_field(name="Cost", value=f"{ship['ship_cost']:,}", inline=True)
            embed.add_field(name="Crew", value=str(ship["ship_crew"]), inline=True)
            embed.add_field(name="Popularity", value=str(ship["ship_popularity"]), inline=True)
            embed.add_field(name="Submitted By", value=ship["ship_submitted_by"], inline=True)
            embed.add_field(
                name="Date Submitted", value=ship["ship_date_submitted"].split(" ")[0], inline=True
            )
            embed.set_footer(text=f"Brand: {ship['brand']} | Favorites: {ship['number_fav']}")

            embeds.append(embed)

        await interaction.response.send_message(embeds=embeds, ephemeral=True)


@bot.tree.command(name="upload")
async def upload_ship(interaction: discord.Interaction, ship: discord.Attachment):
    author_name = interaction.user.name
    author_disc = interaction.user.discriminator
    if author_name and author_disc:
        user = f"{author_name}#{author_disc}"

    await interaction.response.defer()

    image_bytes = await ship.read()
    encoded_data = base64.b64encode(image_bytes).decode("utf-8")

    # Generate token for auth
    payload = {
        "user": user,
        "iat": datetime.now(tz=timezone.utc),
        "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=15),
    }
    token = jwt.encode(payload, SECRET_TOKEN, algorithm="HS256")

    # Call API with aiohttp
    base_path = "/insert_ship"
    target = urljoin(API_URL, base_path)
    json_data = {"token": token, "image": encoded_data}

    async with aiohttp.ClientSession() as session:
        async with session.post(target, json=json_data) as resp:
            if resp.status != 200:
                await interaction.followup.send("Error adding ship (API failed)")
                return
            data = await resp.json()

    try:
        ship_id = data["data"]["ship_id"]
        edit_url = f"{FRONT_URL}/edit/{ship_id}"
        view_url = f"{FRONT_URL}/ship/{ship_id}"
        await interaction.followup.send(
            f"Ship added to library.\nedit: {edit_url}\nview: {view_url}", suppress_embeds=True
        )
    except Exception as e:
        print("Exception:", e)
        await interaction.followup.send("Error adding ship (Invalid response)")


@bot.tree.command(name="search")
async def search(interaction: Interaction):
    await interaction.response.send_message(
        "Use the buttons below to filter your query:", view=SearchView(), ephemeral=True
    )


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f"Logged in as {bot.user}")


bot.run(os.getenv("DISCORD_API"))
