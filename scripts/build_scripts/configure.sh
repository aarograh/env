#!/bin/bash
source /opt/casl-tools/gcc-4.8.3/load_dev_env.sh

PROC=8

while getopts ":j:" opt; do
  case $opt in
    j)
      PROC=$OPTARG;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

shift $((OPTIND-1))
SRC_DIR=$1

rm -rf *
/projects/mpact/build-casl_release.sh $SRC_DIR -DMPACT_TEST_CATEGORIES=HEAVY
