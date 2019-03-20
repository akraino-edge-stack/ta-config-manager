#! /bin/bash

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

DB_PORT=6379
DB_IP=127.0.0.1
LOG_BASE_DIR=/srv/deployment/log
DB_LOG=${LOG_BASE_DIR}/redis.log

CM_PORT=61100
CM_IP=127.0.0.1
CM_VALIDATORS=/opt/cmframework/validators
CM_ACTIVATORS=/opt/cmframework/activators
CM_LOG=${LOG_BASE_DIR}/cm.log
USER_CONFIG_HANDLERS=/opt/cmframework/userconfighandlers
INVENTORY_HANDLERS=/opt/cmframework/inventoryhandlers
INVENTORY_DATA=/opt/cmframework/inventory.data


BOOTSTRAP_LOG=${LOG_BASE_DIR}/bootstrap.log

DB_STARTUP_CMD="/bin/redis-server ./redis.conf"
DB_CHECK_CMD="/bin/redis-cli -h $DB_IP --scan --pattern '*'"
CMCLI="/usr/local/bin/cmcli --ip $CM_IP --port $CM_PORT --client-lib cmframework.lib.cmclientimpl.CMClientImpl"
USERCONFIG=

export CONFIG_PHASE="bootstrapping"

DB_PID=
CM_PID=

function log()
{
    priority=$1

    echo "$(date) ($priority) ${FUNCNAME[2]} ${@:2}"
    echo "$(date) ($priority) ${FUNCNAME[2]} ${@:2}" >> $BOOTSTRAP_LOG
}

function log_info()
{
    log info $@
}

function log_error()
{
    log error $@
}


function run_cmd()
{
    log_info "Running $@"
    result=$(eval $@ 2>&1)
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
    pid=$1
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
    #stop_process $DB_PID
    systemctl stop redis
    stop_process $CM_PID
}

function start_db()
{
    log_info "Starting redis db using $DB_STARTUP_CMD"
    #setsid $DB_STARTUP_CMD &
    #export DB_PID=$!
    #log_info "DB pid is $DB_PID"
    #if ! [ -d /proc/$DB_PID ]; then
    #    log_error "DB is not running!"
    #    log_info "Check /var/log/redis.log and $BOOTSTRAP_LOG for details"
    #    return 1
    #fi
    systemctl start redis
    log_info "Wait till DB is serving"
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
    log_info "Starting CM server"
    setsid /usr/local/bin/cmserver --ip $CM_IP --port $CM_PORT --backend-api cmframework.redisbackend.cmredisdb.CMRedisDB --backend-uri redis://:@$DB_IP:$DB_PORT --activationstate-handler-api cmframework.utils.cmstatedummyhandler.CMStateDummyHandler --activationstate-handler-uri dummy_uri --snapshot-handler-api cmframework.utils.cmstatedummyhandler.CMStateDummyHandler --alarmhandler-api cmframework.lib.cmalarmhandler_dummy.AlarmHandler_Dummy --snapshot-handler-uri dummy_uri --inventory-handlers $INVENTORY_HANDLERS --inventory-data $INVENTORY_DATA --validators $CM_VALIDATORS --activators $CM_ACTIVATORS --disable-remote-activation --log-dest console --log-level debug --verbose 2> $CM_LOG 1>&2 &
    export CM_PID=$!
    log_info "cmserver pid is $CM_PID"
    if ! [ -d /proc/$CM_PID ]; then
        log_error "CM server is not running!"
        log_info "Check redis.log and $BOOTSTRATP_LOG for details"
        return 1
    fi
    return 0
}

function handle_user_config()
{
    log_info "Handling user configuration from file $USER_CONFIG"
    run_cmd "$CMCLI bootstrap --config $USER_CONFIG --plugin_path $USER_CONFIG_HANDLERS"
    return $?
}

function main()
{
    # start the database
    start_db
    if [ $? -ne 0 ]; then
        cleanup
        return 1
    fi
   
    # start the configuration management server
    start_cm
    if [ $? -ne 0 ]; then
        cleanup
        return 1
    fi

    echo "============"
    jobs -p

    echo "Use CLI $CMCLI"

    while [ 1 ]; do
        read -n1 -r -p "Press space to exit..." key

        if [ "$key" = '' ]; then
            echo "exiting..."
            break
        fi
    done

    cleanup
    return 0
}

if [ $# -ne 1 ]; then
    echo "Usage:$0 <cmserver ip>"
    exit 1
fi

CM_IP=$1
CMCLI="/usr/local/bin/cmcli --ip $CM_IP --port $CM_PORT --client-lib cmframework.lib.cmclientimpl.CMClientImpl"
mkdir -p ${LOG_BASE_DIR}

main
