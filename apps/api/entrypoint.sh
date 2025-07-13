#!/bin/sh
if [ -n "$APP_CONFIG_JSON" ]; then
  echo "$APP_CONFIG_JSON" | jq -r '
    to_entries
    | map("export \(.key)=" + (
        if ( ( .value | type ) == "string" )
        then @sh "\(.value)"
        else .value | tojson | @sh
        end
      )
    )
    | .[]
  ' > /tmp/app_env.sh
  . /tmp/app_env.sh
fi
exec "$@"