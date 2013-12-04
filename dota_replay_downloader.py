#!/usr/bin/env python

import json
import urllib2
import logging
import sys

logging.basicConfig(level=logging.WARN,
    format='%(asctime)s %(levelname)s - %(message)s',
    datefmt='%y.%m.%d %H:%M:%S')
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger("dota_replay_downloader").addHandler(console)
log = logging.getLogger("dota_replay_downloader")


class dotaPlayer(object):
    """Dota player object"""
    log.debug('in class dotaPlayer()')

    def __init__(self, steamAPIKey, userID):
        """Initialize dotaPlayer object"""
        log.debug('in dotaPlayer.__init__(%s, %s)' % (steamAPIKey, userID))

        self.steamAPIKey = steamAPIKey
        self.userID = userID
        self.matchesDetails = {}
        self.matchesList = []

    def _getMatchHistory(self):
        """Given get the match history for <userID>. <userID> is expected to be a
        string (almost certainly in the form of X:XXXXX"""
        log.debug('in dotaPlayer._getMatchHistory()')

        log.debug('opening url: https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v001/?key=%s&account_id=%s' % (self.steamAPIKey, self.userID))
        matchHistoryJSON = urllib2.urlopen(
                "https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v001/?key=%s&account_id=%s" % (self.steamAPIKey, self.userID))
        matchHistoryDict = json.loads(matchHistoryJSON.read())
        for i in matchHistoryDict['result']['matches']:
            self.matchesDetails[i['match_id']] = { 
                    'start_time' : i['start_time'],
                    'cluster' : ''}


    def _getMatchDetails(self):
        """Get the cluster details for the match, so we can download the replay"""
        log.debug('in dota_Player._getMatchDetails()')

        matchList = []
        for match in self.matchesDetails:
            matchList.append(match)
        matchDetails = {}
        if len(matchList) > 5:
            print "Limitting to only 5 matches. %i matches were found" % len(matchList)
            matchList = matchList[:5]

        for matchID in matchList:
            log.debug('opening url: https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v001/?key=%s&match_id=%s' % (self.steamAPIKey, matchID))
            matchDetailsJSON = urllib2.urlopen("https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v001/?key=%s&match_id=%s" % (self.steamAPIKey, matchID))
            matchDetailsDict = json.loads(matchDetailsJSON.read())
            self.matchesDetails[matchID]['cluster'] = matchDetailsDict['result']['cluster']


    def _getMatchReplay(self):
        """Download the replay for the match"""
        log.debug('in dotaPlayer._getMatchReplay()')

        for match in self.matchesDetails:
            log.debug('opening url: https://rjackson.me/tools/matchurls?matchid=%s' % match)
            urllib2.urlopen('https://rjackson.me/tools/matchurls?matchid=%s' % match)


if __name__ == "__main__":
    import argparse

    cmd_parser = argparse.ArgumentParser(description='Does something neat with the Dota 2 API')
    cmd_parser.add_argument(
        '-i',
        '--steamID',
        dest='steamID',
        type=str,
        action='store',
        #to find your steamID, check http://steamidfinder.com/
        default='0:42440556',
        help='32 or 64-bit steam ID')
    cmd_parser.add_argument(
        '-a',
        '--apikey',
        dest='steamAPIKey',
        type=str,
        action='store',
        default='',
        help='YOUR steam API key')
    cmd_parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='Enable debugging during execution')
    args = cmd_parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    player = dotaPlayer(args.steamAPIKey, args.steamID)
    player._getMatchHistory()
    player._getMatchDetails()
    player._getMatchReplay()
