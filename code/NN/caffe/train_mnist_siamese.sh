#!/usr/bin/env sh

TOOLS=~/caffe/build/tools

$TOOLS/caffe train --solver=mnist_siamese_solver.prototxt
