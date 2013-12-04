#!/usr/bin/env python

import json
import urllib2
import logging
import sys
import time

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
        self.finalMatchList = []

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
        last_week = int(round(time.time() - 604800))
        for match in self.matchesDetails:
            if self.matchesDetails[match['start_time']] < last_week:
                self.matchesList.append(match)
        if len(self.matchesList) > 5:
            print "limitting to 5 matches. %s matches found in the last week" % len(self.matchesList)
            self.finalMatchList = self.matchesList[:5]
        else:
            self.finalMatchList = self.matchesList


    def _getMatchReplay(self):
        """Download the replay for the match"""
        log.debug('in dotaPlayer._getMatchReplay()')

        for match in self.matchesList:
            log.debug('opening url: https://rjackson.me/tools/matchurls?matchid=%s' % match)
            download_link = urllib2.urlopen('https://rjackson.me/tools/matchurls?matchid=%s' % match)
            print download_link
            raw_input()


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
