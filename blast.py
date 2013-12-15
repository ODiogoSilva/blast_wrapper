#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  blast.py
#  
#  Copyright 2013 Diogo N Silva <diogo@arch>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  blast.py v1.1
#  Author: Diogo N Silva
#  Last update: 14/02/2013 

import os
import sys
import argparse
import itertools
from multiprocessing import Pool
import subprocess
from Bio.Blast import NCBIWWW


parser = argparse.ArgumentParser(description="Remote multiprocessing BLAST wrapper")

parser.add_argument("-in",dest="infile",required=True,help="Provide the FASTA input file name")
parser.add_argument("-b",dest="blast_prog",default="blastn",choices=["blastn","blastp","blastx","tblastn","tblastx"],help="Select the BLAST program to run (default is '%(default)s')")
parser.add_argument("-db",dest="database",default="nr",help="Select the data base to run BLAST (default is '%(default)s')")
parser.add_argument("-e",dest="evalue",default=1,type=str,help="The minimum e-value. Notation can be '0.001' or '1e-3' (default is '%(default)s')")
parser.add_argument("-hit",dest="hitlist",default=50,type=int,help="The maximum number of hits per BLAST search (default is '%(default)s')")
parser.add_argument("-p",dest="proc",default=7,type=int,help="The number of parallel instaces to run BLAST. Use with caution, as a number larger than 7 may cause the connection to be severed due to overload")
parser.add_argument("-o",dest="outputfile",required=True,help="Please provide the name of the output file")
parser.add_argument("-outfmt",dest="output_format",default="XML",choices=["HTML","Text","ASN.1","XML"],help="Select the BLAST output format")

arg = parser.parse_args()

def loading (current_state,size,prefix,width):
	""" Function that prints the loading progress of the script """
	percentage = ((float(current_state)+1)/float(size))*100.0
	complete = float(width*percentage*0.01)
	if percentage == 100:
		sys.stdout.write("\r%s [%s%s] %s%% -- Done!\n" % (prefix,"#"*int(complete),"."*(int(width-complete)),int(percentage)))
	else:
		sys.stdout.write("\r%s [%s%s] %s%%" % (prefix,"#"*int(complete),"."*(int(width-complete)),int(percentage)))
	sys.stdout.flush()


def read_file (infile):
	""" Function that parses a FASTA formated file and returns a dictionary """
	sequences_storage = {}
	sequences_order = []
	file_handle = open(infile)
	for line in file_handle:
		if line.startswith(">"):
			name = line.strip()[1:]
			sequences_storage[name] = ""
			sequences_order.append(name)
		else:
			sequences_storage[name] += line.strip()
	sequences_list = [(k,sequences_storage[k]) for k in sequences_order]
	file_handle.close()
	return sequences_list
	
def subset_creator (sequences_dic, proc=7):
	""" Function that breaks the original sequence dictionary in smaller subsets that will be run in parallel """
	subset_num = len(sequences_dic)/int(proc)
	subset_rest = len(sequences_dic)%int(proc)
	subset_list, counter, dif = [], 0, int(proc)
	for i in range(subset_num):
		subset_list.append(sequences_dic[counter:int(proc)])
		counter += dif
		proc += dif
	else:
		subset_list.append(sequences_dic[counter:counter+subset_rest])
	return subset_list	

def blast (arguments):
	""" Worker function that executes the WWWNCBI blast """
	# Gathering arguments
	blast_program = arguments[0]
	name,seq = arguments[1]
	database = arguments[2]
	evalue = arguments[3]
	hitlist = arguments[4]
	output_num = arguments[5]
	output_format = arguments[6]
	
	# Executing BLAST
	save_file = open("blast_out_%s_%s" % (output_file,output_num)  ,"a")
	result_handle = NCBIWWW.qblast(blast_program, database, ">%s\n%s" % (name, seq), expect=evalue, hitlist_size=hitlist, format_type=output_format)
	save_file.write(result_handle.read())
	save_file.close()
	
def output_merge (output_name):
	""" Function that merge the individual output blast searches into a single file """
	subprocess.Popen(["cat blast_out_%s_* >> %s" % (output_file,output_name)],shell=True).wait()
	subprocess.Popen(["rm blast_out_%s_*" % (output_file)],shell=True).wait()

def output_check (output_name):
	""" Function that checks if the output file name is already present in the current directory """
	if os.path.exists(output_name):
		condition = raw_input("The file %s already exists.\n\nDo you really really want to proceed? Oh! Oh! Oh! (y/n): " % output_name)
		if condition == "y":
			pass
		elif condition == "n":
			sys.exit("Exiting")
		else:
			sys.exit("Option %s not recognized. Exiting!\n" % condition)				


def main(input_f):
	input_file = input_f
	blast_program = arg.blast_prog
	blast_database = arg.database
	evalue = arg.evalue
	hitlist = arg.hitlist
	proc_number = arg.proc
	output_file = arg.outputfile
	output_format = arg.output_format
	
	# Parsing and organizing data set
	fasta_list = read_file (input_file)
	fasta_backup = fasta_list[:] # Creating list copy for backup purposes
	
	if proc_number == 1:
		
		for fasta_element in fasta_list:
			loading(fasta_list.index(fasta_element), len(fasta_list), "BLASTing... ", 50)
			
			try:
				blast([blast_program, fasta_element, blast_database, evalue, hitlist, output_file, output_format])
			except:
				continue
			
			fasta_backup = fasta_backup[fasta_list.index(fasta_element):]
		
	else:
	
		# Creating process pool and running remote BLAST
		fasta_subset = subset_creator(fasta_list,proc=proc_number)
		
		for subset in fasta_subset:
			loading(fasta_subset.index(subset),len(fasta_subset),"BLASTing... ",50)
			try:
				map(blast, itertools.izip(itertools.repeat(blast_program),
											subset,
											itertools.repeat(blast_database),
											itertools.repeat(evalue),
											itertools.repeat(hitlist),
											range(proc_number),
											itertools.repeat(output_format)))
			except:
				continue
			fasta_backup = fasta_backup[proc_number:]
		else:
			output_merge (output_file)
	
	return fasta_backup


def backup (input_file, backup_list):
	""" Function that writes the remaining sequences to a new file so that the blast search can resume """
	# Check if previous resume file exists
	if os.path.exists(input_file+".resume"):
		subprocess.Popen(["rm %s" % input_file+".resume"],shell=True).wait()
		
	output_file = open(input_file+".resume","w")
	for name,seq in backup_list:
		output_file.write(">%s\n%s\n" % (name,seq))
	output_file.close()
	return 0

if __name__ == '__main__':
	# Checking if output file already exists
	input_file = arg.infile
	output_file = arg.outputfile
	
	output_check (output_file)
	
	dump = main(input_file)
	while dump != []:
		print ("Restarting...")
		backup(arg.infile,dump)
		dump = main(input_file)
