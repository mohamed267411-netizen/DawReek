import hashlib
import os
import re
import random
from datetime import datetime, timedelta
import customtkinter as ctk
from PIL import Image, ImageChops, ImageDraw

import state

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def crop_image(img):
    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)
    return img

def load_image_safe(path, size=(120, 120), rounded=True):
    cache_key = (path, size, rounded)
    if cache_key in state.IMAGE_CACHE:
        return state.IMAGE_CACHE[cache_key]

    try:
        if not os.path.exists(path):
            return None
        img = Image.open(path).convert("RGBA")
        img = crop_image(img)
        img = img.resize(size)
        if rounded:
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), 16, fill=255)
            img.putalpha(mask)
        ctk_image = ctk.CTkImage(img, size=size)
        state.IMAGE_CACHE[cache_key] = ctk_image
        return ctk_image
    except Exception:
        return None

def get_team_logo_map():
    if state.TEAM_LOGO_CACHE is not None:
        return state.TEAM_LOGO_CACHE
    try:
        state.my_cursor.execute("SELECT teamname, teamLogo FROM Teams")
        state.TEAM_LOGO_CACHE = {row[0]: row[1] for row in state.my_cursor.fetchall()}
    except Exception:
        state.TEAM_LOGO_CACHE = {}
    return state.TEAM_LOGO_CACHE

def get_team_names():
    try:
        state.my_cursor.execute("SELECT teamname FROM Teams ORDER BY teamname")
        return [row[0] for row in state.my_cursor.fetchall()]
    except Exception:
        return ["Arsenal", "Chelsea", "Liverpool", "Manchester City", "Manchester United", "Tottenham Hotspur"]

def get_analysis_images():
    analysis_dir = os.path.join(os.path.dirname(__file__), "imag", "analysis")
    images_by_season = {}

    if not os.path.isdir(analysis_dir):
        return images_by_season

    for filename in sorted(os.listdir(analysis_dir)):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        match = re.search(r"_(\d{2})(?=\.)", filename)
        season = f"20{match.group(1)}" if match else "All"
        images_by_season.setdefault(season, []).append(os.path.join(analysis_dir, filename))

    return images_by_season

def load_analysis_image(path, max_size=(300, 410)):
    cache_key = ("analysis", path, max_size)
    if cache_key in state.IMAGE_CACHE:
        return state.IMAGE_CACHE[cache_key]

    try:
        img = Image.open(path).convert("RGBA")
        img.thumbnail(max_size)
        ctk_image = ctk.CTkImage(img, size=img.size)
        state.IMAGE_CACHE[cache_key] = ctk_image
        return ctk_image
    except Exception:
        return None

def get_model_prediction():
    if state.model_get_prediction is not None:
        return state.model_get_prediction

    try:
        from Module import get_prediction
        state.model_get_prediction = get_prediction
        state.MODEL_IMPORT_ERROR = None
        return state.model_get_prediction
    except Exception as exc:
        state.MODEL_IMPORT_ERROR = exc
        raise RuntimeError(f"Model is not ready: {exc}")

def ensure_2025_fixtures():
    return state.generated_fixtures

def get_2025_week_matches(week):
    fixtures = ensure_2025_fixtures()
    if 1 <= week <= len(fixtures):
        return fixtures[week - 1]
    return []

def get_team_rating(team, season=2025):
    cache_key = (team, season)
    if cache_key in state.TEAM_RATING_CACHE:
        return state.TEAM_RATING_CACHE[cache_key]

    try:
        query = """
        SELECT TOP 1 sr.fifa_rating
        FROM Season_Rating sr
        JOIN Teams t ON sr.teamID = t.teamID
        WHERE t.teamname = ? AND sr.season_year <= ?
        ORDER BY sr.season_year DESC
        """
        state.my_cursor.execute(query, (team, season))
        row = state.my_cursor.fetchone()
        if row and row[0] is not None:
            state.TEAM_RATING_CACHE[cache_key] = float(row[0])
            return state.TEAM_RATING_CACHE[cache_key]
    except Exception:
        pass
    state.TEAM_RATING_CACHE[cache_key] = 75.0
    return state.TEAM_RATING_CACHE[cache_key]

def get_historical_team_defaults(team):
    if team in state.TEAM_DEFAULTS_CACHE:
        return state.TEAM_DEFAULTS_CACHE[team]

    try:
        query = """
        SELECT TOP 5 GoalsFor, GoalsAgainst
        FROM (
            SELECT MatchID, hometeamID AS TeamID, home_goals AS GoalsFor, away_goals AS GoalsAgainst
            FROM Matches
            UNION ALL
            SELECT MatchID, awayteamID AS TeamID, away_goals AS GoalsFor, home_goals AS GoalsAgainst
            FROM Matches
        ) tm
        JOIN Teams t ON tm.TeamID = t.teamID
        WHERE t.teamname = ?
        ORDER BY MatchID DESC
        """
        state.my_cursor.execute(query, (team,))
        rows = state.my_cursor.fetchall()
        if rows:
            points = []
            goals = []
            for gf, ga in rows:
                goals.append(float(gf or 0))
                if (gf or 0) > (ga or 0):
                    points.append(3)
                elif (gf or 0) == (ga or 0):
                    points.append(1)
                else:
                    points.append(0)
            state.TEAM_DEFAULTS_CACHE[team] = (sum(points), sum(goals) / len(goals))
            return state.TEAM_DEFAULTS_CACHE[team]
    except Exception:
        pass
    state.TEAM_DEFAULTS_CACHE[team] = (0.0, 1.0)
    return state.TEAM_DEFAULTS_CACHE[team]

def get_simulated_team_stats(team, before_week):
    points = []
    goals_for = []

    for week in sorted(state.simulated_2025_results):
        if week >= before_week:
            continue
        for match in state.simulated_2025_results[week]:
            if match["home"] == team:
                gf = match["home_goals"]
                ga = match["away_goals"]
            elif match["away"] == team:
                gf = match["away_goals"]
                ga = match["home_goals"]
            else:
                continue

            goals_for.append(gf)
            if gf > ga:
                points.append(3)
            elif gf == ga:
                points.append(1)
            else:
                points.append(0)

    if not points:
        return get_historical_team_defaults(team)

    return sum(points[-5:]), sum(goals_for) / len(goals_for)

def build_2025_model_features(match, week):
    home = match["home"]
    away = match["away"]
    h_form, h_goals_avg = get_simulated_team_stats(home, week)
    a_form, a_goals_avg = get_simulated_team_stats(away, week)

    return {
        "home": home,
        "away": away,
        "h_fifa": get_team_rating(home),
        "a_fifa": get_team_rating(away),
        "h_form": h_form,
        "a_form": a_form,
        "h_goals_avg": h_goals_avg,
        "a_goals_avg": a_goals_avg
    }

def simulate_2025_week(week):
    if week in state.simulated_2025_results:
        return state.simulated_2025_results[week]

    predictor = get_model_prediction()
    week_matches = get_2025_week_matches(week)
    results = []

    for match in week_matches:
        features = build_2025_model_features(match, week)
        home_goals, away_goals, home_prob, draw_prob, away_prob = predictor(
            features["home"], features["away"],
            features["h_fifa"], features["a_fifa"],
            features["h_form"], features["a_form"],
            features["h_goals_avg"], features["a_goals_avg"]
        )

        results.append({
            "home": features["home"],
            "away": features["away"],
            "datetime": match.get("datetime"),
            "home_goals": int(home_goals),
            "away_goals": int(away_goals),
            "home_prob": home_prob,
            "draw_prob": draw_prob,
            "away_prob": away_prob
        })

    state.simulated_2025_results[week] = results
    return results

def get_2025_matches_for_display(week):
    if week in state.simulated_2025_results:
        return state.simulated_2025_results[week]

    return [
        {
            "home": match["home"],
            "away": match["away"],
            "datetime": match.get("datetime"),
            "home_goals": None,
            "away_goals": None,
            "home_prob": None,
            "draw_prob": None,
            "away_prob": None
        }
        for match in get_2025_week_matches(week)
    ]

def get_2025_standings():
    teams = {}
    logo_map = get_team_logo_map()

    for week in ensure_2025_fixtures():
        for match in week:
            for team in (match["home"], match["away"]):
                teams.setdefault(team, {
                    "team": team, "logo": logo_map.get(team), "P": 0,
                    "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0,
                    "GD": 0, "Pts": 0
                })

    for results in state.simulated_2025_results.values():
        for match in results:
            home = teams[match["home"]]
            away = teams[match["away"]]
            hg = match["home_goals"]
            ag = match["away_goals"]

            home["P"] += 1
            away["P"] += 1
            home["GF"] += hg
            home["GA"] += ag
            away["GF"] += ag
            away["GA"] += hg

            if hg > ag:
                home["W"] += 1
                away["L"] += 1
                home["Pts"] += 3
            elif hg < ag:
                away["W"] += 1
                home["L"] += 1
                away["Pts"] += 3
            else:
                home["D"] += 1
                away["D"] += 1
                home["Pts"] += 1
                away["Pts"] += 1

    rows = []
    for data in teams.values():
        data["GD"] = data["GF"] - data["GA"]
        rows.append((
            data["team"], data["logo"], data["P"], data["W"], data["D"],
            data["L"], data["GD"], data["Pts"]
        ))
    return rows

def generate_fixtures_with_time():
    state.simulated_2025_results.clear()

    state.my_cursor.execute("SELECT teamname FROM Teams")
    teams = [row[0] for row in state.my_cursor.fetchall()]

    random.shuffle(teams)

    def round_robin(t):
        real_teams = list(t)
        num_real_teams = len(real_teams)
        team_to_idx = {team: idx for idx, team in enumerate(real_teams)}

        if len(t) % 2 != 0:
            t.append("BYE")

        n = len(t)
        rounds = n - 1
        half = n // 2
        schedule = []

        for r in range(rounds):
            pairs = []
            for i in range(half):
                t1 = t[i]
                t2 = t[n - 1 - i]

                if t1 != "BYE" and t2 != "BYE":
                    idx1 = team_to_idx[t1]
                    idx2 = team_to_idx[t2]
                    
                    if (idx1 - idx2) % num_real_teams <= num_real_teams // 2:
                        home, away = t1, t2
                    else:
                        home, away = t2, t1

                    pairs.append((home, away))

            schedule.append(pairs)
            t = [t[0]] + [t[-1]] + t[1:-1]

        return schedule

    fixtures = round_robin(teams)
    start_date = datetime(2025, 8, 1, 18, 0)  

    state.generated_fixtures = []

    for week_index, matches in enumerate(fixtures):
        week_matches = []
        for match_index, (home, away) in enumerate(matches):
            match_time = start_date + timedelta(days=week_index * 7, hours=match_index * 2)
            week_matches.append({
                "home": home,
                "away": away,
                "datetime": match_time
            })
        state.generated_fixtures.append(week_matches)

    return state.generated_fixtures
