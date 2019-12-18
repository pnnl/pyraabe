#!/bin/bash

vmtkcenterlines -ifile $1 -seedselector openprofiles -endpoints 1 --pipe vmtkbranchextractor --pipe vmtkcenterlinemerge -ofile $2
