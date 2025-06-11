# dashboard/dashboard_texts.py
# Stores configuration for UI elements like custom messages and titles.

import random

# --- Hall of Shame (PvP Leaderboard) ---
HALL_OF_SHAME_CONFIG = {
    "sackillu22": "{player} has been sat {deaths} times for a total of {value} gp!",
    "Au Joel": None,
    "Doug Lee": None
}

DEFAULT_SHAME_MESSAGES = [
    "{player} is a liability, dying {deaths} times and losing {value} gp.",
    "{player} is donating gear to the wilderness, losing {value} gp over {deaths} deaths.",
    "Someone get {player} a teleport tab. They've lost {value} gp in {deaths} deaths.",
    "The clan's official piranha is {player}, feeding {value} gp to the wildy in {deaths} deaths."
]

def get_shame_message(player, deaths, value):
    message_template = HALL_OF_SHAME_CONFIG.get(player) or random.choice(DEFAULT_SHAME_MESSAGES)
    return message_template.format(player=player, deaths=deaths, value=value)


# --- 111 Kicks Page ---
TOP_KICKED_MESSAGES = [
    "The clan's favourite bootie is {player}, kicked {count} times.",
    "{player} has seen the login screen {count} times this period.",
]

FASTEST_FINGER_MESSAGES = [
    "The admin with the happiest trigger finger is {player}, kicking {count} people.",
    "{player} is laying down the law, with {count} kicks delivered.",
]

# --- Stolen Whips Page ---
WHIP_QUEEN = "Abby Queen"
WHIP_SHAME_MESSAGE = "{queen} has rightfully earned {queen_count} whips. The clan owes her {total_stolen} whips! Shame on {top_thief} for being the top thieving rat."


# --- Biggest Yappers Page ---
TOP_YAPPER_MESSAGES = ["The clan's biggest menace is {player}, spamming '111' {count} times."]
TOP_GZER_MESSAGES = ["The most supportive member is {player}, with {count} GZs."]


# --- Personal Bests Page ---
SWEATIEST_PLAYERS_MESSAGES = [
    "{player} has {count} records—someone hose them down, they're sweating through the leaderboard!",
    "{player} spent more time Ruby Bolt resetting than sleeping. {count} records say it paid off… kinda.",
]

# --- Recent Achievements Page ---
HIGH_HITTER_MESSAGES = ["o/ {player} has joined the ranks of the High Hitters on {date}."]
MAXED_SKILL_MESSAGES = ["On {date}, {player} finally maxed {skill}! No more training for them."]
COMBAT_TASK_MESSAGES = ["A new PvM legend is born! {player} completed the {tier} task '{task}' on {date}."]
DIARY_MESSAGES = ["On {date}, {player} finished the {tier} {diary} diary. Nice!"]
CA_TIER_MESSAGES = ["Big congrats to {player} for unlocking the {tier} tier of Combat Achievements on {date}!"]