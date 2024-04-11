#!/bin/bash

sysctl vm.overcommit_memory=1

exec "$@"
