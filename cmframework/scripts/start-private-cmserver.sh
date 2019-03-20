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

:'
This script can be used to start a private cmserver to test your CM userconfighandler and/or validator plugins.

To test userconfighandlers and installation time validators do the following:
- Copy your userconfighandler to a target system under /opt/cmframework/userconfighandlers/ directory.

- Copy your validator to a target system under /opt/cmframework/validators directory.

- Start a private cmserver
  ./start-private-cmserver.sh <some port number> no-cm-data
  
- The above command will print information about the temporary directory used for the private cmserver, it will also print the command to be used to access the cmserver e.g. the output can look like:

=======================================================================================================================
Use CLI /opt/bin/cmcli --ip 127.0.0.1 --port 51110
Root DIR /tmp/tmp.HcyehIQQoQ
=======================================================================================================================

- Test your plugins by running the following command:
  /opt/bin/cmcli --ip 127.0.0.1 --port <port> bootstrap --config /opt/userconfig/user_config.yaml --plugin_path /<cmserver root>/opt/cmframework/userconfighandlers

- If the above succeeds then your userconfighandler and validator are working properly. You can view the configuration data by running the following command:
  /opt/bin/cmcli --ip 127.0.0.1 --port <port> get-properties --matching-filter '.*'
  
To test run-time validation do the following:
- Copy your validator to a target system under /opt/cmframework/validators directory.

- Start a private cmserver
  ./start-private-cmserver.sh <some port number> no-cm-data
  
- The above command will print information about the temporary directory used for the private cmserver, it will also print the command to be used to access the cmserver e.g. the output can look like:

=======================================================================================================================
Use CLI /opt/bin/cmcli --ip 127.0.0.1 --port 51110
Root DIR /tmp/tmp.HcyehIQQoQ
=======================================================================================================================

- Test your plugins by changing the configuration by running the following command:
  /opt/bin/cmcli --ip 127.0.0.1 --port <port> set-property --property NAME VALUE

- If the above succeeds then your validator is working properly. You can view the configuration data by running the following command:
  /opt/bin/cmcli --ip 127.0.0.1 --port <port> get-properties --matching-filter '.*'
'

CM_PORT=
CM_IP=127.0.0.1
NO_CM_DATA=0
ROOT_DIR=$(mktemp -d)
CM_VALIDATORS=$ROOT_DIR/opt/cmframework/validators
CM_ACTIVATORS=$ROOT_DIR/opt/cmframework/activators
CM_LOG=$ROOT_DIR/var/log/cm.log
USER_CONFIG_HANDLERS=$ROOT_DIR/opt/cmframework/userconfighandlers
INVENTORY_HANDLERS=$ROOT_DIR/opt/cmframework/inventoryhandlers
INVENTORY_DATA=$ROOT_DIR/inventory.data

LOG_FILE=$ROOT_DIR/var/log/cm.log

DB_DIR=$ROOT_DIR/db
DB_FILE=$DB_DIR/db

CMCLI="/usr/local/bin/cmcli --ip $CM_IP --port $CM_PORT"
ENV_FILE=$ROOT_DIR/

export CONFIG_PHASE="bootstrapping"

CM_PID=


function log()
{
    priority=$1

    echo "$(date) ($priority) ${FUNCNAME[2]} ${@:2}"
    echo "$(date) ($priority) ${FUNCNAME[2]} ${@:2}" >> $LOG_FILE
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

function prepare_environment()
{
    mkdir -p $(dirname $CM_LOG)
    log_info "Creating directories under $ROOT_DIR"
    run_cmd "mkdir -p $USER_CONFIG_HANDLERS"
    run_cmd "mkdir -p $INVENTORY_HANDLERS"
    run_cmd "mkdir -p $CM_VALIDATORS"
    run_cmd "mkdir -p $CM_ACTIVATORS"
    run_cmd "mkdir -p $DB_DIR"

    log_info "Copying inventory handlers and user config handlers to $ROOT_DIR"
    cp -f /opt/cmframework/userconfighandlers/* $USER_CONFIG_HANDLERS/
    cp -f /opt/cmframework/inventoryhandlers/* $INVENTORY_HANDLERS/
    cp -f /opt/cmframework/validators/* $CM_VALIDATORS/

    if [ $NO_CM_DATA -eq 0 ]; then
        log_info "Generating DB file under $DB_FILE"
        /usr/local/bin/cmcli get-properties --matching-filter '.*' > $DB_FILE
    fi
    return $?
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
    stop_process $CM_PID
    rm -rf $ROOT_DIR
}

function start_cm()
{
    log_info "Starting CM server $CM_IP $CM_PORT $CM_LOG"
    extra_args=""
    if [ $NO_CM_DATA -eq 1 ]; then
        extra_args="--install-phase"
    fi
    setsid /usr/local/bin/cmserver --ip $CM_IP --port $CM_PORT --backend-api cmframework.filebackend.cmfilebackend.CMFileBackend --backend-uri $DB_FILE --activationstate-handler-api cmframework.utils.cmstatedummyhandler.CMStateDummyHandler --activationstate-handler-uri dummy_uri --alarmhandler-api cmframework.lib.cmalarmhandler_dummy.AlarmHandler_Dummy --snapshot-handler-api cmframework.utils.cmstatedummyhandler.CMStateDummyHandler --snapshot-handler-uri dummy_uri --inventory-handlers $INVENTORY_HANDLERS --inventory-data $INVENTORY_DATA --validators $CM_VALIDATORS --activators $CM_ACTIVATORS --disable-remote-activation --log-dest console --log-level debug --verbose $extra_args 2> $CM_LOG 1>&2 &
    export CM_PID=$!
    log_info "cmserver pid is $CM_PID"
    if ! [ -d /proc/$CM_PID ]; then
        log_error "CM server is not running!"
        log_info "Check $CM_LOG for details"
        return 1
    fi
    return 0
}

function main()
{
    # prapare private environment
    prepare_environment
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

    jobs -p

    echo ""
    echo ""
    echo "======================================================================================================================="
    echo "Use CLI $CMCLI"
    echo "Root DIR $ROOT_DIR"
    echo "======================================================================================================================="
    echo ""
    echo ""
    while [ 1 ]; do
        read -n1 -r -p "Press 'q' space to exit..." key

        if [ "$key" = 'q' ]; then
            echo "exiting..."
            break
        fi
    done

    cleanup
    return 0
}

if [ $# -lt 1 ]; then
    echo "Usage:$0 <cmserver port> [no-cm-data]"
    exit 1
fi

CM_PORT=$1
shift 1

for arg in "$@"; do
    if [ "$arg" == "no-cm-data" ]; then
        NO_CM_DATA=1
    else
        CONFIG_PHASE=$arg
    fi
done

CMCLI="/usr/local/bin/cmcli --ip $CM_IP --port $CM_PORT"

main
