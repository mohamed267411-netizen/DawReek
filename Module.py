import pandas as pd
import pyodbc
import numpy as np 
from sklearn.linear_model import PoissonRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error,r2_score,mean_absolute_error
from sklearn.model_selection import train_test_split ,GridSearchCV
from scipy.stats import poisson

def get_data():
    server = r'DESKTOP-FGR06IV\SQLEXPRESS' 
    database = 'footballDB'
    conn_str = (
        f'DRIVER={{SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection=yes;'
    )
    conn = pyodbc.connect(conn_str)
    
    query = """
    SELECT 
        MF.*, 
        M.home_goals, 
        M.away_goals,
        T1.teamname AS HomeTeamName,
        T2.teamname AS AwayTeamName
    FROM Match_Features MF
    JOIN Matches M ON MF.MatchID = M.MatchID
    JOIN Teams T1 ON M.hometeamID = T1.teamID
    JOIN Teams T2 ON M.awayteamID = T2.teamID
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df


df = get_data()
# print(df.columns)

y_home = df['home_goals'] 
y_away = df['away_goals']  



numerical_features = [
    'home_form', 'away_form', 'form_diff', 
    'home_goals_avg', 'away_goals_avg', 'goals_diff', 
    'home_fifa', 'away_fifa', 'rating_diff'
]

X_final = df[numerical_features]

X_train, X_test, y_h_train, y_h_test, y_a_train, y_a_test = train_test_split(
    X_final, y_home, y_away, test_size=0.2, random_state=42
)


scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

X_train_scaled[numerical_features] = scaler.fit_transform(X_train[numerical_features])
X_test_scaled[numerical_features] = scaler.transform(X_test[numerical_features])

X_train = X_train_scaled
X_test = X_test_scaled

param_grid = {'alpha': [0.1, 0.05, 0.01, 0.005, 0.001]}
grid = GridSearchCV(PoissonRegressor(), param_grid, cv=5)
grid.fit(X_train, y_h_train)

print(f"Best alpha found: {grid.best_params_['alpha']}")
model_poisson_home = PoissonRegressor(alpha=grid.best_params_['alpha'], max_iter=300)
model_poisson_away = PoissonRegressor(alpha=grid.best_params_['alpha'], max_iter=300)


model_poisson_home.fit(X_train, y_h_train)
model_poisson_away.fit(X_train, y_a_train)


h_preds = model_poisson_home.predict(X_test)
a_preds = model_poisson_away.predict(X_test)


def match_outcome_probabilities(home_lambda, away_lambda, max_goals=10):
    
    home_probs = [poisson.pmf(i, home_lambda) for i in range(max_goals + 1)]
    away_probs = [poisson.pmf(i, away_lambda) for i in range(max_goals + 1)]

    home_win = 0
    draw = 0
    away_win = 0

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = home_probs[h] * away_probs[a]

            if h > a:
                home_win += prob
            elif h == a:
                draw += prob
            else:
                away_win += prob

    return home_win, draw, away_win

def most_likely_score(home_lambda, away_lambda, max_goals=10):
    best_prob = 0
    best_score = (0, 0)

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):

            prob = poisson.pmf(h, home_lambda) * poisson.pmf(a, away_lambda)

            if prob > best_prob:
                best_prob = prob
                best_score = (h, a)

    return best_score
def get_prediction(home_team, away_team, h_fifa, a_fifa, h_form, a_form, h_goals_avg, a_goals_avg):
    numeric_input = pd.DataFrame([[
        h_form, a_form, h_form - a_form,
        h_goals_avg, a_goals_avg, h_goals_avg - a_goals_avg,
        h_fifa, a_fifa, h_fifa - a_fifa
    ]], columns=numerical_features)

    full_input = scaler.transform(numeric_input)

    pred_h = model_poisson_home.predict(full_input)[0]
    pred_a = model_poisson_away.predict(full_input)[0]

    home_win, draw, away_win = match_outcome_probabilities(pred_h, pred_a)
    home_goals, away_goals = most_likely_score(pred_h*1.4, pred_a*1.1)
    return home_goals, away_goals, home_win, draw, away_win

def get_prediction_matrix(home_team, away_team, h_fifa, a_fifa, h_form, a_form, h_goals_avg, a_goals_avg, max_goals=4):
    numeric_input = pd.DataFrame([[
        h_form, a_form, h_form - a_form,
        h_goals_avg, a_goals_avg, h_goals_avg - a_goals_avg,
        h_fifa, a_fifa, h_fifa - a_fifa
    ]], columns=numerical_features)

    full_input = scaler.transform(numeric_input)

    pred_h = model_poisson_home.predict(full_input)[0]
    pred_a = model_poisson_away.predict(full_input)[0]

    home_lambda = pred_h * 1.4
    away_lambda = pred_a * 1.1

    matrix = []
    for h in range(max_goals + 1):
        row = []
        for a in range(max_goals + 1):
            prob = poisson.pmf(h, home_lambda) * poisson.pmf(a, away_lambda)
            row.append(prob)
        matrix.append(row)
    return matrix

def predict_round(matches_list, verbose=False):
    results = []
    
    for match in matches_list:
        ph, pa, hw, dr, aw = get_prediction(
            match['home'], match['away'], 
            match['h_fifa'], match['a_fifa'], 
            match['h_form'], match['a_form'], 
            match['h_goals_avg'], match['a_goals_avg']
        )
        
        results.append({
            'Match': f"{match['home']} vs {match['away']}",
            'Score': f"{ph}-{pa}",
            'HomeProb': f"{hw*100:.1f}%",
            'DrawProb': f"{dr*100:.1f}%",
            'AwayProb': f"{aw*100:.1f}%"
        })
        
        if verbose:
            print(f"{match['home']:<15} vs {match['away']:<15} | {ph}-{pa:<5} | {hw*100:>6.1f}% | {dr*100:>6.1f}% | {aw*100:>6.1f}%")
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    print(f"Poisson Home Goals MAE: {mean_absolute_error(y_h_test, h_preds):.4f}")
    print(f"Poisson Away Goals MAE: {mean_absolute_error(y_a_test, a_preds):.4f}")

    next_round = [
        {
            'home': 'Liverpool', 'away': 'Arsenal',
            'h_fifa': 92, 'a_fifa': 82, 'h_form': 2.5, 'a_form': 2.0,
            'h_goals_avg': 3.0, 'a_goals_avg': 1.5
        },
        {
            'home': 'Chelsea', 'away': 'Tottenham',
            'h_fifa': 90, 'a_fifa': 85, 'h_form': 2.8, 'a_form': 1.2,
            'h_goals_avg': 2.5, 'a_goals_avg': 1.0
        }
    ]

    round_df = predict_round(next_round, verbose=True)



