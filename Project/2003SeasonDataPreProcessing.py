import os
import pandas as pd
import math
import datetime

pathForCoachesCareer = os.getcwd()
pathForCoachesCareer += "/Project/Datasets/coaches_career.txt"

pathForCoachesSeason = os.getcwd()
pathForCoachesSeason += "/Project/Datasets/coaches_season.txt"

coachesCareer = pd.read_csv(pathForCoachesCareer)
coachesSeason = pd.read_csv(pathForCoachesSeason)

# Coaching Data is only till 2003
# Will have to self calculate for upcoming seasonsbnh

coachesSeason2002 = coachesSeason.query("year == 2002")
coachesSeason2003 = coachesSeason.query("year == 2003")
coachesSeason2003Rating = coachesSeason2003[["coachid", "year", "firstname", "lastname", "team"]]
coachesSeason2002Rating = coachesSeason2002[["coachid", "year", "firstname", "lastname", "team"]]
coachesCareer2003 = coachesCareer.query('coachid in @coachesSeason2003["coachid"]')
coachesCareer2003["career_win_percentage"] = (coachesCareer2003["season_win"] + coachesCareer2003["playoff_win"]) / ( coachesCareer2003["season_win"] + coachesCareer2003["season_loss"] + coachesCareer2003["playoff_win"] + coachesCareer2003["playoff_loss"] ) 
coachesSeason2003Rating = coachesSeason2003Rating.merge(coachesCareer2003[["career_win_percentage","coachid"]])
coachesSeason2002Rating["past_season_win_percentage"] = coachesSeason2002["season_win"] / ( coachesSeason2002["season_win"] + coachesSeason2002["season_loss"] ) 
coachesSeason2002Rating["past_season_playoff_win_percentage"] = coachesSeason2002["playoff_win"] / ( coachesSeason2002["playoff_win"] + coachesSeason2002["playoff_loss"] ) 
coachesSeason2003Rating = coachesSeason2003Rating.merge(coachesSeason2002Rating[["coachid","past_season_win_percentage","past_season_playoff_win_percentage"]], how="left")



# Coach Rating Calculation:
# 30% coach career performance
# 70% past season rating
# Past season rating:
# 10% made it to playoffs or not
# 10% Was a coach in the past season
# 80% pastSeason Wins Rating 
coachesSeason2003Rating["past_season_rating"] = 0.1 * (pd.notna(coachesSeason2003Rating["past_season_playoff_win_percentage"])) + 0.1 * ( pd.notna(coachesSeason2003Rating["past_season_win_percentage"])) + 0.8 * ( (coachesSeason2003Rating["past_season_win_percentage"] + 0.5) / (coachesSeason2003Rating["past_season_win_percentage"] + 1) )
coachesSeason2003Rating["past_season_rating"].loc[pd.isna(coachesSeason2003Rating["past_season_rating"])] = 0.1 * (pd.notna(coachesSeason2003Rating["past_season_playoff_win_percentage"])) + 0.1 * ( pd.notna(coachesSeason2003Rating["past_season_win_percentage"])) + 0.8 * 0.5
coachesSeason2003Rating["Rating"] = 0.3 * coachesSeason2003Rating["career_win_percentage"] + 0.7 * coachesSeason2003Rating["past_season_rating"] 

coachesSeason2003Rating = coachesSeason2003Rating[["coachid", "year", "firstname", "lastname", "team", "Rating"]]

#Team Ratings from Player data
pathForPlayerSeasonData = os.getcwd();
pathForPlayerSeasonData += "/Project/Datasets/player_regular_season.txt"
playerSeason = pd.read_csv(pathForPlayerSeasonData)
playerSeason2002 = playerSeason.query("year == 2002")
playerSeason2002.groupby("ilkid").sum()
playerSeason2002["fg_success_rate"] = playerSeason2002["fgm"] / ( playerSeason2002["fga"] )
playerSeason2002["ft_success_rate"] = playerSeason2002["ftm"] / ( playerSeason2002["fta"] )
playerSeason2002["tp_success_rate"] = playerSeason2002["tpm"] / ( playerSeason2002["tpa"] )



playerPreviousSeason2003Stats = playerSeason.query("year == 2003")
playerPreviousSeason2003Stats = playerPreviousSeason2003Stats[["ilkid", "year", "firstname", "lastname", "team"]]
playerPreviousSeason2003Stats = playerPreviousSeason2003Stats.merge(playerSeason2002[["ilkid", "minutes", "pts", "oreb", "dreb", "reb", "asts", "stl", "blk", "turnover", "pf", "fga",  "fgm",  "fta",  "ftm",  "tpa",  "tpm",  "fg_success_rate",  "ft_success_rate",  "tp_success_rate"]], how="left", on="ilkid")

# Taking Top 8 players from each team to calculate team stats (idea from NBA2K23)
playerPreviousSeason2003Stats = playerPreviousSeason2003Stats.groupby('team').apply(lambda x: x.nlargest(8, 'minutes', keep='all').sum())

#Cleaning Data
playerPreviousSeason2003Stats = playerPreviousSeason2003Stats[[ 'team', "pts", "oreb", "dreb", "reb", "asts", "stl", "blk", "turnover", "pf", "fga",  "fgm",  "fta",  "ftm",  "tpa",  "tpm"]]
for i in range (playerPreviousSeason2003Stats.shape[0]):
    playerPreviousSeason2003Stats['team'][i] = playerPreviousSeason2003Stats['team'][i][0:3]

playerPreviousSeason2003Stats["fg_success_rate"] = playerPreviousSeason2003Stats["fgm"] / ( playerPreviousSeason2003Stats["fga"] )
playerPreviousSeason2003Stats["ft_success_rate"] = playerPreviousSeason2003Stats["ftm"] / ( playerPreviousSeason2003Stats["fta"] )
playerPreviousSeason2003Stats["tp_success_rate"] = playerPreviousSeason2003Stats["tpm"] / ( playerPreviousSeason2003Stats["tpa"] )
playerPreviousSeason2003Stats = playerPreviousSeason2003Stats.add_prefix("p_")


#Team Ratings from Team data
pathForTeamSeasonData = os.getcwd();
pathForTeamSeasonData += "/Project/Datasets/team_season.txt"
teamSeason = pd.read_csv(pathForTeamSeasonData)
teamSeason2002 = teamSeason.query("year == 2002")
teamPastSeason2003 = teamSeason2002.add_prefix('t_')
teamPastSeason2003Data = teamSeason2002.loc[:, ~teamSeason2002.columns.str.startswith('d_')]




#Combining all three aspects (coach, player, and team data)
teamData2003 = teamPastSeason2003[['t_team']]
teamData2003["team"] = teamPastSeason2003[['t_team']]
teamData2003 = teamData2003[["team"]]
teamData2003 = teamData2003.merge(playerPreviousSeason2003Stats,left_on="team", right_on="p_team")
# , "p_pts", "p_oreb", "p_dreb", "p_reb", "p_asts", "p_stl", "p_blk", "p_turnover", "p_pf", "p_fga",  "p_fgm",  "p_fta",  "p_ftm",  "p_tpa",  "p_tpm"]], how="left")
teamData2003 = teamData2003.drop("p_team", axis=1)
teamData2003 = teamData2003.merge(teamPastSeason2003,left_on="team", right_on="t_team")
teamData2003 = teamData2003.merge(coachesSeason2003Rating[["team","Rating"]],left_on="team", right_on="team")
teamData2003["c_rating"] = teamData2003["Rating"]
teamData2003 = teamData2003.drop("Rating", axis=1)









#Building Main Dataframe for Games
path = os.getcwd()
path += "/Project/Datasets/games.csv"
games = pd.read_csv(path)

filt_games_2003 = (games['SEASON']==2003)
games_2003_stats = games[filt_games_2003]
games_2003_stats = games_2003_stats.replace('Bucks','MIL')
games_2003_stats = games_2003_stats.replace('Suns','PHX')
games_2003_stats = games_2003_stats.replace( 'Hawks','ATL')
games_2003_stats = games_2003_stats.replace( 'Clippers','LAC')
games_2003_stats = games_2003_stats.replace( '76ers','PHI')
games_2003_stats = games_2003_stats.replace( 'Nets','BKN')
games_2003_stats = games_2003_stats.replace( 'Jazz','UTA')
games_2003_stats = games_2003_stats.replace( 'Nuggets','DEN')
games_2003_stats = games_2003_stats.replace( 'Mavericks','DAL')
games_2003_stats = games_2003_stats.replace( 'Trail Blazers','POR')
games_2003_stats = games_2003_stats.replace( 'Lakers','LAL')
games_2003_stats = games_2003_stats.replace( 'Knicks','NYK')
games_2003_stats = games_2003_stats.replace( 'Wizards','WAS')
games_2003_stats = games_2003_stats.replace( 'Grizzlies','MEM')
games_2003_stats = games_2003_stats.replace( 'Celtics','BOS')
games_2003_stats = games_2003_stats.replace( 'Warriors','GSW')
games_2003_stats = games_2003_stats.replace( 'Heat','MIA')
games_2003_stats = games_2003_stats.replace( 'Pacers','IND')
games_2003_stats = games_2003_stats.replace( 'Raptors','TOR')
games_2003_stats = games_2003_stats.replace( 'Spurs','SAS')
games_2003_stats = games_2003_stats.replace( 'Pistons','DET')
games_2003_stats = games_2003_stats.replace( 'Bulls','CHI')
games_2003_stats = games_2003_stats.replace( 'Timberwolves','MIN')
games_2003_stats = games_2003_stats.replace( 'Pelicans','SAS')
games_2003_stats = games_2003_stats.replace( 'Pistons','DET')
games_2003_stats = games_2003_stats.replace( 'Bulls','CHI')
games_2003_stats = games_2003_stats.replace( 'Thunder','OKC')
games_2003_stats = games_2003_stats.replace( 'Kings','SAC')
games_2003_stats = games_2003_stats.replace( 'Rockets','HOU')
games_2003_stats = games_2003_stats.replace( 'Hornets','CHA')
games_2003_stats = games_2003_stats.replace( 'Cavaliers','CLE')
games_2003_stats = games_2003_stats.replace( 'Magic','ORL')

#2003 Data
# Rest
games_2003_stats["GAMES_IN_5_DAYS_HOME"] = 0
games_2003_stats["GAMES_IN_5_DAYS_VISITOR"] = 0

#Recent Performance
games_2003_stats["AVG_POINTS_IN_10_DAYS_VISITOR"] = 0
games_2003_stats["AVG_POINTS_IN_10_DAYS_HOME"] = 0
games_2003_stats["AVG_FGP_IN_10_DAYS_VISITOR"] = 0
games_2003_stats["AVG_FGP_IN_10_DAYS_HOME"] = 0
games_2003_stats["AVG_FG3P_IN_10_DAYS_VISITOR"] = 0
games_2003_stats["AVG_FG3P_IN_10_DAYS_HOME"] = 0
games_2003_stats["AVG_FTP_IN_10_DAYS_VISITOR"] = 0
games_2003_stats["AVG_FTP_IN_10_DAYS_HOME"] = 0
games_2003_stats["AVG_AST_IN_10_DAYS_VISITOR"] = 0
games_2003_stats["AVG_AST_IN_10_DAYS_HOME"] = 0
games_2003_stats["AVG_REB_IN_10_DAYS_VISITOR"] = 0
games_2003_stats["AVG_REB_IN_10_DAYS_HOME"] = 0

#Overall Season Performance
games_2003_stats["AVG_POINTS_CURRENT_SEASON_VISITOR"] = 0
games_2003_stats["AVG_POINTS_CURRENT_SEASON_HOME"] = 0
games_2003_stats["AVG_FGP_CURRENT_SEASON_VISITOR"] = 0
games_2003_stats["AVG_FGP_CURRENT_SEASON_HOME"] = 0
games_2003_stats["AVG_FG3P_CURRENT_SEASON_VISITOR"] = 0
games_2003_stats["AVG_FG3P_CURRENT_SEASON_HOME"] = 0
games_2003_stats["AVG_FTP_CURRENT_SEASON_VISITOR"] = 0
games_2003_stats["AVG_FTP_CURRENT_SEASON_HOME"] = 0
games_2003_stats["AVG_AST_CURRENT_SEASON_VISITOR"] = 0
games_2003_stats["AVG_AST_CURRENT_SEASON_HOME"] = 0
games_2003_stats["AVG_REB_CURRENT_SEASON_VISITOR"] = 0
games_2003_stats["AVG_REB_CURRENT_SEASON_HOME"] = 0
games_2003_stats['GAME_DATE_EST'] = pd.to_datetime(games_2003_stats['GAME_DATE_EST'])  

for index, row in games_2003_stats.iterrows():
    d = datetime.timedelta(days = 5)
    d2 = datetime.timedelta(days = 10)
    gameDate = row["GAME_DATE_EST"]
    minDate = gameDate - d
    minDate2 = gameDate - d2
    minDate3 = games_2003_stats["GAME_DATE_EST"].min()
    mask = (games_2003_stats['GAME_DATE_EST'] > minDate) & (games_2003_stats['GAME_DATE_EST'] < gameDate)
    mask2 = (games_2003_stats['GAME_DATE_EST'] >= minDate2) & (games_2003_stats['GAME_DATE_EST'] < gameDate)
    mask3 = (games_2003_stats['GAME_DATE_EST'] >= minDate3) & (games_2003_stats['GAME_DATE_EST'] < gameDate)
    maskedGameStats = games_2003_stats.loc[mask]
    maskedGameStats2 = games_2003_stats.loc[mask2]
    maskedGameStats3 = games_2003_stats.loc[mask3]
    homeTeam = row["HOME_TEAM_ID"]
    visitorTeam = row["VISITOR_TEAM_ID"]
    homeTeamGameCount = len(maskedGameStats.query("HOME_TEAM_ID == @homeTeam | VISITOR_TEAM_ID == @homeTeam").index)
    visitorTeamGameCount = len(maskedGameStats.query("HOME_TEAM_ID == @visitorTeam | VISITOR_TEAM_ID == @visitorTeam").index)

    visitorTeamAveragePoints =  (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["PTS_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["PTS_away"].sum()) / (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["PTS_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["PTS_away"].count()) 
    if(pd.isna( visitorTeamAveragePoints)):
        visitorTeamAveragePoints = 93.4
    homeTeamAveragePoints =  (maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["PTS_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["PTS_away"].sum())/(maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["PTS_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["PTS_away"].count())
    if(pd.isna( homeTeamAveragePoints)):
        homeTeamAveragePoints = 93.4
    visitorTeamAverageFGP =  (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["FG_PCT_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["FG_PCT_away"].sum() ) / (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["FG_PCT_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["FG_PCT_away"].count()) 
    if(pd.isna( visitorTeamAverageFGP)):
        visitorTeamAverageFGP = 0.439
    homeTeamAverageFGP =  (maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["FG_PCT_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["FG_PCT_away"].sum())/(maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["FG_PCT_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["FG_PCT_away"].count())
    if(pd.isna( homeTeamAverageFGP)):
        homeTeamAverageFGP = 0.439
    visitorTeamAverageFG3P =  (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["FG3_PCT_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["FG3_PCT_away"].sum() ) / (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["FG3_PCT_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["FG3_PCT_away"].count()) 
    if(pd.isna( visitorTeamAverageFG3P)):
        visitorTeamAverageFG3P = 0.347
    homeTeamAverageFG3P =  (maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["FG3_PCT_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["FG3_PCT_away"].sum())/(maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["FG3_PCT_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["FG3_PCT_away"].count())
    if(pd.isna( homeTeamAverageFG3P)):
        homeTeamAverageFG3P = 0.347
    
    visitorTeamAverageFTP =  (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["FT_PCT_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["FT_PCT_away"].sum() ) / (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["FT_PCT_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["FT_PCT_away"].count()) 
    if(pd.isna( visitorTeamAverageFTP)):
        visitorTeamAverageFTP = 0.752
    homeTeamAverageFTP =  (maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["FT_PCT_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["FT_PCT_away"].sum())/(maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["FT_PCT_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["FT_PCT_away"].count())
    if(pd.isna( homeTeamAverageFTP)):
        homeTeamAverageFTP = 0.752

    visitorTeamAverageAST =  (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["AST_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["AST_away"].sum() ) / (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["AST_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["AST_away"].count()) 
    if(pd.isna( visitorTeamAverageAST)):
        visitorTeamAverageAST = 21.3
    homeTeamAverageAST =  (maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["AST_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["AST_away"].sum())/(maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["AST_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["AST_away"].count())
    if(pd.isna( homeTeamAverageAST)):
        homeTeamAverageAST = 21.3
    
    visitorTeamAverageREB =  (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["REB_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["REB_away"].sum() ) / (maskedGameStats2.query("HOME_TEAM_ID == @visitorTeam")["REB_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @visitorTeam")["REB_away"].count()) 
    if(pd.isna( visitorTeamAverageREB)):
        visitorTeamAverageREB = 42.2
    homeTeamAverageREB =  (maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["REB_home"].sum() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["REB_away"].sum())/(maskedGameStats2.query("HOME_TEAM_ID == @homeTeam")["REB_home"].count() + maskedGameStats2.query("VISITOR_TEAM_ID == @homeTeam")["REB_away"].count())
    if(pd.isna( homeTeamAverageREB)):
        homeTeamAverageREB = 42.2

    visitorTeamAveragePointsCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["PTS_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["PTS_away"].sum()) / (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["PTS_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["PTS_away"].count()) 
    if(pd.isna( visitorTeamAveragePoints)):
        visitorTeamAveragePoints = 93.4
    homeTeamAveragePointsCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["PTS_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["PTS_away"].sum())/(maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["PTS_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["PTS_away"].count())
    if(pd.isna( homeTeamAveragePoints)):
        homeTeamAveragePoints = 93.4
    visitorTeamAverageFGPCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["FG_PCT_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["FG_PCT_away"].sum() ) / (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["FG_PCT_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["FG_PCT_away"].count()) 
    if(pd.isna( visitorTeamAverageFGP)):
        visitorTeamAverageFGP = 0.439
    homeTeamAverageFGPCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["FG_PCT_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["FG_PCT_away"].sum())/(maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["FG_PCT_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["FG_PCT_away"].count())
    if(pd.isna( homeTeamAverageFGP)):
        homeTeamAverageFGP = 0.439
    visitorTeamAverageFG3PCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["FG3_PCT_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["FG3_PCT_away"].sum() ) / (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["FG3_PCT_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["FG3_PCT_away"].count()) 
    if(pd.isna( visitorTeamAverageFG3P)):
        visitorTeamAverageFG3P = 0.347
    homeTeamAverageFG3PCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["FG3_PCT_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["FG3_PCT_away"].sum())/(maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["FG3_PCT_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["FG3_PCT_away"].count())
    if(pd.isna( homeTeamAverageFG3P)):
        homeTeamAverageFG3P = 0.347
    
    visitorTeamAverageFTPCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["FT_PCT_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["FT_PCT_away"].sum() ) / (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["FT_PCT_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["FT_PCT_away"].count()) 
    if(pd.isna( visitorTeamAverageFTP)):
        visitorTeamAverageFTP = 0.752
    homeTeamAverageFTPCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["FT_PCT_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["FT_PCT_away"].sum())/(maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["FT_PCT_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["FT_PCT_away"].count())
    if(pd.isna( homeTeamAverageFTP)):
        homeTeamAverageFTP = 0.752

    visitorTeamAverageASTCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["AST_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["AST_away"].sum() ) / (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["AST_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["AST_away"].count()) 
    if(pd.isna( visitorTeamAverageAST)):
        visitorTeamAverageAST = 21.3
    homeTeamAverageASTCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["AST_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["AST_away"].sum())/(maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["AST_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["AST_away"].count())
    if(pd.isna( homeTeamAverageAST)):
        homeTeamAverageAST = 21.3
    
    visitorTeamAverageREBCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["REB_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["REB_away"].sum() ) / (maskedGameStats3.query("HOME_TEAM_ID == @visitorTeam")["REB_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @visitorTeam")["REB_away"].count()) 
    if(pd.isna( visitorTeamAverageREB)):
        visitorTeamAverageREB = 42.2
    homeTeamAverageREBCurrentSeason  =  (maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["REB_home"].sum() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["REB_away"].sum())/(maskedGameStats3.query("HOME_TEAM_ID == @homeTeam")["REB_home"].count() + maskedGameStats3.query("VISITOR_TEAM_ID == @homeTeam")["REB_away"].count())
    if(pd.isna( homeTeamAverageREB)):
        homeTeamAverageREB = 42.2

    games_2003_stats.at[index,"GAMES_IN_5_DAYS_HOME"] = homeTeamGameCount 
    games_2003_stats.at[index,"GAMES_IN_5_DAYS_VISITOR"] = visitorTeamGameCount 
    games_2003_stats.at[index,"AVG_POINTS_IN_10_DAYS_VISITOR"] = visitorTeamAveragePoints 
    games_2003_stats.at[index,"AVG_POINTS_IN_10_DAYS_HOME"] = homeTeamAveragePoints
    games_2003_stats.at[index,"AVG_FGP_IN_10_DAYS_VISITOR"] = visitorTeamAverageFGP
    games_2003_stats.at[index,"AVG_FGP_IN_10_DAYS_HOME"] = homeTeamAverageFGP
    games_2003_stats.at[index,"AVG_FG3P_IN_10_DAYS_VISITOR"] = visitorTeamAverageFG3P
    games_2003_stats.at[index,"AVG_FG3P_IN_10_DAYS_HOME"] = homeTeamAverageFG3P
    games_2003_stats.at[index,"AVG_FTP_IN_10_DAYS_VISITOR"] = visitorTeamAverageFTP
    games_2003_stats.at[index,"AVG_FTP_IN_10_DAYS_HOME"] = homeTeamAverageFTP
    games_2003_stats.at[index,"AVG_AST_IN_10_DAYS_VISITOR"] = visitorTeamAverageAST
    games_2003_stats.at[index,"AVG_AST_IN_10_DAYS_HOME"] = homeTeamAverageAST
    games_2003_stats.at[index,"AVG_REB_IN_10_DAYS_VISITOR"] = visitorTeamAverageREB
    games_2003_stats.at[index,"AVG_REB_IN_10_DAYS_HOME"] = homeTeamAverageREB

    games_2003_stats.at[index,"AVG_POINTS_CURRENT_SEASON_VISITOR"] = visitorTeamAveragePointsCurrentSeason 
    games_2003_stats.at[index,"AVG_POINTS_CURRENT_SEASON_HOME"] = homeTeamAveragePointsCurrentSeason 
    games_2003_stats.at[index,"AVG_FGP_CURRENT_SEASON_VISITOR"] = visitorTeamAverageFGPCurrentSeason 
    games_2003_stats.at[index,"AVG_FGP_CURRENT_SEASON_HOME"] = homeTeamAverageFGPCurrentSeason 
    games_2003_stats.at[index,"AVG_FG3P_CURRENT_SEASON_VISITOR"] = visitorTeamAverageFG3PCurrentSeason 
    games_2003_stats.at[index,"AVG_FG3P_CURRENT_SEASON_HOME"] = homeTeamAverageFG3PCurrentSeason 
    games_2003_stats.at[index,"AVG_FTP_CURRENT_SEASON_VISITOR"] = visitorTeamAverageFTPCurrentSeason 
    games_2003_stats.at[index,"AVG_FTP_CURRENT_SEASON_HOME"] = homeTeamAverageFTPCurrentSeason 
    games_2003_stats.at[index,"AVG_AST_CURRENT_SEASON_VISITOR"] = visitorTeamAverageASTCurrentSeason 
    games_2003_stats.at[index,"AVG_AST_CURRENT_SEASON_HOME"] = homeTeamAverageASTCurrentSeason 
    games_2003_stats.at[index,"AVG_REB_CURRENT_SEASON_VISITOR"] = visitorTeamAverageREBCurrentSeason 
    games_2003_stats.at[index,"AVG_REB_CURRENT_SEASON_HOME"] = homeTeamAverageREBCurrentSeason 

games_2003_stats = games_2003_stats.merge(coachesSeason2003Rating[["team","Rating"]], how="left", left_on="HOME_TEAM_ID", right_on="team")
games_2003_stats = games_2003_stats.merge(coachesSeason2003Rating[["team","Rating"]], how="left", left_on="VISITOR_TEAM_ID", right_on="team", suffixes=("_home_coach","_visitor_coach"))

games_2003_stats = games_2003_stats.merge(playerPreviousSeason2003Stats, how="left", left_on="HOME_TEAM_ID", right_on="team")
games_2003_stats = games_2003_stats.merge(playerPreviousSeason2003Stats, how="left", left_on="VISITOR_TEAM_ID", right_on="team", suffixes=("_past_season_player_home","_past_season_player_visitor"))

games_2003_stats = games_2003_stats.merge(teamPastSeason2003Data[["team", "o_fgm",  "o_fga",  "o_ftm",  "o_fta",  "o_oreb",  "o_dreb",  "o_reb",  "o_asts",  "o_pf",  "o_stl",  "o_to",  "o_blk", "o_3pm",  "o_3pa",  "o_pts", "pace",  "won",  "lost"]], how="left", left_on="HOME_TEAM_ID", right_on="team")
games_2003_stats = games_2003_stats.merge(teamPastSeason2003Data[["team", "o_fgm",  "o_fga",  "o_ftm",  "o_fta",  "o_oreb",  "o_dreb",  "o_reb",  "o_asts",  "o_pf",  "o_stl",  "o_to",  "o_blk", "o_3pm",  "o_3pa",  "o_pts", "pace",  "won",  "lost"]], how="left", left_on="VISITOR_TEAM_ID", right_on="team", suffixes=("_past_season_team_home","_past_season_team_visitor"))

coachingData  = ["Rating_home_coach", "Rating_visitor_coach"]

restData = ["GAMES_IN_5_DAYS_HOME", "GAMES_IN_5_DAYS_VISITOR"]

pastSeasonTeamPerformance = ["o_fgm_past_season_team_home",  "o_fga_past_season_team_home",  "o_ftm_past_season_team_home",  "o_fta_past_season_team_home",  "o_oreb_past_season_team_home",  "o_dreb_past_season_team_home",  "o_reb_past_season_team_home",  "o_asts_past_season_team_home",  "o_pf_past_season_team_home",  "o_stl_past_season_team_home",  "o_to_past_season_team_home",  "o_blk_past_season_team_home", "o_3pm_past_season_team_home",  "o_3pa_past_season_team_home",  "o_pts_past_season_team_home", "pace_past_season_team_home",  "won_past_season_team_home",  "lost_past_season_team_home",
  "o_fgm_past_season_team_visitor",  "o_fga_past_season_team_visitor",  "o_ftm_past_season_team_visitor",  "o_fta_past_season_team_visitor",  "o_oreb_past_season_team_visitor",  "o_dreb_past_season_team_visitor",  "o_reb_past_season_team_visitor",  "o_asts_past_season_team_visitor",  "o_pf_past_season_team_visitor",  "o_stl_past_season_team_visitor",  "o_to_past_season_team_visitor",  "o_blk_past_season_team_visitor", "o_3pm_past_season_team_visitor",  "o_3pa_past_season_team_visitor",  "o_pts_past_season_team_visitor", "pace_past_season_team_visitor",  "won_past_season_team_visitor",  "lost_past_season_team_visitor",
  ]

pastSeasonTop8PlayersPerformance = ["p_pts_past_season_player_home", "p_oreb_past_season_player_home", "p_dreb_past_season_player_home", "p_reb_past_season_player_home", "p_asts_past_season_player_home", "p_stl_past_season_player_home", "p_blk_past_season_player_home", "p_turnover_past_season_player_home",
  "p_pf_past_season_player_home", "p_fga_past_season_player_home",  "p_fgm_past_season_player_home",  "p_fta_past_season_player_home",  "p_ftm_past_season_player_home",  "p_tpa_past_season_player_home",  "p_tpm_past_season_player_home",
  "p_pts_past_season_player_visitor", "p_oreb_past_season_player_visitor", "p_dreb_past_season_player_visitor", "p_reb_past_season_player_visitor", "p_asts_past_season_player_visitor", 
  "p_stl_past_season_player_visitor", "p_blk_past_season_player_visitor", "p_turnover_past_season_player_visitor", "p_pf_past_season_player_visitor", "p_fga_past_season_player_visitor",  
  "p_fgm_past_season_player_visitor",  "p_fta_past_season_player_visitor",  "p_ftm_past_season_player_visitor",  "p_tpa_past_season_player_visitor",  "p_tpm_past_season_player_visitor"]

currentSeasonAverageStatsForPast10Days = ["AVG_POINTS_IN_10_DAYS_VISITOR", "AVG_POINTS_IN_10_DAYS_HOME", "AVG_FGP_IN_10_DAYS_VISITOR", "AVG_FGP_IN_10_DAYS_HOME","AVG_FG3P_IN_10_DAYS_VISITOR", "AVG_FG3P_IN_10_DAYS_HOME", "AVG_FTP_IN_10_DAYS_VISITOR", "AVG_FTP_IN_10_DAYS_HOME", "AVG_AST_IN_10_DAYS_VISITOR", "AVG_AST_IN_10_DAYS_HOME", "AVG_REB_IN_10_DAYS_VISITOR", "AVG_REB_IN_10_DAYS_HOME"]

currentSeasonAverageStatsOverall = ["AVG_POINTS_CURRENT_SEASON_VISITOR", "AVG_POINTS_CURRENT_SEASON_HOME", "AVG_FGP_CURRENT_SEASON_VISITOR", "AVG_FGP_CURRENT_SEASON_HOME","AVG_FG3P_CURRENT_SEASON_VISITOR", "AVG_FG3P_CURRENT_SEASON_HOME", "AVG_FTP_CURRENT_SEASON_VISITOR", "AVG_FTP_CURRENT_SEASON_HOME", "AVG_AST_CURRENT_SEASON_VISITOR", "AVG_AST_CURRENT_SEASON_HOME", "AVG_REB_CURRENT_SEASON_VISITOR", "AVG_REB_CURRENT_SEASON_HOME"]

classifier = ["HOME_TEAM_WINS"]

games_2003 = games_2003_stats[restData + coachingData + pastSeasonTeamPerformance + pastSeasonTop8PlayersPerformance + currentSeasonAverageStatsForPast10Days + currentSeasonAverageStatsOverall + classifier]

normalized_games_2003=(games_2003-games_2003.min())/(games_2003.max()-games_2003.min())

normalized_games_2003.to_csv('Project/Datasets/Derived/games_2003.csv', index=False, na_rep='0')









