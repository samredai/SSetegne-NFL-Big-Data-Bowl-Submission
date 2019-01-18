from flask import Flask, render_template, render_template_string, request, current_app
import pandas as pd
import traceback
import pickle as p

app = Flask(__name__)
app.add_url_rule('/static/<path:filename>', endpoint='static',
                 view_func=app.send_static_file)
                 
try:
    app.csmodel = p.load( open( "catchSeparationModel.pkl", "rb" ) )
except FileNotFoundError:
    app.csmodel = p.load( open( "/home/ssetegne/nfl_animation_site/catchSeparationModel.pkl", "rb" ) )

topbar = '''
<div id="navbar">
  <a href="/">-Home-</a>
  <a href="/csm/v1">-Catch Separation Predictor-</a>
  <a href="/games">-Visualize Tracking Data-</a>
</div>
'''

topbar_js = '''
<script>
window.onscroll = function() {myFunction()};

var navbar = document.getElementById("navbar");
var sticky = navbar.offsetTop;

function myFunction() {
  if (window.pageYOffset >= sticky) {
    navbar.classList.add("sticky")
  } else {
    navbar.classList.remove("sticky");
  }
}
</script>
'''

def getPlay(datadf, gameId, playId):
    filtdf = datadf[(datadf['gameId'] == int(gameId)) & (datadf['playId'] == int(playId))]
    return filtdf

def getPlayMovement(playdf):
    away = playdf[(playdf['team'] == 'away')]
    home = playdf[(playdf['team'] == 'home')]
    #Get the ball tracking data
    ball = playdf[(playdf['team'] == 'ball')]
    ballTracking = {'x' : ball['x'].tolist(), 'y' : ball['y'].tolist()}
    ####
    awayPlayerTracking = {}
    homePlayerTracking = {}
    awayPlayerNames = away['displayName'].unique().tolist()
    homePlayerNames = home['displayName'].unique().tolist()
    for player in awayPlayerNames:
        playerMoves = away[(away['displayName'] == player)]
        awayPlayerTracking[player] = {'x' : playerMoves['x'].tolist(), 'y' : playerMoves['y'].tolist(), 'position' : playerMoves['PositionAbbr'].tolist()}
    for player in homePlayerNames:
        playerMoves = home[(home['displayName'] == player)]
        homePlayerTracking[player] = {'x' : playerMoves['x'].tolist(), 'y' : playerMoves['y'].tolist(), 'position' : playerMoves['PositionAbbr'].tolist()}
    numframes = playdf['frame.id'].max()
    playMovement = { 'players' : { 'away' : awayPlayerTracking, 'home' : homePlayerTracking, 'awayNames' : awayPlayerNames, 'homeNames' : homePlayerNames }, 'ball' : ballTracking,'numberOfFrames' : numframes }
    return playMovement

def getPlayMovementCSS(playMovements):
    frameMultiplier = 100/playMovements['numberOfFrames']
    awaycssMovements = {}
    awaycounter = 1
    #Ball
    xpoints = playMovements['ball']['x']
    ypoints = playMovements['ball']['y']
    startx = playMovements['ball']['x'][0]
    starty = playMovements['ball']['y'][0]
    endx = playMovements['ball']['x'][-1]
    endy = playMovements['ball']['y'][-1]
    css = '''
        #football {
        position: absolute;
        top: '''+str(537-(starty*10))+'''px;
        left: '''+str(startx*10)+'''px;
        z-index: 999;
        -webkit-animation: football-route 6s infinite linear;
        animation-play-state: paused;
        }

        '''
    css += '@-webkit-keyframes football-route { \n'
    percentage = 0
    for counter, x in enumerate(xpoints):
        css += '\n' + str(percentage*frameMultiplier) + '% \n{ \nleft: ' + str(x*10) + 'px; \n'
        css += 'top: ' + str(537-ypoints[counter]*10) + 'px; \n} \n'
        percentage += 1
    css += '\n100% \n{ \nleft: ' + str(endx*10) + 'px; \n'
    css += 'top: ' + str(537-endy*10) + 'px; \n} \n'
    ballMovements = css + '}\n\n'
    ########
    
    for player in playMovements['players']['away']:
        xpoints = playMovements['players']['away'][player]['x']
        ypoints = playMovements['players']['away'][player]['y']
        startx = playMovements['players']['away'][player]['x'][0]
        starty = playMovements['players']['away'][player]['y'][0]
        endx = playMovements['players']['away'][player]['x'][-1]
        endy = playMovements['players']['away'][player]['y'][-1]
        position = playMovements['players']['away'][player]['position'][0]
        if position in ('WR', 'TE', 'RB', 'FB'):
           css = '''
           #player'''+str(awaycounter)+'''-away {
           position: absolute;
           top: '''+str(537-(starty*10))+'''px;
           left: '''+str(startx*10)+'''px;
           -webkit-animation: player'''+str(awaycounter)+'''-away-route 6s infinite linear;
           -webkit-transform: translate(-50%, -50%);
           animation-play-state: paused;
           border: 3px solid #333;
           position: absolute;
           height: 100px;
           width: 100px;
           -moz-border-radius:75px;
           -webkit-border-radius: 75px;
           }
           '''
        else:
            css = '''
            #player'''+str(awaycounter)+'''-away {
            position: absolute;
            top: '''+str(537-(starty*10))+'''px;
            left: '''+str(startx*10)+'''px;
            -webkit-animation: player'''+str(awaycounter)+'''-away-route 6s infinite linear;
            -webkit-transform: translate(-50%, -50%);
            animation-play-state: paused;
            }
            '''
        css += '@-webkit-keyframes player' + str(awaycounter) + '-away-route { \n'
        percentage = 0
        for counter, x in enumerate(xpoints):
            css += '\n' + str(percentage*frameMultiplier) + '% \n{ \nleft: ' + str(x*10) + 'px; \n'
            css += 'top: ' + str(537-ypoints[counter]*10) + 'px; \n} \n'
            percentage += 1
        css += '\n100% \n{ \nleft: ' + str(endx*10) + 'px; \n'
        css += 'top: ' + str(537-endy*10) + 'px; \n} \n'
        awaycssMovements[player] = css + '}\n\n'
        awaycounter += 1
    homecssMovements = {}
    homecounter = 1
    for player in playMovements['players']['home']:
        xpoints = playMovements['players']['home'][player]['x']
        ypoints = playMovements['players']['home'][player]['y']
        startx = playMovements['players']['home'][player]['x'][0]
        starty = playMovements['players']['home'][player]['y'][0]
        endx = playMovements['players']['home'][player]['x'][-1]
        endy = playMovements['players']['home'][player]['y'][-1]
        position = playMovements['players']['home'][player]['position'][0]
        if position in ('WR', 'TE', 'RB', 'FB'):
            css = '''
            #player'''+str(homecounter)+'''-home {
            position: absolute;
            top: '''+str(537-(starty*10))+'''px;
            left: '''+str(startx*10)+'''px;
            -webkit-animation: player'''+str(homecounter)+'''-home-route 6s infinite linear;
            -webkit-transform: translate(-50%, -50%);
            animation-play-state: paused;
            border: 3px solid #333;
            position: absolute;
            height: 100px;
            width: 100px;
            -moz-border-radius:75px;
            -webkit-border-radius: 75px;
            }
            '''
        else:
             css = '''
             #player'''+str(homecounter)+'''-home {
             position: absolute;
             top: '''+str(537-(starty*10))+'''px;
             left: '''+str(startx*10)+'''px;
             -webkit-animation: player'''+str(homecounter)+'''-home-route 6s infinite linear;
             -webkit-transform: translate(-50%, -50%);
             animation-play-state: paused;
             }
             '''
        css += '@-webkit-keyframes player' + str(homecounter) + '-home-route { \n'
        percentage = 0
        for counter, x in enumerate(xpoints):
            css += '\n' + str(percentage*frameMultiplier) + '% \n{ \nleft: ' + str(x*10) + 'px; \n'
            css += 'top: ' + str(537-ypoints[counter]*10) + 'px; \n} \n'
            percentage += 1
        css += '\n100% \n{ \nleft: ' + str(endx*10) + 'px; \n'
        css += 'top: ' + str(537-endy*10) + 'px; \n} \n'
        homecssMovements[player] = css + '}\n\n'
        homecounter += 1
    cssMovements = {'away' : awaycssMovements, 'home' : homecssMovements, 'ball' : ballMovements, 'awayNames' : playMovements['players']['awayNames'], 'homeNames' : playMovements['players']['homeNames']}
    return cssMovements

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/games")
def games():
        try:
                try:
                    df = pd.read_csv(r'/home/ssetegne/nfl_animation_site/Data/games.csv')
                except:
                    df = pd.read_csv(r'Data/games.csv')
                games = df.to_dict('records')
                html = '''
                <!DOCTYPE html>
                <html>
                <head>
                <link rel="stylesheet" href="{{ url_for('static', filename='css/games.css') }}">
                <link rel="stylesheet" href="{{ url_for('static', filename='css/topbar.css') }}">
                <link rel="apple-touch-icon" sizes="57x57" href="{{ url_for('static', filename='images/favicons/apple-icon-57x57.png') }}">
                <link rel="apple-touch-icon" sizes="60x60" href="{{ url_for('static', filename='images/favicons/apple-icon-60x60.png') }}">
                <link rel="apple-touch-icon" sizes="72x72" href="{{ url_for('static', filename='images/favicons/apple-icon-72x72.png') }}">
                <link rel="apple-touch-icon" sizes="76x76" href="{{ url_for('static', filename='images/favicons/apple-icon-76x76.png') }}">
                <link rel="apple-touch-icon" sizes="114x114" href="{{ url_for('static', filename='images/favicons/apple-icon-114x114.png') }}">
                <link rel="apple-touch-icon" sizes="120x120" href="{{ url_for('static', filename='images/favicons/apple-icon-120x120.png') }}">
                <link rel="apple-touch-icon" sizes="144x144" href="{{ url_for('static', filename='images/favicons/apple-icon-144x144.png') }}">
                <link rel="apple-touch-icon" sizes="152x152" href="{{ url_for('static', filename='images/favicons/apple-icon-152x152.png') }}">
                <link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='images/favicons/apple-icon-180x180.png') }}">
                <link rel="icon" type="image.png" sizes="192x192"  href="{{ url_for('static', filename='images/favicons/android-icon-192x192.png') }}">
                <link rel="icon" type="image.png" sizes="32x32" href="{{ url_for('static', filename='images/favicons/favicon-32x32.png') }}">
                <link rel="icon" type="image.png" sizes="96x96" href="{{ url_for('static', filename='images/favicons/favicon-96x96.png') }}">
                <link rel="icon" type="image.png" sizes="16x16" href="{{ url_for('static', filename='images/favicons/favicon-16x16.png') }}">
                <link rel="manifest" href="{{ url_for('static', filename='images/favicons/manifest.json') }}">
                <meta name="msapplication-TileColor" content="#ffffff">
                <meta name="msapplication-TileImage" content="{{ url_for('static', filename='images/favicons/ms-icon-144x144.png') }}">
                <meta name="theme-color" content="#ffffff">
                </head>
                <meta charset="utf-8" />
                <title>SSetegne - NFL Big Data Bowl Competition Submission</title>
                <body>
                ''' + topbar + '''
                <div class="content">
                <b>Select a game to view plays.</b>
                {% for item in requestedList %}
                <br><a href="/games/{{ item.gameId }}"><button type="button" class="block">{{ item.homeDisplayName }} ({{ item.HomeScore }}) vs. {{ item.visitorDisplayName }} ({{ item.VisitorScore }}) - {{ item.season }} season, Week {{ item.week }}, {{ item.gameDate }}</button></a>
                {% endfor %}
                </div>
                ''' + topbar_js + '''
                </body>
                </html>
                '''
                page = render_template_string(html, requestedList = games)
                return page
        except Exception as e:
                return ("There was a problem: " + str(e))

@app.route("/games/<req_gameId>")
def plays(req_gameId):
        try:
            df = pd.read_csv(r'/home/ssetegne/nfl_animation_site/Data/plays.csv')
        except:
            df = pd.read_csv(r'Data/plays.csv')
        game = df[(df['gameId'] == int(req_gameId))]
        playList = []
        for row in game.itertuples():
                play = {'playId' : row.playId, 'playDescription' : row.playDescription}
                playList.append(play)
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
        <link rel="stylesheet" href="{{ url_for('static', filename='css/games.css') }}">
        <link rel="stylesheet" href="{{ url_for('static', filename='css/topbar.css') }}">
        <link rel="apple-touch-icon" sizes="57x57" href="{{ url_for('static', filename='images/favicons/apple-icon-57x57.png') }}">
        <link rel="apple-touch-icon" sizes="60x60" href="{{ url_for('static', filename='images/favicons/apple-icon-60x60.png') }}">
        <link rel="apple-touch-icon" sizes="72x72" href="{{ url_for('static', filename='images/favicons/apple-icon-72x72.png') }}">
        <link rel="apple-touch-icon" sizes="76x76" href="{{ url_for('static', filename='images/favicons/apple-icon-76x76.png') }}">
        <link rel="apple-touch-icon" sizes="114x114" href="{{ url_for('static', filename='images/favicons/apple-icon-114x114.png') }}">
        <link rel="apple-touch-icon" sizes="120x120" href="{{ url_for('static', filename='images/favicons/apple-icon-120x120.png') }}">
        <link rel="apple-touch-icon" sizes="144x144" href="{{ url_for('static', filename='images/favicons/apple-icon-144x144.png') }}">
        <link rel="apple-touch-icon" sizes="152x152" href="{{ url_for('static', filename='images/favicons/apple-icon-152x152.png') }}">
        <link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='images/favicons/apple-icon-180x180.png') }}">
        <link rel="icon" type="image.png" sizes="192x192"  href="{{ url_for('static', filename='images/favicons/android-icon-192x192.png') }}">
        <link rel="icon" type="image.png" sizes="32x32" href="{{ url_for('static', filename='images/favicons/favicon-32x32.png') }}">
        <link rel="icon" type="image.png" sizes="96x96" href="{{ url_for('static', filename='images/favicons/favicon-96x96.png') }}">
        <link rel="icon" type="image.png" sizes="16x16" href="{{ url_for('static', filename='images/favicons/favicon-16x16.png') }}">
        <link rel="manifest" href="{{ url_for('static', filename='images/favicons/manifest.json') }}">
        <meta name="msapplication-TileColor" content="#ffffff">
        <meta name="msapplication-TileImage" content="{{ url_for('static', filename='images/favicons/ms-icon-144x144.png') }}">
        <meta name="theme-color" content="#ffffff">
        </head>
        <meta charset="utf-8" />
        <title>SSetegne - NFL Big Data Bowl Competition Submission</title>
        <body>
        ''' + topbar + '''
        <div class="content">
        <b>Play's from game #{{ gameId }}
        {% for item in requestedList %}
        <br><a href="/games/{{ gameId }}/{{ item.playId }}"><button type="button" class="block">{{ item.playDescription }}</button></a>
        {% endfor %}
        </div>
        ''' + topbar_js + '''
        </body>
        </html>
        '''
        return render_template_string(html, requestedList = playList, gameId = req_gameId)

@app.route("/games/<req_gameId>/<req_playId>")
def gameAnimation(req_gameId, req_playId):
        try:
                try:
                    df = pd.read_csv(r'/home/ssetegne/nfl_animation_site/Data/tracking_gameId_' + str(req_gameId) + '.csv')
                    df_players = pd.read_csv(r'/home/ssetegne/nfl_animation_site/Data/players.csv')
                except:
                    df = pd.read_csv(r'Data/tracking_gameId_' + str(req_gameId) + '.csv')
                    df_players = pd.read_csv(r'Data/players.csv')
                df_players = df_players[['nflId','PositionAbbr']]
                df = df.join(df_players.set_index('nflId'), on='nflId')
                play44 = getPlayMovement(getPlay(df, req_gameId, req_playId)) #touchdown
                cssMotion = getPlayMovementCSS(play44)
                css = ''
                awayPlayers = cssMotion['awayNames']
                homePlayers = cssMotion['homeNames']
                #Football movements
                css += cssMotion['ball']

                #Away team movements
                for player in cssMotion['away']:
                        css += cssMotion['away'][player]

                #Home team movements
                for player in cssMotion['home']:
                        css += cssMotion['home'][player]
                
                stylecss = '''
                * {
                margin: 0;
                padding: 0;
                }

                header {
                height: 537px;
                width: 1200px;
                }
                
                body {
                  background-color: #b5c588;
                  font-size: 30px;
                  font-family: 'Karla', sans-serif;
                }
                
                button {
                  background-color: #4CAF50; /* Green */
                  border: none;
                  color: white;
                  padding: 15px 32px;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 16px;
                }

                .field {
                height: 537px;
                width: 1200px;
                position: relative;
                background: url(/static/images/field.png);
                background-color: green;
                margin: auto;
                }

                #wrapper {
                  text-align: center;
                }

                .controls {
                position: relative;
                margin: auto;
                display: inline-block;
                }
                
                .player-home {
                background: url(/static/images/home_player.png);
                background-repeat: no-repeat;
                background-size: 30px 30px;
                background-position: center;
                position: absolute;
                height: 40px;
                width: 40px;
                }

                .player-away {
                background: url(/static/images/away_player.png);
                background-repeat: no-repeat;
                background-size: 30px 30px;
                background-position: center;
                position: absolute;
                height: 40px;
                width: 40px;
                }
                '''
                fullcss = '<style>' + stylecss + '\n' + css + '</style>'
                page = '''
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="utf-8" />
                <title>SSetegne - NFL Big Data Bowl Competition Submission</title>
                <link href="https://fonts.googleapis.com/css?family=Karla" rel="stylesheet">
				<link rel="apple-touch-icon" sizes="57x57" href="{{ url_for('static', filename='images/favicons/apple-icon-57x57.png') }}">
				<link rel="apple-touch-icon" sizes="60x60" href="{{ url_for('static', filename='images/favicons/apple-icon-60x60.png') }}">
				<link rel="apple-touch-icon" sizes="72x72" href="{{ url_for('static', filename='images/favicons/apple-icon-72x72.png') }}">
				<link rel="apple-touch-icon" sizes="76x76" href="{{ url_for('static', filename='images/favicons/apple-icon-76x76.png') }}">
				<link rel="apple-touch-icon" sizes="114x114" href="{{ url_for('static', filename='images/favicons/apple-icon-114x114.png') }}">
				<link rel="apple-touch-icon" sizes="120x120" href="{{ url_for('static', filename='images/favicons/apple-icon-120x120.png') }}">
				<link rel="apple-touch-icon" sizes="144x144" href="{{ url_for('static', filename='images/favicons/apple-icon-144x144.png') }}">
				<link rel="apple-touch-icon" sizes="152x152" href="{{ url_for('static', filename='images/favicons/apple-icon-152x152.png') }}">
				<link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='images/favicons/apple-icon-180x180.png') }}">
				<link rel="icon" type="image.png" sizes="192x192"  href="{{ url_for('static', filename='images/favicons/android-icon-192x192.png') }}">
				<link rel="icon" type="image.png" sizes="32x32" href="{{ url_for('static', filename='images/favicons/favicon-32x32.png') }}">
				<link rel="icon" type="image.png" sizes="96x96" href="{{ url_for('static', filename='images/favicons/favicon-96x96.png') }}">
				<link rel="icon" type="image.png" sizes="16x16" href="{{ url_for('static', filename='images/favicons/favicon-16x16.png') }}">
				<link rel="manifest" href="{{ url_for('static', filename='images/favicons/manifest.json') }}">
				<meta name="msapplication-TileColor" content="#ffffff">
				<meta name="msapplication-TileImage" content="{{ url_for('static', filename='images/favicons/ms-icon-144x144.png') }}">
				<meta name="theme-color" content="#ffffff">
                {fullcss}
                </head>
                <body>
                <div id="wrapper"> 
                <div class="controls">
                <button onclick="togglePlayState('Paused');">Pause</button>
                <button onclick="togglePlayState('Running');">Play</button>
                </div>
                </div>
                                <div class="field">
                                        <img src="/static/images/football.png" alt="football" id="football" />
                                        <p alt="player1-home"  id="player1-home"  class="player-home catch-circle" title="{player1home}" /> 
                                        <p alt="player2-home"  id="player2-home"  class="player-home" title="{player2home}" />
                                        <p alt="player3-home"  id="player3-home"  class="player-home" title="{player3home}" />
                                        <p alt="player4-home"  id="player4-home"  class="player-home" title="{player4home}" />
                                        <p alt="player5-home"  id="player5-home"  class="player-home" title="{player5home}" />
                                        <p alt="player6-home"  id="player6-home"  class="player-home" title="{player6home}" />
                                        <p alt="player7-home"  id="player7-home"  class="player-home" title="{player7home}" />
                                        <p alt="player8-home"  id="player8-home"  class="player-home" title="{player8home}" />
                                        <p alt="player9-home"  id="player9-home"  class="player-home" title="{player9home}" />
                                        <p alt="player10-home" id="player10-home" class="player-home" title="{player10home}" />
                                        <p alt="player11-home" id="player11-home" class="player-home" title="{player11home}" />
                                        <p alt="player1-away"  id="player1-away"  class="player-away" title="{player1away}"  />
                                        <p alt="player2-away"  id="player2-away"  class="player-away" title="{player2away}"  />
                                        <p alt="player3-away"  id="player3-away"  class="player-away" title="{player3away}"  />
                                        <p alt="player4-away"  id="player4-away"  class="player-away" title="{player4away}"  />
                                        <p alt="player5-away"  id="player5-away"  class="player-away" title="{player5away}"  />
                                        <p alt="player6-away"  id="player6-away"  class="player-away" title="{player6away}"  />
                                        <p alt="player7-away"  id="player7-away"  class="player-away" title="{player7away}"  />
                                        <p alt="player8-away"  id="player8-away"  class="player-away" title="{player8away}"  />
                                        <p alt="player9-away"  id="player9-away"  class="player-away" title="{player9away}"  />
                                        <p alt="player10-away" id="player10-away" class="player-away" title="{player10away}" />
                                        <p alt="player11-away" id="player11-away" class="player-away" title="{player11away}" />
                                </div>
                <div id="wrapper"> 
                <b>note: Circles represent a 5 yard catch radius around WR's, TE's, RB's, and FB's</b>
                <br>
                <div class="controls">
                <button onclick="togglePlayState('Paused');">Pause</button>
                <button onclick="togglePlayState('Running');">Play</button>
                </div>
                </div>
                </div>
                </body>
                <script>
                function togglePlayState(newState) {{
                        document.getElementById("football").style.animationPlayState=newState;
                        document.getElementById("player1-home").style.animationPlayState=newState;
                        document.getElementById("player2-home").style.animationPlayState=newState;
                        document.getElementById("player3-home").style.animationPlayState=newState;
                        document.getElementById("player4-home").style.animationPlayState=newState;
                        document.getElementById("player5-home").style.animationPlayState=newState;
                        document.getElementById("player6-home").style.animationPlayState=newState;
                        document.getElementById("player7-home").style.animationPlayState=newState;
                        document.getElementById("player8-home").style.animationPlayState=newState;
                        document.getElementById("player9-home").style.animationPlayState=newState;
                        document.getElementById("player10-home").style.animationPlayState=newState;
                        document.getElementById("player11-home").style.animationPlayState=newState;
                        document.getElementById("player1-away").style.animationPlayState=newState;
                        document.getElementById("player2-away").style.animationPlayState=newState;
                        document.getElementById("player3-away").style.animationPlayState=newState;
                        document.getElementById("player4-away").style.animationPlayState=newState;
                        document.getElementById("player5-away").style.animationPlayState=newState;
                        document.getElementById("player6-away").style.animationPlayState=newState;
                        document.getElementById("player7-away").style.animationPlayState=newState;
                        document.getElementById("player8-away").style.animationPlayState=newState;
                        document.getElementById("player9-away").style.animationPlayState=newState;
                        document.getElementById("player10-away").style.animationPlayState=newState;
                        document.getElementById("player11-away").style.animationPlayState=newState;
                }}
                </script>
                </html>
                '''.format(fullcss=fullcss, \
                player1home=homePlayers[0], \
                player2home=homePlayers[1], \
                player3home=homePlayers[2], \
                player4home=homePlayers[3], \
                player5home=homePlayers[4], \
                player6home=homePlayers[5], \
                player7home=homePlayers[6], \
                player8home=homePlayers[7], \
                player9home=homePlayers[8], \
                player10home=homePlayers[9], \
                player11home=homePlayers[10], \
                player1away=awayPlayers[0], \
                player2away=awayPlayers[1], \
                player3away=awayPlayers[2], \
                player4away=awayPlayers[3], \
                player5away=awayPlayers[4], \
                player6away=awayPlayers[5], \
                player7away=awayPlayers[6], \
                player8away=awayPlayers[7], \
                player9away=awayPlayers[8], \
                player10away=awayPlayers[9], \
                player11away=awayPlayers[10])
                return render_template_string(page, game = req_gameId, play = req_playId)
        except Exception as e:
                return ("There was a problem: " + str(e) + "\nFull Traceback:\n " + str(traceback.format_exc()))

@app.route("/csm/v1", methods=['GET', 'POST'])
def catchSeparationModel():
    if request.method == 'POST':
        sample = {}
        sample[0] = [request.form["rec2_xroute"]] # xReceiverMate1
        sample[1] = [request.form["rec2_yroute"]] # yReceiverMate1
        sample[2] = [request.form["rec3_xroute"]] # xReceiverMate2
        sample[3] = [request.form["rec3_yroute"]] # yReceiverMate2
        sample[4] = [request.form["rec4_xroute"]] # xReceiverMate3
        sample[5] = [request.form["rec4_yroute"]] # yReceiverMate3
        sample[6] = [request.form["rec5_xroute"]] # xReceiverMate4
        sample[7] = [request.form["rec5_yroute"]] # yReceiverMate4
        sample[8] = [request.form["rectar_xroute"]] # xcatchingReceiverRoute
        sample[9] = [request.form["rectar_yroute"]] # ycatchingReceiverRoute
        sample[10] = [request.form["down"]]
        sample[11] = [request.form["ytogo"]]
        sample[12] = [request.form["oformation"]]
        sample[13] = [request.form["definbox"]]
        sample[14] = [request.form["passrushers"]]
        sample[15] = [request.form["defensep"]]
        sample[16] = [request.form["offensep"]]
        
        sampledf = pd.DataFrame(sample)
        
        prediction = current_app.csmodel.predict(sampledf)
        
        return render_template('prediction_result.html', prediction = str(round(prediction[0], 1)), topbar = topbar, topbar_js = topbar_js)
    else:
        return render_template('catch_separation.html')

if __name__ == "__main__":
        app.run(debug=True)
