#!/bin/bash

# Copyright 2019 Nokia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#
# Collection of variables and functions for the bootstrap.sh

set -o nounset

#
# Variables
#

CM_IP=127.0.0.1
CM_PORT=61100
CMCLI="/usr/local/bin/cmcli --ip $CM_IP --port $CM_PORT --client-lib cmframework.lib.cmclientimpl.CMClientImpl"
CM_ACTIVATORS=/opt/cmframework/activators
CM_PID=
CM_VALIDATORS=/opt/cmframework/validators
CM_INVENTORY_HANDLERS=/opt/cmframework/inventoryhandlers
DB_IP=127.0.0.1
DB_CHECK_CMD="/bin/redis-cli -h $DB_IP --scan --pattern '*'"
DB_PORT=6379
DB_STARTUP_CMD="/bin/redis-server ./redis.conf"
INVENTORY_FILE=/opt/cmframework/inventory.data
STATE_FILE=/etc/installation_state
USER_CONFIG_HANDLERS=/opt/cmframework/userconfighandlers

#
# Source log variables and functions
#
source $(dirname "${BASH_SOURCE[0]}")/log.sh

#
# Functions
#

function run_cmd()
{
    local result
    local ret
    log_info "Running $*"
    result=$(eval "$*" 2>&1)
    ret=$?
    if [ $ret -ne 0 ]; then
        log_error "Failed with error $result"
    else
        log_info "Command succeeded: $result"
    fi

    return $ret
}

function stop_process()
{
    local pid=$1
    log_info "Stopping process $pid"
    if ! [ -z $pid ]; then
        if [ -d /proc/$pid ]; then
            log_info "Shutting down process $pid gracefully"
            run_cmd "pkill -TERM -g $pid"
            log_info "Waiting for process $pid to exit"
            for ((i=0; i<10; i++)); do
                if ! [ -d /proc/$pid ]; then
                    log_info "Process $pid exited"
                    break
                fi
                log_info "Process $pid is still running"
                sleep 2
            done

            if [ -d /proc/$pid ]; then
                log_error "Process $pid is still running, forcefully shutting it down"
                run_cmd "pkill -KILL -g $pid"
            fi
        fi
    fi
}

function cleanup()
{
    log_info "Cleaning up"
    systemctl stop redis
    stop_process $CM_PID
    rm -f $INVENTORY_FILE
}

function start_db()
{
    log_info "Starting redis db using $DB_STARTUP_CMD"
    systemctl start redis
    log_info "Wait till DB is serving"
    local dbok
    dbok=0
    for ((i=0; i<10; i++)); do
        run_cmd "$DB_CHECK_CMD"
        dbok=$?
        if [ $dbok -eq 0 ]; then
            break
        fi
        log_info "DB still not running"
        sleep 2
    done

    return $dbok
}

function start_cm()
{
    rm -f "${STATE_FILE}"
    log_info "Starting CM server"
    setsid /usr/local/bin/cmserver --ip $CM_IP --port $CM_PORT \
        --backend-api cmframework.redisbackend.cmredisdb.CMRedisDB \
        --backend-uri redis://:@$DB_IP:$DB_PORT \
        --log-level debug \
        --validators $CM_VALIDATORS \
        --activators $CM_ACTIVATORS \
        --disable-remote-activation \
        --log-dest console \
        --log-level debug \
        --inventory-handlers $CM_INVENTORY_HANDLERS \
        --inventory-data $INVENTORY_FILE \
        --activationstate-handler-api cmframework.utils.cmdsshandler.CMDSSHandler \
        --activationstate-handler-uri /run/.dss-server \
        --alarmhandler-api cmframework.lib.cmalarmhandler_dummy.AlarmHandler_Dummy \
        --install-phase \
        --snapshot-handler-api cmframework.utils.cmdsshandler.CMDSSHandler \
        --snapshot-handler-uri /run/.dss-server \
        --verbose 2> "$CM_LOG" 1>&2 &
    export CM_PID=$!
    log_info "cmserver pid is $CM_PID"
    if ! [ -d /proc/$CM_PID ]; then
        log_error "CM server is not running!"
        log_info "Check redis.log and $BOOTSTRAP_LOG for details"
        return 1
    fi

    log_info "Wait till cmserver is ready to serve"
    local out
    while true; do
        out=$($CMCLI get-properties --matching-filter '.*' 2>&1)
        if [ $? -eq 0 ]; then
            break
        fi
        echo $out | grep "Not found" 2> /dev/null 1>&2
        if [ $? -eq 0 ]; then
            break
        fi
        log_info "cmserver not ready yet, got error $out"
        sleep 1
    done
    return 0
}

function handle_user_config()
{
    log_info "Handling user configuration from file $CONFIG_FILE"
    run_cmd "$CMCLI bootstrap --config $CONFIG_FILE --plugin_path $USER_CONFIG_HANDLERS"
    return $?
}

function start_installation()
{
    log_info "Start installation"
    handle_user_config
    return $?
}

function wait_installation_complete()
{
    log_info "Waiting for installation to complete"
    while true; do
        if [ -f $STATE_FILE ]; then
            log_info "installation completed"
            break
        fi
        sleep 5
    done
    local result
    result=$(cat $STATE_FILE)

    if [ "$result" == "success" ]; then
        log_info "exiting with success :)"
        return 0
    else
        log_error "exiting with failure :("
        return 1
    fi
}

function execute_post_install()
{
    log_info "Start post installation"
    return 0
}

function parameter_exists_in_list()
{
    local EXPECTED_PARAM=$1
    shift
    local PARAM_LIST=$*
    local PARAM
    for PARAM in ${PARAM_LIST}
    do
        if [ "${PARAM}" == "${EXPECTED_PARAM}" ]
        then
            return 0
        fi
    done
    return 1
}

function get_next_boot_args()
(
    GRUB_CMDLINE_LINUX=""
    GRUB_CMDLINE_LINUX_DEFAULT=""

    if source /etc/default/grub > /dev/null
    then
        echo "${GRUB_CMDLINE_LINUX} ${GRUB_CMDLINE_LINUX_DEFAULT}"
    fi
)

function get_current_boot_args()
{
    local CURRENT_BOOT_ARGS
    local CMDLINE_PATTERN='BOOT_IMAGE='
    CURRENT_BOOT_ARGS=$(grep ${CMDLINE_PATTERN} /proc/cmdline)
    CURRENT_BOOT_ARGS=${CURRENT_BOOT_ARGS#${CMDLINE_PATTERN}}
    CURRENT_BOOT_ARGS=${CURRENT_BOOT_ARGS#\"}
    CURRENT_BOOT_ARGS=${CURRENT_BOOT_ARGS%\"}
    echo "${CURRENT_BOOT_ARGS}"
}

function has_kernel_parameters_changed()
{
    local CURRENT_BOOT_ARGS
    CURRENT_BOOT_ARGS=$(get_current_boot_args)
    local NEXT_BOOT_ARG
    for NEXT_BOOT_ARG in $(get_next_boot_args)
    do
        if ! parameter_exists_in_list "${NEXT_BOOT_ARG}" "${CURRENT_BOOT_ARGS}"
        then
            log_info "kernel parameter <${NEXT_BOOT_ARG}> does not exist in [${CURRENT_BOOT_ARGS}]"
            return 0
        fi
    done
    return 1
}

function reboot_host()
{
    local DELAY=5
    log_info "Reboot the host in ${DELAY} seconds to apply the kernel parameter changes"
    sleep ${DELAY}
    systemctl reboot
}
