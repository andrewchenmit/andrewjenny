import itertools
import os.path
import pandas as pd
import pickle
import pulp
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1UvSzPssXakkMip5nHDd2E4IwHPcLy1n_0aZicBl4BdE'
RANGE = 'Week 6!A4:O'

def solve_fantasy_knapsack(desc, data, salary_cap, roster_spots, min_point, min_eff, max_tier, projection):
    # Format for data frame & prune players that will never be selected
    #print("Start:",len(data))
    point_index = 9
    eff_index = 10
    if projection == 'vegas':
        point_index = 13
        eff_index = 14
    players_raw = []
    low_num = 0
    incomplete_num = 0
    eff_num = 0
    tier_num = 0
    for row in data:
        print(row)
        if len(row)<eff_index+1:
            incomplete_num+=1
            continue
        if row[point_index]=='':
            incomplete_num+=1
            continue
        if float(row[point_index])<min_point:
            low_num+=1
            continue
        if float(row[eff_index])<min_eff[row[2]]:
            eff_num+=1
            continue
        if int(row[8])>max_tier[row[2]]:
            tier_num+=1
            continue
        players_raw.append((row[2],row[1],int(row[3]),float(row[point_index])))

    #print("Incomplete:",incomplete_num)
    #print("Too Low:",low_num)
    #print("Inefficient:",eff_num)
    #print("Bad Tier:",tier_num)
    #print("Players:",len(players_raw))
    #print(f"--------------------------------------------")

    df = pd.DataFrame(players_raw, columns=["position","name","salary","points"])

    #print(df)

    players = df.to_dict("records")

    """
    Solves the fantasy football lineup optimization problem using PuLP.
    """
    # Create the LP problem object
    prob = pulp.LpProblem("FantasyFootballLineup", pulp.LpMaximize)

    # Create decision variables for each player, indicating if they are selected (1) or not (0)
    player_vars = pulp.LpVariable.dicts("Player", [player['name'] for player in players], 0, 1, pulp.LpBinary)

    # Objective: Maximize total projected points
    prob += pulp.lpSum([player_vars[player['name']] * player['points'] for player in players]), "Total_Points"

    # Constraint 1: Stay under the salary cap
    prob += pulp.lpSum([player_vars[player['name']] * player['salary'] for player in players]) <= salary_cap, "Salary_Cap"

    # Constraint 2: Fill roster spots by position
    all_positions = set(p['position'] for p in players)
    for pos, num_players in roster_spots.items():
        if pos == 'QB':
            prob += pulp.lpSum([player_vars[p['name']] for p in players if p['position'] == pos]) == num_players, f"Roster_{pos}"
        if pos == 'RB':
            prob += pulp.lpSum([player_vars[p['name']] for p in players if p['position'] == pos]) <= num_players+1, f"Roster_{pos}"
        if pos == 'WR':
            prob += pulp.lpSum([player_vars[p['name']] for p in players if p['position'] == pos]) <= num_players+1, f"Roster_{pos}"
            prob += pulp.lpSum([player_vars[p['name']] for p in players if p['position'] == pos]) >= num_players, f"Roster_{pos}_2"
        if pos == 'TE':
            prob += pulp.lpSum([player_vars[p['name']] for p in players if p['position'] == pos]) <= num_players+1, f"Roster_{pos}"
        if pos == 'DEF':
            prob += pulp.lpSum([player_vars[p['name']] for p in players if p['position'] == pos]) == num_players, f"Roster_{pos}"

    # Constraint 3: Handle the FLEX position
    # The number of FLEX players can be fulfilled by RBs, WRs, or TEs
    prob += pulp.lpSum([
        player_vars[p['name']] for p in players if p['position'] in ['RB', 'WR', 'TE']
    ]) == roster_spots['RB'] + roster_spots['WR'] + roster_spots['TE'] + roster_spots['FLEX'], "FLEX_Roster"

    # Solve the problem
    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    # Output the results
    if pulp.LpStatus[prob.status] == 'Optimal':
        reply = {}
        answer = []
        lineup = {'QB':[],'RB':[],'WR':[],'TE':[],'DEF':[]}
        total_salary = 0
        total_points = 0
        for player in players:
            if player_vars[player['name']].varValue == 1:
                lineup[player['position']].append((player['position'],player['name'],player['salary'],player['points']))
                total_salary += player['salary']
                total_points += player['points']

        answer.append(lineup['QB'][0])
        answer.append(lineup['RB'][0])
        answer.append(lineup['RB'][1])
        answer.append(lineup['WR'][0])
        answer.append(lineup['WR'][1])
        answer.append(lineup['WR'][2])
        answer.append(lineup['TE'][0])
        if len(lineup['RB'])>2:
            answer.append(lineup['RB'][2])
        elif len(lineup['WR'])>3:
            answer.append(lineup['WR'][3])
        else:
            answer.append(lineup['TE'][1])
        answer.append(lineup['DEF'][0])

        print("ANSWER")
        print(answer)
        reply['description'] = desc
        reply['lineup'] = answer
        reply['points'] = round(total_points,1)
        reply['salary'] = total_salary
        return reply

def knapsack():

    # Initialize variables
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        try:
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        except:
            pass

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
    data = result.get('values', [])

    # Run the solver
    salary_cap = 200
    roster_spots = {
        'QB': 1,
        'RB': 2,
        'WR': 3,
        'TE': 1,
        'FLEX': 1,  # Can be RB, WR, or TE
        'DEF': 1,
    }

    print("RUNNING")
    solution = {'lineups': []}
    solution['lineups'].append(solve_fantasy_knapsack('Unconstrained Vegas', data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 99, 'RB': 99, 'WR': 99, 'TE': 99, 'DEF': 99}, 'vegas'))
    solution['lineups'].append(solve_fantasy_knapsack('Unconstrained FP', data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 99, 'RB': 99, 'WR': 99, 'TE': 99, 'DEF': 99}, 'fp'))
    solution['lineups'].append(solve_fantasy_knapsack('RB/WR/TE Max 8 FP', data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 99, 'RB': 8, 'WR': 8, 'TE': 8, 'DEF': 99}, 'fp'))
    solution['lineups'].append(solve_fantasy_knapsack('QB/RB/WR/TE Max 8 FP', data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 8, 'RB': 8, 'WR': 8, 'TE': 8, 'DEF': 99}, 'fp'))
    solution['lineups'].append(solve_fantasy_knapsack('RB/WR/TE Max 7 FP', data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 99, 'RB': 7, 'WR': 7, 'TE': 7, 'DEF': 99}, 'fp'))
    print(solution)
    print("RETURNING")
    return solution

    #solve_fantasy_knapsack(data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 99, 'RB': 8, 'WR': 8, 'TE': 8, 'DEF': 99}, 'fp')
    #solve_fantasy_knapsack(data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 8, 'RB': 8, 'WR': 8, 'TE': 8, 'DEF': 99}, 'fp')
    #solve_fantasy_knapsack(data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 7, 'RB': 7, 'WR': 7, 'TE': 7, 'DEF': 99}, 'fp')
    #solve_fantasy_knapsack(data, salary_cap, roster_spots, 3, {'QB': 0.3, 'RB': 0.3, 'WR': 0.3, 'TE': 0.3, 'DEF': 0.3}, {'QB': 6, 'RB': 6, 'WR': 6, 'TE': 6, 'DEF': 99}, 'fp')
