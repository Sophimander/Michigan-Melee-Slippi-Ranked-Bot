import datetime

from slippi import slippi_ranked, slippi_data
from database import database_setup
from database import database_operations as do
import discord_bot


users_codes = ["Soph,so#0",
               "ninja1167,NINJ#330",
               "SIN KISKE,TNDR#944",
               "Aloof,GAMR#723",
               "LilyMW,Haha#450",
               "Hell0Wrld,WRLD#252",
               "Waffle(call me dani you animals),wffl#231",
               "erhi0pium,opium#0",
               "Muuglek,KING#407",
               "Coleslaw,COLE#672",
               "denpa,dnpa#727",
               "Xatudrip,xatu#584",
               "polymath,poly#832",
               "ferrety,ferr#293",
               "mathandsurf,math#621",
               "stink bomb terrorist,help#712",
               "slicksiwik,slik#917",
               "brazmonkey,braz#13",
               "mc zero,mc#0",
               "rich,rich#0",
               "fledgling,grlboy#0",
               "maclo4,macl#421",
               "PRETTYBOIFLOCKA,ASAP#254",
               "ZrAcid,acid#441",
               "Paco_Goosequacko,PACO#594",
               "Negat!ve,BRUH#413",
               "Bomb,BADF#931",
               "htcp,htcp#231",
               "Nyte,Nyte#185",
               "Coin,COIN#492",
               "shoopzerder,sein#244"]

full_user_codes = ["Soph,so#0,126913881879740416",
                   "ninja1167,NINJ#330,820273017875202089",
                   "SIN KISKE,TNDR#944,564138198389751819",
                   "Aloof,GAMR#723,183057602115141632",
                   "LilyMW,Haha#450,1053258638682247219",
                   "Hell0Wrld,WRLD#252,1052856622273265695",
                   "erhi0pium,opium#0,1053129307385495614",
                   "Muuglek,KING#407,1051973278169841704",
                   "Coleslaw,COLE#672,1051987771855749201",
                   "denpa,dnpa#727,1053011041992323084",
                   "Xatudrip,xatu#584,1053188329157439508",
                   "polymath,poly#832,433683686760775681",
                   "ferrety,ferr#293,1048080122210697258",
                   "mathandsurf,math#621,332587851151704077",
                   "stink bomb terrorist,help#712,1052667826705535116",
                   "slicksiwik,slik#917,315517836371951626",
                   "brazmonkey,braz#13,76109907408977920",
                   "mc zero,mc#0,1052692566082068561",
                   "rich,rich#0,165644859447705600",
                   "fledgling,grlboy#0,114178785674264581",
                   "maclo4,macl#421,928831896404762674",
                   "ZrAcid,acid#441,1053130095079989368",
                   "Paco_Goosequacko,PACO#594,351243628771016706",
                   "Negat!ve,BRUH#413,936514899637583932",
                   "Bomb,BADF#931,152942824638251018",
                   "htcp,htcp#231,1053011042772471888",
                   "Nyte,Nyte#185,133026050505572352",
                   "Coin,COIN#492,96101675722379264",
                   "Gaussian,gsan#552,799525240614813726",
                   "Nara,NARA#836,1048074347492950036",
                   "helm,helm#591,148601885811539968",
                   "jackie,Bel#306,143935513508708353",
                   "Mushu,MUSH#683,413007200940851201",
                   "Jflip,Flip#178,1048075870994186331",
                   "huh?,HUH#517,339462683914928138",
                   "Joka,Joka#162,1054181286450823229",
                   "shoopzerder,sein#244,965218421144973322",
                   "Nara's DK,SHAC#339,404148836911808517",
                   "Dubz,DUBZ#757,172914188946112512",
                   "Andy,SHAF#596,156211421049389057"
                   ]


def create_user_data(conn):
    for player in full_user_codes:
        player_info = player.split(",")
        print(slippi_data.create_user_entry(conn, int(player_info[2]), player_info[0], player_info[1]))


def create_ranked_list():
    leaderboard = []
    for player in users_codes:
        player_info = player.split(",")
        slippi_stats = slippi_ranked.get_player_ranked_data(player_info[1], player_info[0])
        if slippi_stats:
            leaderboard.append(slippi_stats)

    leaderboard.sort(reverse=True, key=slippi_ranked.elo_sort)

    incr = 0
    for position in leaderboard:
        incr += 1
        print(f"{incr}. {position[0]} | {position[3]} ({position[4]}/{position[5]})")


def main():
    print("Main ran")

    conn = do.create_con("database.db")
    database_setup.create_database(conn, conn.cursor())


if __name__ == '__main__':
    main()

