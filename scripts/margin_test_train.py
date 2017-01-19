#! /usr/bin/env python

import string
import getopt
import sys
import pickle
import os
import re


SEPARATOR = ':'

def usage():
	print 'Usage: margin_test_train.py    '
	print '\t--boost-info-test=filename  margins file as output by jboost (-a -2 switch)'
	print '\t--boost-info-train=filename  margins file as output by jboost (-a -2 switch)'
	print '\t--iteration=i,j,k,...  the iterations to inspect, no spaces between commas'


def process_margins(m_list, iters, filename):
	margin_list = []
	for i in range(len(iters)):
		scores = m_list[i]
		m = m_list[i]
		margins = m[:]
		margins.sort()
		margin_list.append(margins)

	lines = []
	margin_list_maxes = []
	for i in range(len(margin_list)):
		margins = margin_list[i]
		margin_list_maxes.append(max(margins))


	for w in range(len(margin_list[0])):
		line = ""
		line += str(float(w)/len(margin_list[0]))
		for i in range(len(margin_list)):
			margins = margin_list[i]
			marg_max = margin_list_maxes[i]
			line += ' '
			line += str(margins[w]/marg_max)
		line += ' \n' 
		lines.append(line)

	f= open(filename, 'w')
	f.writelines(lines)
	f.close()

	

def write_gnuplot(m_list_train, m_list_test, iters, datafile):

	process_margins(m_list_train, iters, 'margin_train.dat')
	process_margins(m_list_test, iters, 'margin_test.dat')

	epsoutlines = []
	epsoutlines.append('set terminal postscript eps enhanced color\n')
	epsoutlines.append('set output \'' + datafile + '.margin.eps\'\n')
	epsoutlines.append('set title "' + datafile + ' Margins" font "Times,20"\n')
	epsoutlines.append('set key left top\n')
	epsoutlines.append('set size 0.8, 0.8\n')
	epsoutlines.append('set xlabel "Margin" font "Times,20"\n')
	epsoutlines.append('set ylabel "Cumulative Distribution" font "Times,20"\n')
	out = ''
	out += 'plot '
	color = 1
	for i in range(len(iters)):
		out += ' "margin_train.dat" using ' + str(i+2) + ':1'
		out += ' title \'Train Iteration: ' + str(iters[i]) + '\' with lines'
		out += ' lt 3 lc ' + str(color) + ' lw 3 ,'
		color += 1
	color = 1
	for i in range(len(iters)):
		out += ' "margin_test.dat" using ' + str(i+2) + ':1'
		out += ' title \'Test Iteration: ' + str(iters[i]) + '\' with lines'
		out += ' lt 1 lc ' + str(color) + ' lw 1 ,'
		color += 1
	out = out[:-1]
	out += '\n'
	epsoutlines.append(out)
	
	epsfilename = datafile + '.margin.eps.gnuplot'

	f = open(epsfilename, 'w')
	f.writelines(epsoutlines)
	f.close()

	os.system('gnuplot ' + epsfilename)
	os.system('epstopdf ' + datafile + '.margin.eps')

def main():
    # Usage: see usage()
    # Looks at all the examples that have negative margins
    # the output can be used to find the examples that are probably mislabeled
    # and also the examples that might need more features

    try:
        opts, args= getopt.getopt(sys.argv[1:], '', ['boost-info-test=', 'boost-info-train=', 'iteration='])
    except getopt.GetoptError, inst:
        print 'Received an illegal argument:', inst
        usage()
        sys.exit(2)

    boostfile_test = boostfile_train = iteration = None
    for opt,arg in opts:
	    if (opt == '--boost-info-test'):
		    boostfile_test = arg
	    elif (opt == '--boost-info-train'):
		    boostfile_train = arg
	    elif (opt == '--iteration'):
		    iteration = arg
	
    if(boostfile_test == None or boostfile_train == None):
	    print 'Need .boosting.info files'
	    usage()
	    sys.exit(2)
        
    print 'Reading test boosting info'
    f= open(boostfile_test,'r')
    data_test = f.readlines()
    f.close()
    margin_elements_test = int((string.split(data_test[0],SEPARATOR))[1].split('=')[1])
 
    print 'Reading train boosting info'
    f= open(boostfile_train,'r')
    data_train = f.readlines()
    f.close()
    margin_elements_train = int((string.split(data_train[0],SEPARATOR))[1].split('=')[1])
    
    def get_margin(line):
	    m = line.split(SEPARATOR)[1]
	    m.replace(']','')
	    m.replace(';','')
	    m.replace(SEPARATOR,'')
	    m.replace(' ','')
	    m.replace('\t','')
	    return float(m)

    # if iterations are not specified on command line, we do the last iteration
    iters = [1]
    iters[0] = len(data_train) / (margin_elements_train+1)

    margin_list_train = []
    if (iteration != None):
	    iters = map(int, [x.strip() for x in iteration.split(',')])
	    for iter in iters:
		    lines = [x for x in data_train[iter*(margin_elements_train+1)+1:(iter+1)*(margin_elements_train+1)]]
		    
		    if len(lines) == 0:
			    print "Error: Missing data for some iterations. Make sure your .boosting.info is generated with -a -2 option."
			    exit(1)

		    margins = map(get_margin, lines)
		    margin_list_train.append(margins)
    else:
	    lines = [x for x in data_train[-margin_elements_train:]]
	    margins = map(get_margin, lines)
	    margin_list_train.append(margins)

    margin_list_test = []
    if (iteration != None):
	    iters = map(int, [x.strip() for x in iteration.split(',')])
	    for iter in iters:
		    lines = [x for x in data_test[iter*(margin_elements_test+1)+1:(iter+1)*(margin_elements_test+1)]]
		    
		    if len(lines) == 0:
			    print "Error: Missing data for some iterations. Make sure your .boosting.info is generated with -a -2 option."
			    exit(1)

		    margins = map(get_margin, lines)
		    margin_list_test.append(margins)
    else:
	    lines = [x for x in data_test[-margin_elements_test:]]
	    margins = map(get_margin, lines)
	    margin_list_test.append(margins)

    dataname = boostfile_train.split(".")[0]
    write_gnuplot(margin_list_train, margin_list_test, iters, dataname)
    

if __name__ == "__main__":
    main()
