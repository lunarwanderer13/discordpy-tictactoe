#!/usr/bin/env bash

cd "$(dirname "$0")" || exit 1

nohup ./discordpy-tictactoe.sh >/dev/null 2>&1 &

