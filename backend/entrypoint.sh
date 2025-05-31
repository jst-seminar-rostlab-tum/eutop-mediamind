#!/bin/sh
if [ -n "$APP_CONFIG_JSON" ]; then
  echo "$APP_CONFIG_JSON" | jq -r 'to_entries|map("export \(.key)=\"\(.value|tostring)\"")|.[]' > /tmp/app_env.sh
  . /tmp/app_env.sh
fi
exec "$@"