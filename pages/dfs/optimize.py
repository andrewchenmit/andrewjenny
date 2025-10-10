import itertools
import os.path
import pandas as pd
import pickle
import sys
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1UvSzPssXakkMip5nHDd2E4IwHPcLy1n_0aZicBl4BdE'
RANGE = 'Week 6!A4:M'

def main():

    # Initialize variables
    start_time = time.perf_counter()
    POSITIONS = ['QB', 'RB', 'WR', 'TE', 'DEF']
    MIN_POINT_THRESHOLD = 5
    MIN_EFF_THRESHOLD = {'QB': 0.4, 'RB': 0.4, 'WR': 0.4, 'TE': 0.4, 'DEF': 0.4}
    #MIN_EFF_THRESHOLD = {'QB': 0.7, 'RB': 0.55, 'WR': 0.45, 'TE': 0.55, 'DEF': 0.62}
    MAX_TIER_THRESHOLD = {'QB': 99, 'RB': 8, 'WR': 9, 'TE': 8, 'DEF': 99}
    players = []
    incomplete_num = 0
    low_num = 0
    eff_num = 0
    tier_num = 0
    creds = None
    point_index = 9
    eff_index = 10
    if len(sys.argv) > 1:
        point_source = sys.argv[1:]
        if point_source == 'vegas':
            point_index = 13
            eff_index = 14

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
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
    data = result.get('values', [])

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"--------------------------------------------")
    print(f"Data access time: {elapsed_time:.6f} seconds")
    print(f"--------------------------------------------")


    # Format for data frame & prune players that will never be selected
    start_time = time.perf_counter()
    print("Start:",len(data))
    for row in data:
        if len(row)<7:
            incomplete_num+=1
            continue
        if float(row[point_index])<MIN_POINT_THRESHOLD:
            low_num+=1
            continue
        if float(row[eff_index])<MIN_EFF_THRESHOLD[row[2]]:
            eff_num+=1
            continue
        if int(row[8])>MAX_TIER_THRESHOLD[row[2]]:
            tier_num+=1
            continue
        players.append((row[2],row[1],int(row[3]),float(row[point_index])))

    print("Incomplete:",incomplete_num)
    print("Too Low:",low_num)
    print("Inefficient:",eff_num)
    print("Bad Tier:",tier_num)
    print("Players:",len(players))

    df = pd.DataFrame(players, columns=["Pos","Name","Salary","Points"])

    print(df)

    # Split by position
    qbs = df[df.Pos=="QB"].to_dict("records")
    rbs = df[df.Pos=="RB"].to_dict("records")
    wrs = df[df.Pos=="WR"].to_dict("records")
    tes = df[df.Pos=="TE"].to_dict("records")
    defs = df[df.Pos=="DEF"].to_dict("records")
    everybody = df.to_dict("records")

    print("QB count:",len(qbs))
    print("RB count:",len(rbs))
    print("WR count:",len(wrs))
    print("TE count:",len(tes))
    print("DEF count:",len(defs))
    print("Total count:",len(qbs)+len(rbs)+len(wrs)+len(tes)+len(defs))

    qbs_pruned = qbs.copy()
    for p in itertools.combinations(qbs, 2):
        if p[0]['Points'] < p[1]['Points'] and p[0]['Salary'] >= p[1]['Salary']:
            try:
                qbs_pruned.remove(p[0])
                print("Removed:",p[0],"worse than",p[1])
            except:
                pass
        if p[0]['Points'] > p[1]['Points'] and p[0]['Salary'] <= p[1]['Salary']:
            try:
                qbs_pruned.remove(p[1])
                print("Removed:",p[1],"worse than",p[0])
            except:
                pass

    tes_pruned = tes.copy()
    for p in itertools.combinations(tes, 2):
        if p[0]['Points'] < p[1]['Points'] and p[0]['Salary'] >= p[1]['Salary']:
            try:
                tes_pruned.remove(p[0])
                print("Removed:",p[0],"worse than",p[1])
            except:
                pass
        if p[0]['Points'] > p[1]['Points'] and p[0]['Salary'] <= p[1]['Salary']:
            try:
                tes_pruned.remove(p[1])
                print("Removed:",p[1],"worse than",p[0])
            except:
                pass

    defs_pruned = defs.copy()
    for p in itertools.combinations(defs, 2):
        if p[0]['Points'] < p[1]['Points'] and p[0]['Salary'] >= p[1]['Salary']:
            try:
                defs_pruned.remove(p[0])
                print("Removed:",p[0],"worse than",p[1])
            except:
                pass
        if p[0]['Points'] > p[1]['Points'] and p[0]['Salary'] <= p[1]['Salary']:
            try:
                defs_pruned.remove(p[1])
                print("Removed:",p[1],"worse than",p[0])
            except:
                pass

    rbs_pruned = rbs.copy()
    for p in itertools.combinations(rbs, 2):
        if p[0]['Points'] < p[1]['Points'] and p[0]['Salary'] >= p[1]['Salary']:
            try:
                rbs_pruned.remove(p[0])
                print("Removed:",p[0],"worse than",p[1])
            except:
                pass
        if p[0]['Points'] > p[1]['Points'] and p[0]['Salary'] <= p[1]['Salary']:
            try:
                rbs_pruned.remove(p[1])
                print("Removed:",p[1],"worse than",p[0])
            except:
                pass

    wrs_pruned = wrs.copy()
    for p in itertools.combinations(wrs, 2):
        if p[0]['Points'] < p[1]['Points'] and p[0]['Salary'] >= p[1]['Salary']:
            try:
                wrs_pruned.remove(p[0])
                print("Removed:",p[0],"worse than",p[1])
            except:
                pass
        if p[0]['Points'] > p[1]['Points'] and p[0]['Salary'] <= p[1]['Salary']:
            try:
                wrs_pruned.remove(p[1])
                print("Removed:",p[1],"worse than",p[0])
            except:
                pass

    wr_min = 9999
    for p in itertools.combinations(wrs, 3):
        salaries = sum(w["Salary"] for w in p)
        if salaries < wr_min:
            wr_min = salaries
    print("Minimum 3WR Salary:",wr_min)

    rb_min = 9999
    for p in itertools.combinations(rbs, 2):
        salaries = sum(w["Salary"] for w in p)
        if salaries < rb_min:
            rb_min = salaries
    print("Minimum 2RB Salary:",rb_min)

    print(qbs_pruned)
    print(rbs_pruned)
    print(wrs_pruned)
    print(tes_pruned)
    print(defs_pruned)
    print("QB count:",len(qbs_pruned),"vs.",len(qbs))
    print("RB count:",len(rbs_pruned),"vs.",len(rbs))
    print("WR count:",len(wrs_pruned),"vs.",len(wrs))
    print("TE count:",len(tes_pruned),"vs.",len(tes))
    print("DEF count:",len(defs_pruned),"vs.",len(defs))
    print("Total count:",len(qbs_pruned)+len(rbs_pruned)+len(wrs_pruned)+len(tes_pruned)+len(defs_pruned))

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"--------------------------------------------")
    print(f"Pruning time: {elapsed_time:.6f} seconds")
    print(f"--------------------------------------------")

    # Pre-compute
    #start_time = time.perf_counter()

    #wrs_combos = {}
    #for wrs_combo in itertools.combinations(wrs_pruned, 3):
    #    wrs_combos[wrs_combo[0]['Name']+wrs_combo[1]['Name']] = {'Salary': sum(p["Salary"] for p in wrs_combo), 'Points': sum(p["Points"] for p in wrs_combo)}

    #end_time = time.perf_counter()
    #elapsed_time = end_time - start_time
    #print(f"--------------------------------------------")
    #print(f"Precompute time: {elapsed_time:.6f} seconds")
    #print(f"--------------------------------------------")

    # Optimization
    start_time_2 = time.perf_counter()
    cap = 200
    best = {"points":0,"salary":0,"lineup":None}
    count = 0
    total = len(qbs_pruned)*len(tes_pruned)*len(defs_pruned)
    for qb in qbs_pruned:
        print(qb)
        for te in tes_pruned:
            print(te)
            for defense in defs_pruned:
                start_time = time.perf_counter()
                count+=1

                base_salary = qb["Salary"] + te["Salary"] + defense["Salary"]
                base_points = qb["Points"] + te["Points"] + defense["Points"]
                if base_salary > cap-10-rb_min-wr_min:
                    print("Skipping",base_salary,qp,te,defense)
                    continue

                for rb in rbs_pruned:
                    rbs_left = rbs.copy()
                    try:
                        rbs_left.remove(rb)
                    except:
                        pass
                    for rb2 in rbs_left:
                        rb_salary = rb["Salary"] + rb2["Salary"]
                        rb_points = rb["Points"] + rb2["Points"]
                        if base_salary + rb_salary > cap-10-wr_min:
                            continue

                        for wr in wrs_pruned:
                            wrs_left = wrs.copy()
                            try:
                                wrs_left.remove(wr)
                            except:
                                pass
                            for wrs_combo in itertools.combinations(wrs_left, 2):
                                wr_salary = wr["Salary"] + sum(p["Salary"] for p in wrs_combo)
                                wr_points = wr["Points"] + sum(p["Points"] for p in wrs_combo)
                                subtotal_salary = base_salary + rb_salary + wr_salary
                                subtotal_points = base_points + rb_points + wr_points
                                if subtotal_salary > cap-10:
                                    continue

                                # Flex: choose any RB, WR, or TE not already used
                                used = {qb["Name"], te["Name"], defense["Name"], rb["Name"], rb2["Name"], wr["Name"], *[w["Name"] for w in wrs_combo]}
                                flex_pool = [p for p in everybody if p["Pos"] in ("RB","WR","TE") and p["Name"] not in used]
                                for flex in flex_pool:
                                    total_salary = subtotal_salary + flex["Salary"]
                                    if total_salary > cap:
                                        continue
                                    total_points = subtotal_points + flex["Points"]
                                    if total_points > best["points"] or (total_points == best["points"] and total_salary < best["salary"]):
                                        best = {
                                            "points": total_points,
                                            "salary": total_salary,
                                            "lineup": [qb, rb, rb2, wr, wrs_combo[0], wrs_combo[1], te, flex, defense]
                                            #"lineup": {"QB": qb, "RB1": rb, "RB2": rb2, "WR1": wr, "WR2": wrs_combo[0], "WR3": wrs_combo[1],"TE": te, "DEF": defense, "Flex": flex}
                                        }
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                print(f"--------------------------------------------")
                print(count,"/",total,"cycles |",round(count/total*100,1),"% complete")
                print(f"Cycle time: {elapsed_time:.6f} seconds")
                print(f"Elapsed time: {(time.perf_counter()-start_time_2)/60:.1f} minutes")
                print(f"ETA: {elapsed_time*(total-count)/60:.1f} minutes")
                print(f"--------------------------------------------")

    end_time_2 = time.perf_counter()
    elapsed_time_2 = end_time_2 - start_time_2
    print(f"--------------------------------------------")
    print(f"Optimization time: {elapsed_time_2/60:.1f} minutes")
    print(f"--------------------------------------------")
    print("Points:",best['points'])
    print("Salary:",best['salary'])
    best_df = pd.DataFrame(best['lineup'], columns=["Pos","Name","Salary","Points"])
    print(best_df)

if __name__ == '__main__':
    main()
