import random
import copy
import math
import players

camels = [0,1,2,3,4]
num_camels = len(camels)
num_players = 4
finish_line = 12
display_updates = True

class GameState:
    def __init__(self):
        self.camel_track = [[]]*finish_line+2 #Plus 2 because they could roll a 3 and go a bit past the finish
        self.trap_track = [[]]*finish_line+2 #entry of the form [trap_type (-1,1), player]
        self.player_has_placed_trap = [False,False,False,False]
        self.round_bets = []		#of the form [camel,player]
        self.game_winner_bets = []			#of the form [camel,player]
        self.game_losing_bets = []			#of the form [camel,player]
        self.player_round_bets = []
        self.player_game_bets = [[False]*num_camels]*num_players #Players can only bet on a camel being a game winner/loser
        self.player_money_values = [3]*num_players
        self.camel_yet_to_move = [1]*num_camels
        self.active_game = True
        self.camels = camels
        initial_camels = copy.deepcopy(camels)

        for _ in range(0,num_camels):
                index = random.randint(0,len(initial_camels)-1)
                distance = random.randint(0,2)
                self.camel_track[distance].append(initial_camels[index])
                initial_camels.remove(initial_camels[index])

def MoveCamel(g,player):
    if (sum(g.camel_yet_to_move) < 0):
        print(str(player) + ' tried to move a camel when none could be moved')
        return False
        #raise ValueError(str(player) + ' tried to move a camel when none could be moved')
    selected_camel = False         #Select camel to move
    while not selected_camel:
        camel_index = random.randint(0,num_camels - 1)
        selected_camel = g.camel_yet_to_move[camel_index]
    g.camel_yet_to_move[camel_index] = 0 #Remove camel from pool
    [curr_pos,found_y_pos] = [(ix,iy) for ix, row in enumerate(g.camel_track) for iy, i in enumerate(row) if i == camel_index][0] #Find distance, check for traps
    stack = len(g.camel_track[curr_pos])-found_y_pos
    print(stack)
    print(g.camel_track)
    print(curr_pos)
    print(camel_index)
    distance = random.randint(1,3)
    if (len(g.trap_track[curr_pos + distance]) > 0):
        if display_updates : print("Player hit a trap!")
        g.player_money_values[g.trap_track[curr_pos + distance][1]] += 1 #Give the player a coin
        distance += g.trap_track[curr_pos + distance][0] #Change the distance
    camels_to_move = [] #Actually move camel
    for c in range(0,stack):
        camels_to_move.append(g.camel_track[curr_pos].pop(found_y_pos))
        g.camel_track[curr_pos + distance].append(camels_to_move[0])
        camels_to_move.clear()
    g.player_money_values[player] += 1 #Give the rolling player a coin
    if sum(g.camel_yet_to_move) == 0 : EndOfRound(g) #If round is over, trigger End Of Round effects
    if len(g.camel_track[finish_line]) + len(g.camel_track[finish_line + 1]) + len(g.camel_track[finish_line + 2]) > 0 :
        #print("EndOfGameTrigger")
        EndOfRound(g)
        EndOfGame(g) #If game is over, trigger End Of Game and round effects
    return True
    
def PlaceTrap(g,trap_type,trap_place,player):
    if ((trap_place > 0 and len(g.trap_track[trap_place - 1]) != 0) or (len(g.trap_track[trap_place]) != 0) or (trap_place < len(g.trap_track) and len(g.trap_track[trap_place + 1]) != 0)): raise ValueError(str(player) + ' tried to place a trap in an illegal spot') #Check to see if track placement is legal
    if g.player_has_placed_trap[player] == True : raise ValueError(str(player) + ' tried to place two traps somehow')
    g.trap_track[trap_place] = [trap_type,player]
    g.player_has_placed_trap[player] = True
    return True

def MoveTrap(g,trap_type,trap_place,player):
        #[curr_pos,stack] = [(ix,iy) for ix, row in enumerate(g.camel_track) for iy, i in enumerate(row) if i == camel_index][0] #Find distance, check for traps
    [curr_pos] = [y for y, row in enumerate(g.trap_track) if (row[1] if 0 < len(row) else None) == player]
    g.trap_track[curr_pos] = []
    g.player_has_placed_trap[player] = False
    PlaceTrap(g,trap_type,trap_place,player)
    return True

def PlaceGameWinnerBet(g,camel,player):
    if (g.player_game_bets[player][camel] == True) :
        print(str(player) + ' tried to bet on a camel winning that theyd already bet on!')
        return False
        #raise ValueError(str(player) + ' tried to bet on a camel winning that theyd already bet on!')
    g.game_winner_bets.append([camel,player])
    g.player_game_bets[player][camel] = True
    return True

def PlaceGameLoserBet(g,camel,player):
    if (g.player_game_bets[player][camel] == 0) :
        print(str(player) + ' tried to bet on a camel winning that theyd already bet on!')
        return False
    #if (g.player_game_bets[player][camel] == 0) : raise ValueError(str(player) + ' tried to bet on a camel losing that theyd already bet on!')
    g.game_losing_bets.append([camel,player])
    g.player_game_bets[player][camel] = 0
    return True

def PlaceRoundWinnerBet(g,camel,player):
    g.round_bets.append([camel,player])
    return True

def EndOfRound(g):
    first_place_payout = [5,3,2,0] #Settle round bets
    second_place_payout = 1
    third_or_worse_place_payout = -1
    
    first_place_payout_index = 0
    
    first_place_camel = FindCamelInNthPlace(g.camel_track,1)
    second_place_camel = FindCamelInNthPlace(g.camel_track,2)
    
    for i in range(0,len(g.round_bets) - 1): #Payout
        if g.round_bets[i][0] == first_place_camel :
            g.player_money_values[g.round_bets[i][1]] += (first_place_payout[first_place_payout_index] if first_place_payout_index < len(first_place_payout) else 0) #handles out of range exceptions by returning 0
            if display_updates : print("Paid Player " + str(g.round_bets[i][1]) + " " + str(first_place_payout[first_place_payout_index]) + " coins for selecting the round winner")
            first_place_payout_index += 1
        elif g.round_bets[i][0] == second_place_camel : 
            g.player_money_values[g.round_bets[i][1]] += second_place_payout
            if display_updates : print("Paid Player " + str(g.round_bets[i][1]) + " " + str(second_place_payout) + " coins for selecting the round runner up")
        else : 
            g.player_money_values[g.round_bets[i][1]] += second_place_payout
            if display_updates : print("Paid Player " + str(g.round_bets[i][1]) + " " + str(third_or_worse_place_payout) + " coins for selecting the a third place or worse camel")
    g.camel_bet_values = [5,5,5,5,5] #Reset camel bet values and camels yet to move
    g.camel_yet_to_move = [1,1,1,1,1]
    g.round_bets = [] #clear round bets
    return

def EndOfGame(g):
    winning_camel = FindCamelInNthPlace(g.camel_track,1) #Find camel that won
    losing_camel = FindCamelInNthPlace(g.camel_track,num_camels) #Find camel that lost
    
    # Settle game bets
        # game_bets are of the form [camel,player]

        # Selecting correct winner gives 8,5,3,1,1,1,1
        # Selecting wrong gives -1
        #Settle bets on winning camel
    
    payout_index = 0
    payout_struct = [8,5,3,1] #anything out of bounds gives a 1
    for i in range(0,len(g.game_winner_bets) - 1):
        if g.game_winner_bets[i][0] == winning_camel: #if you win, get prize
            g.player_money_values[g.game_winner_bets[i][1]] += (payout_struct[payout_index] if payout_index < len(payout_struct) else 1)
            if display_updates : print("Paid Player " + str(g.game_winner_bets[i][1]) + " " + str(payout_struct[payout_index] if payout_index < len(payout_struct) else 1) + " coins for selecting the game winner")
            payout_index += 1 #decrease value of guessing winning camel
        else:
            g.player_money_values[g.game_winner_bets[i][1]] -= 1
            if display_updates : print("Paid Player " + str(g.game_winner_bets[i][1]) + " -1 coins for incorrectly selecting the game winner")

    payout_index = 0 #Settle bets on losing camel
    for i in range(0,len(g.game_losing_bets) - 1):
        if g.game_losing_bets[i][0] == winning_camel: #if you win, get prize
            g.player_money_values[g.game_losing_bets[i][1]] += payout_struct[payout_index]
            if display_updates : print("Paid Player " + str(g.game_losing_bets[i][1]) + " " + str(payout_struct[payout_index] if payout_index < len(payout_struct) else 1) + " coins for selecting the game loser")
            payout_index += 1 #decrease value of guessing winning camel
        else:
            g.player_money_values[g.game_losing_bets[i][1]] -= 1
            if display_updates : print("Paid Player " + str(g.game_winner_bets[i][1]) + " -1 coins for incorrectly selecting the game loser")

    g.active_game = False
    return True

def FindCamelInNthPlace(track,n):
    if (n > num_camels or n < 1): raise ValueError('Something tried to find a camel in a Nth place, where N is out of bounds')	
    found_camel = False
    camels_counted = 0
    i = 1
    while not found_camel:
        dtg = n - camels_counted
        camels_in_stack = len(track[len(track)-i])
        if camels_in_stack >= dtg: return track[len(track) - i][camels_in_stack - dtg] 
        else :
            camels_counted += camels_in_stack
            i += 1
    return False

def DisplayGamestate(g):
    print("Track:")
    DisplayTrackState(g.camel_track)
    print("\n")
    print("Traps:")
    DisplayTrackState(g.trap_track)
    print("\n")
    print("$ Totals:")
    print("\t" + str(g.player_money_values))
    print("\n")

def DisplayTrackState(track):
    max_stack = len(max(track,key=len))

    #Print milestones
    track_label_string = "\t|"
    for _ in range(0,finish_line): track_label_string += ("-" + str(_) + "-|")
    print(track_label_string)

    #Print blank line
    track_label_string = "\t|"
    for _ in range(0,finish_line): track_label_string += ("----")
    print(track_label_string+"-|")

    #Print N/A if there are no objects (camels/traps)
    if max_stack == 0:
        track_label_string = "\t  " #extra spaces because double digit numbers mess things up
        for _ in range(0,finish_line): track_label_string += ("  ")
        print(track_label_string+"NA")

    #otherwise print those objects
    for stack_spot in range(0,max_stack):
        track_string = "\t"
        for track_spot in range(0,finish_line):
            if len(track[track_spot]) >= max_stack-stack_spot:
                str_len = len(str(track[track_spot][max_stack-stack_spot-1]))
                track_string += ("|" + " "*(2-str_len)+ str(track[track_spot][max_stack-stack_spot-1]) + " "*len(str(track_spot)))
            else: track_string += ("|" + " "*(2+len(str(track_spot))))
        print(track_string+"|")

    #Print blank line again
    track_label_string = "\t|"
    for _ in range(0,finish_line): track_label_string += ("----")
    print(track_label_string+"-|")

    #Print milestones again
    track_label_string = "\t|"
    for _ in range(0,finish_line): track_label_string += ("-" + str(_) + "-|")
    print(track_label_string)


def GameModerator():
    def players_definitions(player,game):
        if player == 0:
            return players.Player0(player,game)
        elif player == 1:
            return players.Player1(player,game)
        elif player == 2:
            return players.Player2(player,game)
        elif player == 3:
            return players.Player3(player,game)

    def action(result,player):
        if display_updates: print("Player Action: " + str(result))
        if result[0] == 0: #Player wants to move camel
            MoveCamel(g,player)
            if display_updates: print("Player " + str(player) + " moved camel")
        elif result[0] == 1: #Player wants to place trap
            if g.player_has_placed_trap[player]: MoveTrap(g,result[1],result[2],player)
            else : PlaceTrap(g,result[1],result[2],player)
            if display_updates: print("Player " + str(player) + " placed a trap")
        elif result[0] == 2: #Player wants to make round winner bet
            PlaceRoundWinnerBet(g,result[1],player)
            if display_updates: print("Player " + str(player) + " made a round winner bet")
        elif result[0] == 3: #Player wants to make game winner bet
            PlaceGameWinnerBet(g,result[1],player)
            if display_updates: print("Player " + str(player) + " made a game winner bet")
        elif result[0] == 4: #Player wants to make game loser bet
            PlaceGameLoserBet(g,result[1],player)
            if display_updates: print("Player " + str(player) + " made a game loser bet")
        else:
            print("oh jeez result was out of bounds")
            print("Player commited: " + str(player))
            print("Action attempted: " + str(result))
        return
            

    g = GameState()
    g_round = 0
    while g.active_game:
        active_player = (g_round%4)
        action(players_definitions(active_player,g),active_player)
        g_round += 1
        if display_updates:
            DisplayGamestate(g)
    return
GameModerator()