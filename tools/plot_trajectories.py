#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2007-2018 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    plotTrajectories.py
# @author  Jakob Erdmann
# @date    2018-08-18
# @version $Id$

"""
This script plots fcd data for each vehicle using either
- distance vs speed
- time vs speed
- time vs distance
"""
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from collections import defaultdict
from optparse import OptionParser
import matplotlib.pyplot as plt

from sumolib.xml import parse

def getOptions(args=None):
    optParser = OptionParser()
    optParser.add_option("-t", "--trajectory-type", dest="ttype", default="ds",
                         help="select one of ('ds','ts', 'td') for plotting distanceVsSpeed (default), timeVsSpeed, timeVsDistance")
    optParser.add_option("-s", "--show", action="store_true", default=False, help="show plot directly")
    optParser.add_option("-o", "--output", help="outputfile for saving plots", default="plot.png")
    optParser.add_option("--csv-output", dest="csv_output", help="write plot as csv", metavar="FILE")
    optParser.add_option("-b", "--ballistic", action="store_true", default=False, help="perform ballistic integration of distance")
    optParser.add_option("-v", "--verbose", action="store_true", default=False, help="tell me what you are doing")

    options, args = optParser.parse_args(args=args)
    if len(args) != 1:
        sys.exit("mandatory argument FCD_FILE missing")
    options.fcdfile = args[0]
    return options

def write_csv(data, fname):
    with open(fname, 'w') as f:
        for veh, vals in data.items():
            f.write('"%s"\n' % veh)
            for x in zip(*vals):
                f.write(" ".join(map(str, x)) + "\n")
            f.write('\n')

def main(options):
    plt.figure(figsize=(14, 9), dpi=100)

    xdata = 2
    ydata = 1
    if options.ttype == 'ds':
        plt.xlabel("Distance")
        plt.ylabel("Speed")
    elif options.ttype == 'ts':
        plt.xlabel("Time")
        plt.ylabel("Speed")
        xdata = 0
        ydata = 1
    elif options.ttype == 'td':
        plt.xlabel("Time")
        plt.ylabel("Distance")
        xdata = 0
        ydata = 2
    else:
        sys.exit("unsupported plot type '%s'" % options.ttype)

    data = defaultdict(lambda : ([], [], [])) # vehID -> (times, speeds, distances) 
    for timestep in parse(options.fcdfile, 'timestep'):
        if timestep.vehicle is None:
            continue
        for vehicle in timestep.vehicle:
            prevTime = 0
            prevSpeed = 0
            prevDist = 0
            time = float(timestep.time)
            speed = float(vehicle.speed)
            if vehicle.id in data:
                prevTime = data[vehicle.id][0][-1]
                prevSpeed = data[vehicle.id][1][-1]
                prevDist = data[vehicle.id][2][-1]
            data[vehicle.id][0].append(time)
            data[vehicle.id][1].append(speed)

            if options.ballistic:
                avgSpeed = (speed + prevSpeed) / 2
            else:
                avgSpeed = speed
            data[vehicle.id][2].append(prevDist + (time - prevTime) * avgSpeed)


    for d in data.values():
        plt.plot(d[xdata], d[ydata])

    plt.savefig(options.output)
    if options.csv_output is not None:
        write_csv(data, options.csv_output)
    if options.show:
        plt.show()

if __name__ == "__main__":
    main(getOptions())