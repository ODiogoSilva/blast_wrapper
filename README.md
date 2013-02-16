
#### About blast.py

blast.py is a remote BLAST wrapper written in Python2.7 capable of running multiple parallel instances of remote BLAST searches

### Usage

blast.py has several options (see below) that allow you to costumize your BLAST searches. Here I will present just a few examples:

- blast.py -in INPUTFILE -o OUTPUTFILE_NAME

Here, the "-in" option is used to specify the FASTA input file name, and the "-o" option is used to specify the name of the BLAST output file.
By default, blast.py will run "blastn" on the "NR" database and the output will be in "XML" format. It will use an e-value threshold of "1" and will limit the number of best hits per search to "50". Seven parallel instances will be run, as in BLAST2GO. I do not advise you to use a larger number because it may causa overload of the remote servers, resulting in a severed connection.

- blast.py -in INPUTFILE -b blastp -db swissprot -o OUTPUTFILE_NAME

Here, I specified the "blastp" program and swissprot database, instead of the default "blastn" and "nr".

- blast.py -in INPUTFILE -b tblastn -e 1e-10 -o OUTPUTFILE_NAME

Here, I specified the "tblastn" program and an evalue cut off of 1e-10

#### When the connection is severed before time

Since this program depends on the good will of the NCBI servers, I also implemented a fail safe in case the connection is lost. When the program detects that the BLAST search was not completed for any reason, it will produce a new FASTA file (that will end with ".resume") containing the sequences that were not BLASTed yet. In this way, the user can resume the BLAST search from the last saved point, avoiding the inconveniance of having to start all over again and BLASTing sequences repeatedly.

Depending on you internet connection, this is not a common issue (happened only once in my tests), but I implemented this nevertheless, just to be on the safe side.

#### Options

blast.py has the following options (which can also be consulted by typing "blast.py -h" or "blast.py --help" in the command line):

  -h, --help            									**show this help message and exit**
  
  -in INFILE          										**Provide the FASTA input file name**
  
  -b {blastn,blastp,blastx,tblastn,tblastx}					**Select the BLAST program to run (default is 'blastn')**
                        
  -db DATABASE          									**Select the data base to run BLAST (default is 'nr')**
  
  -e EVALUE           										**The minimum e-value. Notation can be '0.001' or '1e-3'**
															**(default is '1')**
                        
  -hit HITLIST          									**The maximum number of hits per BLAST search (default**
															**is '50')**
                        
  -p PROC               									**The number of parallel instaces to run BLAST. Use with**
															**caution, as a number larger than 7 may cause the**
															**connection to be severed due to overload**
							
  -o OUTPUTFILE         									**Please provide the name of the output file**
  
  -outfmt {HTML,Text,ASN.1}									**Select the BLAST output format**
