LOG ANALYZER FOR CLOUDS v2.1
============================


INTRODUCTION
============

We are developing an open source code that allows to analyze the log
files from eucalyptus and displays the results in a convenient
graphical user interface.

Shell to analyze data
---------------------

Our framework is build around analyzing data from various
production clouds and uploading this data into a database.  We have
several mechanisms to deal with the data. First, we can create summary
of the data and can export in a variety of formats. This summary is 
especially important for administrators who like to find out what is 
happening on their clouds, but also for users to see with who they 
compete for resources. The outout format includes png,
googlecharts, and cvs tables. Second, we provide a simpel php
framework that displayse the information in some web pages.

However, as part of our analyzis we are also developing an interactive
shell that can be used to query data directly from our database.

As part of our source code and in this manual we included some simple 
examples so you can test this interface out and explore the data you may have gathered. 

Example: Create a summary table for the month of January
--------------------------------------------------------
The following will create a table with data produced for the month of January

    > fg-metric
    fg> clear users
    fg> analyze -M 01
    fg> table --type users --seperator ,  --caption Testing_the_csv_table
    fg> quit

Naturally you could store this script in a file and pipe to fg-metric
in case you have more complex or repetitive analysis to do. 

Example: How to create a summary analysis for multiple month
------------------------------------------------------------

Assume you like to create a nice html page directory with the analysis
of the data contained. This can be done as follows. Assume the following 
contents is in the file analyze.txt

    clear users
    analyze -M 01 -Y 2012
    createreport -d 2012-01 -t Running_instances_per_user_of_Eucalyptus_in_India
    
    clear users
    analyze -M 02 -Y 2012
    createreport -d 2012-01 -t Running_instances_per_user_of_Eucalyptus_in_India
  
    createreports 2012-01 2012-02

This page creates a beautiful report page with links to the genrated
graphs contained in the directories specified. All index files in
the directories are printed before the images in the derectory are
included. The resulting report is an html report.

To start the script, simply use

    > cat analyze.txt | fg-metric

This will produce a nice directory tree with all the data needed for a
display.

Eucalyptus 2.0 Data Integration
-------------------------------

To achieve analysis of eucalyptus data, we are using 'cc.log'
files. The needed information must be gathered while eucalyptus runs
in 'EUCADEBUG' mode.

We assume the following directory layout

    ./futurgrid/
    ./futurgrid/bin - includes all commands needed to run the log analyzing
    ./futurgrid/lib - includes libraries that may be called from the bin files
    ./futurgrid/etc - location of configuration files
    ./futurgrid/www - location of the www files
    
    
### Eucalyptus data gathering

Euaclyptus provides a supsantial set of log information. The information is typically stored in the eucalyptus log directory
Typically it is also confu=igured by the system administartor with log rotation. THis naturally would mean that the information is lost after a time period specified by the log rotation configuration. There are
two mechanisms of avoiding this. The first method is to cahnge the eucalyptus configuartion files in order to disable log rotation. However this has the disadvantage that the directories may fill up and eucalyptus runs out of space. 
How to disable Eucalyptus log rotation is discussed in the manaula at ... .
However we decided to go another route, buy copying the Eucalyptsu log files after a particular period of time and place them onto our analysis server and also a backup server. To set this mechanism up, a Eucalyptus system administrator
simply can insatall our tools in a predefined directory and call a command that copies the log files. Idially This is integrated into a cron script so that the process is done on regular basis.

Here is how you set this up

    pip install ....
    
This will install several commands in the bin directory. Make sure that it is in your path

Now you can call the command

   [fg-euca-gather-log-files](./man/fg-euca-gather-log-files.md)
   
which will copy all logfiles  that has not yet been copied into our backup directory. The log files have a numerical value from 1 to 9 as a postfix
Once this is done, our analysis scripts can be called from the commandline or a web page to create information about usage and utilization.

To see more information ablout this command, please visit the manual page [fg-euca-gather-log-files](./man/fg-euca-gather-log-files.md)



TODO
----

define variables

    FG_LOG_ANALYZER_WWW_OUTPUT - location where the www files for display are stored
    FG_TMP - location where temporary files are located that are analyzed
    FG_DATA - location where the permanent data is being stored 
    FG_HOME_LOG_ANALYZER - is set to the location of the "futuregrid" directory.
    EUCALYPTUS_LOG_DIR - location where the eucalyptus log dirs are stored

We recommend that the FutureGrid directory is included in the PATH of
the shell that will run the commands.

INSTALLATION
============

### Instalation from pypi 

The programs are distributed in [pypi](xyz). It contains our current release version of the software. 






### Installation form the source in github

If you are adventerus, you can work with our newests code checked into github. To obtain this code, please conduct the following steps.
We assume you have root priveledges to execute "make force"

    > wget https://github.com/futuregrid/futuregrid-cloud-metrics/tarball/v2.1.1
    > tar xvzf v2.1.1
    > cd futuregrid-futuregrid-cloud-metrics-4635fc9
    > make force 
    
This will install the programs in 

    /usr/bin/
    
### What to do if I do not have root priveledge

If you do not have root priveleges, you can also install the program via pythons virtualenv.

Note: Please see our documentation on virtual cluster on how to do that ;-)



COMMANDS
========


[fg-cleanup-db](./man/fg-cleanup-db.md)

* erases the content of the database

[fg-parser](./man/fg-parser.md)

* parses eucalyptus log entries and includes them into the database

[fg-euca-gather-log-files](./man/fg-euca-gather-log-files.md)

* gathers all eucalyptus log files into a single directory from the
eucalyptus log file directory. This script can be called from cron
repeatedly in order to avoid that log data is lost by using log file
rotation in eucalyptus.

[fg-metric](./man/fg-metric.md)

* a shell to interact with the metric database. 

OTHER
=====
./www

* displays graphs about data usage metrics are in 'www'
* Be displaying via google chart tools.

CONTRIBUTORS
============
* Hyungro Lee (lee212@indiana.edu)   
* Gregor von laszewski (laszewski@gmail.com)

KNOWN BUGS
==========

FEATURE REQUESTS
================

This project is under active development. In order for us to identify
priorities please let us know what features you like us to add.  We
will include a list here and identify based on resources and
priorities how to integrate them.

JOINING THE TEAM AND CONTRIBUTIONS
==================================

If you like to join the development efforts, please e-mail us. We can
than discuss how best you can contribute. You may have enhanced our
code already or used it in your system. If so, please let us know.

CONTACT
=======

send mail to laszewski@gmail.com
(Please insert the prefix: "METRICS: " in the subject of email messages)
