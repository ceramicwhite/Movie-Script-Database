#!/bin/bash

# Set default values
RUN_GET_SCRIPTS=${RUN_GET_SCRIPTS:-"true"}
RUN_GET_METADATA=${RUN_GET_METADATA:-"true"}

# Update sources.json based on environment variables
for source in imsdb screenplays scriptsavant dailyscript awesomefilm sfy scriptslug actorpoint scriptpdf; do
    env_var="USE_${source^^}"
    env_value=${!env_var:-"true"}
    jq ".$source = \"$env_value\"" sources.json > temp.json && mv temp.json sources.json
done

# Run get_scripts.py if RUN_GET_SCRIPTS is true
if [ "$RUN_GET_SCRIPTS" = "true" ]; then
    python get_scripts.py
fi

# Run get_metadata.py if RUN_GET_METADATA is true
if [ "$RUN_GET_METADATA" = "true" ]; then
    python get_metadata.py
fi

# Keep the container running
tail -f /dev/null
