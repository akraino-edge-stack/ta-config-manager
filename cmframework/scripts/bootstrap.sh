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

COMMAND=$(basename "${0}")
DO_REBOOT_IF_NEEDED=true

#
# Source log variables and functions
#
source $(dirname "${BASH_SOURCE[0]}")/log.sh

function source_common()
{
    local SCRIPT_PATH
    SCRIPT_PATH=$(dirname "${BASH_SOURCE[0]}")
    local COMMON_SH_FILE=${SCRIPT_PATH}/common.sh
    # shellcheck disable=SC1091
    # shellcheck source=.
    source "${COMMON_SH_FILE}" && return 0
    log_error "Failed to source ${COMMON_SH_FILE}"
    return 1
}

export CONFIG_PHASE="bootstrapping"

function main()
{
    log_info "Bootstrapping started"

    declare -a FUNCTIONS=(source_common start_db start_cm start_installation)
    local func
    for func in "${FUNCTIONS[@]}"
    do
        if ! ${func}
        then
            cleanup
            return 1
        fi
    done

    local rc
    wait_installation_complete
    rc=$?

    if [ $rc -eq 0 ]; then
        export CONFIG_PHASE="postconfig"
        log_info "Generate inventory file to prepare for extra playbooks run"
        run_cmd "$CMCLI ansible-inventory > $INVENTORY_FILE"

        admin="x"
        for d in $(ls -d /home/*); do 
            if [ -f "$d/openrc" ]; then
                admin=$(basename "$d")
                break
            fi
        done

        #take a copy of the initial configuration data
        mkdir /root/.initconfig
        cp /var/lib/redis/dump.rdb /root/.initconfig/

        su - "$admin" -c "/usr/local/bin/openstack-ansible -b -u $admin /opt/openstack-ansible/playbooks/finalize-playbook.yml" &>> $BOOTSTRAP_LOG
        rc=$?

        if [ $rc -eq 0 ]; then
            execute_post_install
            rc=$?
        fi

    fi

    cleanup

    log_info "starting redis again"
    systemctl start redis

    if [ $rc -eq 0 ]; then
        if has_kernel_parameters_changed;
        then
            # The status of the installation will be logged by one of the following services after the host is rebooted.
            #
            # 1) finalize-bootstrap.service: When the performance porfile is enabled on the controller-1 and
            # the network type is "ovs"
            # 2) enable-dpdk.service: When the performance profile is enabled on the controller-1 and the
            # network type is "ovs-dpdk"
            #
            if [ ${DO_REBOOT_IF_NEEDED} == true ]; then
                reboot_host
            else
                log_info "Rebooting of host is skipped as requested."
            fi
        else
            log_installation_success
        fi
    else
        log_installation_failure
    fi

    return $rc
}

function show_help()
{
    echo "Usage:"
    echo "# ${COMMAND} <full path to user-config-yaml|restore-config-yaml>"
    echo "Or to skip the controller-1 reboot in the case kernel boot parameters are changed"
    echo "# ${COMMAND} <full path to user-config-yaml|restore-config-yaml> (--install | --restore) --no-reboot"
}

#
# Assume that the first argument is the configuration file to maintain backwards compatibility
# so handle it separately.
#

if [ $# -lt 1 ]; then
    show_help
    exit 1
else
    CONFIG_FILE=$1
    shift
fi

if ! [ -f "${CONFIG_FILE}" ]; then
    log_error "Failed to open file:${CONFIG_FILE}"
    show_help
    exit 1
fi


#
# And then the remaing arguments in any order
#

IS_INSTALL_ARG_SPECIFIED=false
for arg in "$@"
do
    case ${arg} in
        --no-reboot)
            DO_REBOOT_IF_NEEDED=false
            shift
        ;;
        --install)
            IS_INSTALL_ARG_SPECIFIED=true
            shift
        ;;
        --help)
            show_help
            exit 0
        ;;
        *)
            log_error "Unknown option: ${arg}"
            show_help
            exit 1
        ;;
    esac
done

log_info "====================================================================="
log_info "Boot strapping the environment with $CONFIG_FILE"
log_info "====================================================================="

main
