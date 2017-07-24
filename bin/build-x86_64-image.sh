#!/bin/bash

BIN="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
exec "$BIN"/build_image cloud
