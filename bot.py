import json
from random import randint
from typing import Literal
from rolldice import roll_dice
from dice import roll_min, roll_max
from random import randint
import interactions, dotenv, os, re
from battle_sim import Enemy, Player
from oztils import remove

dotenv.load_dotenv()

player_stats = {
    "Furiouspotato": {
        "health": 16,
        "armor_class": 13,
    },
    "Ultrablob": {
        "health": 15,
        "armor_class": 15,
    },
    "ozzy": {
        "health": 14,
        "armor_class": 14,
    },
}

bot = interactions.Client(token=os.getenv("BOT_TOKEN"))

possible_enemies = json.load(open("enemies.json", "r"))
spells = json.load(open("spells.1.json", "r"))

spells_by_name = {}
# process spells
for spell in spells:
    spells_by_name[spell["name"].lower()] = spell

combatants = []


def where(list, condition):
    for item in list:
        if condition(item):
            return item
    return None


dice_emoji = {
    "d4-1": "<:d4_1:1090768265984344134>",
    "d4-2": "<:d4_2:1090768297026388050>",
    "d4-3": "<:d4_3:1090768262985429102>",
    "d4-4": "<:d4_4:1090768261949440091>",
    "d6-1": "<:d6_1:1090768260879876267>",
    "d6-2": "<:d6_2:1090768259478982737>",
    "d6-3": "<:d6_3:1090768258031943751>",
    "d6-4": "<:d6_4:1090768257511870534>",
    "d6-5": "<:d6_5:1090768255850913893>",
    "d6-6": "<:d6_6:1090768254802341908>",
    "d8-1": "<:d8_1:1090768820077084813>",
    "d8-2": "<:d8_2:1090768818990764192>",
    "d8-3": "<:d8_3:1090768817346580500>",
    "d8-4": "<:d8_4:1090768816167985162>",
    "d8-5": "<:d8_5:1090768815211692073>",
    "d8-6": "<:d8_6:1090768810849603605>",
    "d8-7": "<:d8_7:1090768810295955456>",
    "d8-8": "<:d8_8:1090768808370782220>",
    "d10-1": "<:d10_1:1090768737197641728>",
    "d10-2": "<:d10_2:1090768688308822087>",
    "d10-3": "<:d10_3:1090768686870184067>",
    "d10-4": "<:d10_4:1090768685473476628>",
    "d10-5": "<:d10_5:1090768684315844678>",
    "d10-6": "<:d10_6:1090768682604568677>",
    "d10-7": "<:d10_7:1090768681191088258>",
    "d10-8": "<:d10_8:1090768679899250768>",
    "d10-9": "<:d10_9:1090768678750007306>",
    "d10-10": "<:d10_10:1090768677110038641>",
    "d12-1": "<:d12_1:1091092004190044233>",
    "d12-2": "<:d12_2:1091092002889805965>",
    "d12-3": "<:d12_3:1091092001732165653>",
    "d12-4": "<:d12_4:1091092000016711700>",
    "d12-5": "<:d12_5:1090768909147324436>",
    "d12-6": "<:d12_6:1090768907901616238>",
    "d12-7": "<:d12_7:1090768907012411474>",
    "d12-8": "<:d12_8:1090768905343086774>",
    "d12-9": "<:d12_9:1090768904151912479>",
    "d12-10": "<:d12_10:1090768902910390373>",
    "d12-11": "<:d12_11:1090768901626925056>",
    "d12-12": "<:d12_12:1090768900171517982>",
    "d20-1": "<:d20_1:1090778219554279494>",
    "d20-2": "<:d20_2:1090778250244010024>",
    "d20-3": "<:d20_3:1090778217444548708>",
    "d20-4": "<:d20_4:1090778216479862804>",
    "d20-5": "<:d20_5:1090778215078969355>",
    "d20-6": "<:d20_6:1090778213506101328>",
    "d20-7": "<:d20_7:1090778212369444915>",
    "d20-8": "<:d20_8:1090778211429908480>",
    "d20-9": "<:d20_9:1090778210385534997>",
    "d20-10": "<:d20_10:1090778208317755464>",
    "d20-11": "<:d20_11:1090778335795216465>",
    "d20-12": "<:d20_12:1090778333849071668>",
    "d20-13": "<:d20_13:1090778332443967518>",
    "d20-14": "<:d20_14:1090778331303137342>",
    "d20-15": "<:d20_15:1090778330011283546>",
    "d20-16": "<:d20_16:1090778327687630918>",
    "d20-17": "<:d20_17:1090778326215430225>",
    "d20-18": "<:d20_18:1090778324424470649>",
    "d20-19": "<:d20_19:1090778322688028672>",
    "d20-20": "<:d20_20:1090778319223533738>",
}

def autocomplete_from_list(ls):
    async def autocomplete(ctx: interactions.CommandContext, value: str = ""):
        await ctx.populate(
            [
                interactions.Choice(name=item, value=item)
                for item in ls
                if value.lower() in item.lower() or value == ""
            ][:25] # only 25 options are allowed in the autocomplete
        )
    return autocomplete

@bot.command(
    name="ping",
    description="Check Latency",
    scope=1030231553386754188,
)
@interactions.option()
async def ping(ctx: interactions.CommandContext, response: str = "Pong!"):
    await ctx.send(response)


@bot.command(
    name="restart",
    description="Restart the bot",
    scope=1030231553386754188,
)
async def restart(ctx: interactions.CommandContext):
    await ctx.send("Restarting...")
    os.system("python3 bot.py")
    quit()


def format_explanation(dice_notation: str, explanation: str):
    dice_type = re.findall(r"d\d+", dice_notation)[0]
    return remove(
        re.sub(
            r"(?<=[\[\],])\d+",
            lambda match: dice_emoji.get(
                f"{dice_type}-{match.group(0)}", match.group(0)
            )
            or match.group(0),
            explanation,
        ),
        "[,]",
    )


@bot.command(
    name="roll",
    description="Rolls a number of dice",
    scope=1030231553386754188,
)
@interactions.option()
@interactions.option(
    name="advantage",
    description="Roll with advantage or disadvantage",
    choices=[
        interactions.Choice(name="None", value="None"),
        interactions.Choice(name="Advantage", value="Advantage"),
        interactions.Choice(name="Disadvantage", value="Disadvantage"),
    ],
)
async def roll(
    ctx: interactions.CommandContext,
    dice_notation: str,
    advantage: str = "None",
):
    min_roll, max_roll = int(roll_min(dice_notation)), int(roll_max(dice_notation))
    if advantage != "None":
        (smaller_total, smaller_explanation), (
            larger_total,
            larger_explanation,
        ) = sorted(
            [roll_dice(dice_notation), roll_dice(dice_notation)],
            reverse=advantage == "Disadvantage",
        )
        await ctx.send(
            f"""
:game_die: {dice_notation} (With {advantage}) = **{larger_total}**
~~{format_explanation(dice_notation, smaller_explanation)} = {smaller_total}~~
{format_explanation(dice_notation, larger_explanation)} = {larger_total}
        """.strip()
        )
    else:
        total, explanation = roll_dice(dice_notation)
        await ctx.send(
            f":game_die: {dice_notation} ({1 / (max_roll - min_roll):.3%} chance of any specific outcome)\n{format_explanation(dice_notation, explanation)} = {total}"
        )


def replace_html_tags(string):
    return (
        string.replace("<em>", "")
        .replace("</em>", "")
        .replace("<strong>", "**")
        .replace("</strong>", "**")
        .replace("<p>", "")
        .replace("</p>", "")
        .replace(".**", ".")
        .replace(".,", ".")
    )  # still some errors and weird characters


def split_text(text):
    sentences = re.split(
        r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!) ", text
    )  # what is this regex
    chunks = [sentences[i : i + 3] for i in range(0, len(sentences), 3)]

    new_text = "\n\n".join([" ".join(chunk) for chunk in chunks])

    return new_text


def sort_combatants():
    combatants.sort(key=lambda combatant: combatant.initiative, reverse=True)


@bot.command(
    name="stats",
    description="returns an enemies stats",
    scope=1030231553386754188,
)
@interactions.option(
    name="enemy",
    description="The enemy you want to see the stats of",
    type=interactions.OptionType.STRING,
    required=True,
    autocomplete=True,  # i hate my life
)
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
                color=0x36393F,
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
            embed.add_field(
                name="Senses", value=replace_html_tags(monster["Senses"]), inline=True
            )
            embed.add_field(name="Challenge", value=challenge, inline=True)

            await ctx.send(embeds=[embed])  # only send if we find a match
            return
    await ctx.send(f":warning: No enemy found with that name {enemy} :frog:")

@bot.command(
    name="eval",
    description="Evaluates a python expression (for debugging)",
    scope=1030231553386754188,
)
@interactions.option()
async def eval_(ctx: interactions.CommandContext, expression: str):
    await ctx.send(eval(expression))


@bot.command(
    name="enemy_from_race",
    description="Spawns a new enemy of that race",
    scope=1030231553386754188,
)
@interactions.option()
@interactions.option()
async def create_enemy(
    ctx: interactions.CommandContext, enemy_race: str, initiative: int
):
    combatants.append(enemy := Enemy.from_existing(enemy_race, initiative))
    sort_combatants()
    await ctx.send(f"Spawned new {enemy.name} ({enemy_race})")


@bot.command(
    name="initiative",
    description="Roll Initiative!",
    scope=1030231553386754188,
)
@interactions.option()
@interactions.option()
async def roll_initiative(
    ctx: interactions.CommandContext, bonus: int = 0, override: int = None
):
    if ctx.author.name not in player_stats:
        await ctx.send(
            ":warning: You haven't set your stats yet! (ping ultrablob to do so)"
        )
        return
    if ctx.author.name in [combatant.name for combatant in combatants]:
        await ctx.send(":warning: You already rolled initiative!")
        return

    combatants.append(
        Player(
            ctx.author,
            initiative=(
                roll := roll_dice(f"1d20 + {bonus}" if override is None else override)[
                    0
                ]
            ),
            armor_class=player_stats[ctx.author.name]["armor_class"],
            health=player_stats[ctx.author.name]["health"],
        )
    )
    sort_combatants()
    await ctx.send(f"You rolled a {roll}!")


@bot.command(
    name="end_combat",
    description="Ends combat",
    scope=1030231553386754188,
)
async def end_combat(ctx: interactions.CommandContext):
    combatants.clear()
    await ctx.send("Combat has ended!")


@bot.command(
    name="list_combatants",
    description="Lists all combatants",
    scope=1030231553386754188,
)
async def list_combatants(
    ctx: interactions.CommandContext,
):  # where does the initiative come from??????
    PLAYER_FMT = "{initiative:02} | {name} ({health} HP)"
    ENEMY_FMT = "{initiative:02} | {race} ({name}) {fuzzy_health}"
    if not combatants:
        await ctx.send(":warning: No combatants!")
        return
    await ctx.send(
        embeds=[
            interactions.Embed(
                title="Combatants",
                color=0x36393F,
                description="\n".join(
                    [
                        PLAYER_FMT.format(**combatant.__dict__)
                        if isinstance(combatant, Player)
                        else ENEMY_FMT.format(
                            **combatant.__dict__
                            | {"fuzzy_health": combatant.fuzzy_health}
                        )
                        for combatant in combatants
                    ]
                ),
            )
        ]
    )


@bot.command(
    name="damage",
    description="Try to damage an enemy",
    scope=1030231553386754188,
)
@interactions.option(
    name="target_name",
    description="The name of the target",
    type=interactions.OptionType.STRING,
    required=True,
    autocomplete=True,  # i hate my life
)
@interactions.option()
@interactions.option()
async def damage(
    ctx: interactions.CommandContext, target_name: str, attack: int, damage: int
):
    target = where(
        combatants, lambda combatant: combatant.name.lower() == target_name.lower()
    )  # I'm trying to make it pick a target from the list of available enemies, rather than typing in the name of the enemy
    if not target:
        await ctx.send(
            f":warning: No combatant with that name {target_name} :frog:"
        )  # for some reason copilot really likes the frog emoji wait wha
        return  # I mean using the choices dropdown box # oh ok
    if attack < target.armor_class:
        await ctx.send(f"{target.name} dodged the attack!")
        return
    combatants[0].health -= damage
    if combatants[0].health <= 0:
        await ctx.send(f"{target.name} died!")
        return
    await ctx.send(f"{target.name} took {damage} damage!")


@bot.autocomplete("damage", "target_name")  # trying to figure this out from docs rn
async def damage_target_autocomplete(
    ctx: interactions.CommandContext, target_name: str = ""
):  # watching video on this lmao
    await ctx.populate(
        [
            interactions.Choice(name=combatant.name, value=combatant.name)
            for combatant in combatants
            if combatant.health > 0
        ]  # this is terrible
    )  # go to battle_sim.py oh my god what the heck


@bot.command(
    name="spell",
    description="returns an spell's stats",
    scope=1030231553386754188,
)
@interactions.option(
    name="spell_name",
    description="The name of the spell",
    type=interactions.OptionType.STRING,
    required=True,
    autocomplete=True,
)
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
        title=f"{name} (Level {level} {school})",
        description=description,
        color=0x36393F,
    )  # this is still fine lmao
    embed.add_field(name="Casting Time", value=casting_time, inline=True)
    embed.add_field(name="Components", value=components, inline=True)
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="Range", value=range, inline=True)
    embed.add_field(name="School", value=school, inline=True)
    await ctx.send(embeds=[embed])



@bot.command(
    name="equipment",
    description="returns an items value, stats, and traits",
    scope=1030231553386754188,
)
@interactions.option()
async def equipment(ctx: interactions.CommandContext, item_name: str):
    pass


@bot.command(
    name="class",
    description="returns dnd classes (and maybe subclasses/archetypes)",
    scope=1030231553386754188,
)
@interactions.option()
async def spell(ctx: interactions.CommandContext, item_name: str):
    pass

bot.autocomplete("stats", "enemy")(autocomplete_from_list([enemy["name"] for enemy in possible_enemies])) # have to define autocomplete after commands
bot.autocomplete("spell", "spell_name")(autocomplete_from_list(list(spells_by_name.keys())))

bot.start()
