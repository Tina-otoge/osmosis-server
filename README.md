# osmosis-server

osmosis is an osu! server that entirely disregards combo and uses accuracy.

Live version: https://osmosis.tina.moe

To submit scores on osmosis, one must uses the osu! lazer fork
[osumosis](https://github.com/Tina-otoge/osumosis).

## Philosophy

Combo scoring is unfair and is a source of frustration for many players. I
often see people, including myself, consider a play ruined as soon as they
do a single miss, even though they were doing very great, and quit the song
immediately. This is not OK.  
Accuracy is a very good metric, misses are already properly punished by
lowering the accuracy a lot.

The pp system is too complex and hard to understand, there is also no sign
of it becoming simpler in the future. pp are an entire different way of
judging the quality of a play, and there is no way for a player to know if
a play values more pp than another without relying on third party tools,
because the way pp are calculated is very complex.  
This should not happen. This is only happening because they are admitting
that the score system they have does not judges the players efficiently.
They should fix the score not make another hidden score metric.  
osmosis' equivalent to pp, *osmos*, are highly predictible, as they are
only based on accuracy and the difficulty level of the chart.

The SR system provides good estimations but has shown too many examples of
excessively underevaluating or overevaluating some charts. On osmosis, we
use the SR has a base but review the difficulty level of each chart before
ranking it, making us able to manually fix cases where SR is incorrect.

Respecting artists and their rights is very important. osu!'s approach to
copyright is to let anything go, and remove the content afterwards if a
complaint is sent. This has created a quite bad image of osu! in some
communities, espcially in Japan. Some artists are very glad of their work
being popularized through osu!, but some are very angry about their songs
being used without permission, and don't want to be associated with osu!.
We operate the other way around, we only consider songs if the artists
explicitely said they are okay with their songs being used in osu! (or in
other non-commercial projects in some cases).

## Features

- Supports osu! lazer
- Per-chart leaderboard for every charts, including unsubmitted ones
- Global leaderboard using a global point system called *osmos*, analogous to osu!'s pp
- Charts difficulty level can be re-evaluated at any time, global leaderboard adjusts in real-time
- Ranked charts aren't the ones from the official osu! server but are hand-picked by our players
- Only songs by artists who explicitely agree with their works being used in osu! can be ranked
- Can generate scorecards from scores
- Sending links to scores in Discord will show an easy to understand summary of the score

## Contribute to ranking charts!

I'm not a very active player myself, you can recommend charts to rank directly on our
Discord server at https://discord.gg/xWKFDBu.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run
```
