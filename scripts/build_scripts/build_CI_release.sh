#!/bin/bash
SRC_DIR=$1
/projects/mpact/build-casl_release_830_newTPLs.sh $SRC_DIR -DFutility_ENABLE_DBC=ON -DMPACT_TEST_CATEGORIES=CONTINUOUS -DMPACT_WARN_ABOUT_MISSING_EXTERNAL_PACKAGES=TRUE
