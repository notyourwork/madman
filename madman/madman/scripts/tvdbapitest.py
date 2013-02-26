#!/usr/bin/python

from thetvdbapi import TheTVDB

moo = TheTVDB('273A29FB654AC4D2')
showid = moo.get_matching_shows('House')[0][0]
print moo.get_show(showid).
