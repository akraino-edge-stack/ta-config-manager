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
# Collection of logging variables and functions for the bootstrap.sh

set -o nounset

#
# Variables
#

LOG_BASE_DIR="${LOG_BASE_DIR:-/srv/deployment/log}"
BOOTSTRAP_LOG="${BOOTSTRAP_LOG:-${LOG_BASE_DIR}/bootstrap.log}"
CM_LOG=${LOG_BASE_DIR}/cm.log

#
# Create the log dir
#
mkdir -p ${LOG_BASE_DIR}

#
# Functions
#

function log()
{
    local priority=$1
    shift
    local message=$1

    local caller_function=""
    if [ -z ${FUNCNAME[2]+x} ]; then
        caller_function="${FUNCNAME[1]}"
    else
        caller_function="${FUNCNAME[2]}"
    fi

    echo "$(date) ($priority) ${caller_function} ${message}"
    echo "$(date) ($priority) ${caller_function} ${message}" >> $BOOTSTRAP_LOG
}

function log_info()
{
    log info "$@"
}

function log_error()
{
    log error "$@"
}

function log_installation_success()
{
    log_info "Installation complete, Installation Succeeded :)"
}

function log_installation_failure()
{
    log_error "Installation complete, Installation Failed :("
}
