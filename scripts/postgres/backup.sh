#!/usr/bin/env bash

#set -o errexit # if any command fails any reason, script fails
set -o pipefail # if none of of your pipecommand fails, exit fails
set -o nounset # if none of variables set, exit

working_dir="$(dirname ${0})"

source "${working_dir}/../../.envs/.prod"
source "${working_dir}/_sourced/messages.sh"

message_welcome "Backing up the '${POSTGRES_DB}' database..."

export PGHOST="${POSTGRES_HOST}"
export PGPORT="${POSTGRES_PORT}"
export PGUSER="${POSTGRES_USER}"
export PGPASSWORD="${POSTGRES_PASSWORD}"
export PGDATABASE="${POSTGRES_DB}"

backup_last="backup_last"

mkdir static/backups
cd static/backups || exit
pg_dump -Fc > "${backup_last}" || exit
message_success "'${POSTGRES_DB}' database made backup to 'static/backups/${backup_last}'"
