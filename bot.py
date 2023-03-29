import json
from random import randint
from typing import Literal
from rolldice import roll_dice
from random import randint
import interactions, dotenv, os, re
from battle_sim import Enemy, Player

dotenv.load_dotenv()

bot = interactions.Client(token=os.getenv("BOT_TOKEN"))

possible_enemies = json.load(open("enemies.json", "r"))
spells = json.load(open("spells.1.json", "r"))

spells_by_name = {}
# process spells
for spell in spells:
    spells_by_name[spell["name"].lower()] = spell

alive_combatants = []


@bot.command(
    name="ping",
    description="Check Latency",
    scope=1030231553386754188,
)
async def ping(ctx: interactions.CommandContext):
    await ctx.send("Pong!")


@bot.command(
    name="restart",
    description="Restart the bot",
    scope=1030231553386754188,
)
async def ping(ctx: interactions.CommandContext):
    await ctx.send("Restarting...")
    os.system("python3 bot.py")
    quit()


@bot.command(
    name="roll",
    description="Rolls a number of dice",
    scope=1030231553386754188,
)
@interactions.option()
@interactions.option()
async def roll(
    ctx: interactions.CommandContext,
    dice_notation: str,
    advantage: str = "None",
):
    
    if advantage != "None":
        (smaller_total, smaller_explanation), (larger_total, larger_explanation) = sorted(
            [roll_dice(dice_notation), roll_dice(dice_notation)],
            reverse=advantage == "Disadvantage"
        )
        await ctx.send(
            f"""
:game_die: {dice_notation} (With {advantage})
~~{smaller_explanation} = {smaller_total}~~
{larger_explanation} = {larger_total}
**{larger_total}**
        """.strip()
        )
    else:
        total, explanation = roll_dice(dice_notation)
        await ctx.send(f":game_die: {dice_notation}\n{explanation} = {total}")

def replace_html_tags(string):
    return (
        string.replace("<em>", "")
        .replace("</em>", "")
        .replace("<strong>", "**")
        .replace("</strong>", "**")
        .replace("<p>", "")
        .replace("</p>", "")
        .replace(".**", ".")
    )  # still some errors and weird characters


def split_text(text):
    sentences = re.split(
        r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!) ", text
    )  # what is this regex
    chunks = [sentences[i : i + 3] for i in range(0, len(sentences), 3)]

    new_text = "\n\n".join([" ".join(chunk) for chunk in chunks])

    return ((((new_text))))

def sort_combatants():
    alive_combatants.sort(key=lambda combatant: combatant.initiative, reverse=True)

@bot.command(
    name="stats",
    description="returns an enemies stats",
    scope=1030231553386754188,
)
@interactions.option()
async def enemy(
    ctx: interactions.CommandContext, enemy: str
):  # whats the point of spells 1 FRICK WE HAVE NO CANTRIPS nvm

    for monster in possible_enemies:
        if (
            monster["name"].lower() == enemy.lower()
        ):  # bad not work  lmaooooooooooooooooooooooo but I hat writing
            name = monster["name"]
            meta = monster["meta"]
            armor_class = monster["Armor Class"]
            hit_points = monster["Hit Points"]
            speed = monster["Speed"]
            challenge = monster["Challenge"]
            traits = monster.get("Traits", "No Traits")
            actions = monster.get("Actions", "No Actions")
            legendary_actions = monster.get("Legendary Actions", "No Legendary Actions")
            img_url = monster["img_url"]

            embed = interactions.Embed(
                title=f"{name} ({meta})",
                description=f"**Traits:**\n> {replace_html_tags(traits) or 'No traits lol'}\n\n**Actions:**\n> {replace_html_tags(actions)}",
            )  # move traits and actions to description for more space
            embed.set_thumbnail(url=img_url)
            embed.add_field(name="AC", value=armor_class, inline=True)
            embed.add_field(name="HP", value=hit_points, inline=True)
            embed.add_field(name="Speed", value=speed, inline=True)
            embed.add_field(name="Challenge", value=challenge, inline=True)
            embed.add_field(
                name="Legendary Actions",
                value=replace_html_tags(legendary_actions),
                inline=False,
            )
            embed.add_field(name="Skills", value=monster["Skills"], inline=True)
            embed.add_field(name="Languages", value=monster["Languages"], inline=True)
            embed.add_field(name="Senses", value=monster["Senses"], inline=True)
            embed.add_field(name="Challenge", value=challenge, inline=True)
            
            await ctx.send(embeds=[embed])  # only send if we find a match
            return
    await ctx.send(f":warning: No enemy found with that name {enemy} :frog:")

@bot.command(
    name="enemy_from_race",
    description="Spawns a new enemy of that race",
    scope=1030231553386754188,
)
@interactions.option()
@interactions.option()
async def create_enemy(ctx: interactions.CommandContext, enemy_race: str, initiative: int):
    alive_combatants.append(
        enemy := Enemy.from_existing(enemy_race, initiative)
    )
    sort_combatants()
    await ctx.send(f"Spawned new {enemy.name} ({enemy_race})")

@bot.command(
    name="initiative",
    description="Roll Initiative!",
    scope=1030231553386754188,
)
@interactions.option()
@interactions.option()
async def roll_initiative(ctx: interactions.CommandContext, bonus: int = 0, override: int = None):
    alive_combatants.append(
        Player(ctx.author, roll := (roll_dice(f"1d20 + {bonus}" if override is None else override)[0]))
    )
    sort_combatants()
    await ctx.send(f"You rolled a {roll}!")

@bot.command(
    name="list_combatants",
    description="Lists all combatants",
    scope=1030231553386754188,
)
async def list_combatants(ctx: interactions.CommandContext):
    PLAYER_FMT = "{initiative}: {name}"
    ENEMY_FMT = "{initiative}: {name} ({race}) {fuzzy_health}"
    if not alive_combatants:
        await ctx.send("No combatants!")
        return
    await ctx.send("\n".join([PLAYER_FMT.format(**combatant.__dict__) if isinstance(combatant, Player) else ENEMY_FMT.format(**combatant.__dict__ | {"fuzzy_health": combatant.fuzzy_health}) for combatant in alive_combatants]))


@bot.command(
    name="spell",
    description="returns an spell's stats",
    scope=1030231553386754188,
)
@interactions.option()
async def spell(ctx: interactions.CommandContext, spell_name: str):
    try:
        spell = spells_by_name[spell_name.lower()]  # bot off I think
    except KeyError:
        await ctx.send(
            f":warning: No spell found with that name {spell_name} :man_mage:"
        )
        return  # this stops the function from continuing, like break in a loop :thumbsu

    name = spell_name.title()
    casting_time = spell["casting_time"]
    components = spell["components"]["raw"]
    description = split_text(spell["description"])
    duration = spell["duration"]
    level = spell["level"]
    range = spell["range"]
    school = spell["school"].title()

    embed = interactions.Embed(
        title=f"{name} (Level {level} {school})", description=description
    )  # this is still fine lmao
    embed.add_field(name="Casting Time", value=casting_time, inline=True)
    embed.add_field(name="Components", value=components, inline=True)
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="Range", value=range, inline=True)
    embed.add_field(name="School", value=school, inline=True)
    await ctx.send(embeds=[embed])


bot.start()
