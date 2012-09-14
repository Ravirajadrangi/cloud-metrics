#! /usr/bin/env python
'''FGParser'''

import re
import json
import pprint
import sys
import os
import re
import subprocess
from datetime import * 
from collections import deque
import argparse

import futuregrid.cloud.metric.FGEucaMetricsDB
from futuregrid.cloud.metric.FGStats import FGStats

manual="""
MANUAL PAGE DRAFT

NAME - fg-parser

DESCRIPTION

usage

<TBD>   cat filename.log | fg-parser <parameters>


All log entries are included through a pipe into the program

fg-parser

<TBD>  --nodb
      does not use the internal database, but just files

  --conf filename

      configuraton file of the database to be used. The configuration file has the following format

      [EucaLogDB]
      host=HOST
      port=PORT
      user=USER
      passwd=PASS
      db=DB

  if this parameter is not specified and a database is used the default location for this file is in

      ~/.futuregrid/futuregrid.cfg
      
  --cleardb

     This command without any parameter deletes the entire database.
     Be careful with this

<TBD>  --backup filename

     backups the database into a named file

<TBD>  --restore filename

      restores the database from the named file

  --parse type1 type2 ...

       if one of more types separated with space ar used, those types are
       parsed and included into the database, this parameter is optional and
       by default all types of interest are parsed. they are case insensitive

       types are print_ccInstance, refresh_resources

       BUG: Note the code does not yet analyse or store data
            from refresh resources. This was not our highest priority
       
       types we have not yet included include
          terminate_instances
          ....
          put all the other once we ignore here

  --from date_from --to date_to

     If a from and to date are specified in the following format: 2011-11-06 00:13:15
     all entries outside of these dates are ignored as part of the parsing step
     If no from and to are specified, all data is parsed

  
Usage tip:

using fgrep to search for the types before piping it into this program could
speed up processing. multiple files, can be concatenated simply with cat.
"""

class FGParser:
    ''' Log, DB parser '''

    def convert_data_to_list(self, data, attribute):
        rest = data[attribute]
        rest = re.sub(" ","' , '", rest)
        rest = "['" + rest[1:-1] + "']"
        restdata = eval(rest)
        data[attribute] = restdata

    def convert_data_to_dict(self, data, attribute):
        rest = data[attribute]
        rest = self.convert_str_to_dict_str(rest[1:-1])
        restdata = eval(rest)
        data[attribute] = restdata

    def convert_str_to_dict_str(self, line):
        line = re.sub(' +',' ',line)
        line = line.strip(" ")
        line = re.sub(',','%2C',line) # , value converts '%2C'
        line = re.sub(' ',',',line)

        # more regular dict
        line = re.sub('=','\'=\'',line)
        line = re.sub(',','\',\'',line)
        line = re.sub('=',' : ',line)
        line = re.sub('%2C', ',', line) # Back to , value
        return '{\'' + line + '\'}'

    def parse_type_and_date(self, line, data):
        # split line after the third ] to (find date, id, msgtype)
        # put the rest in the string "rest"
        try:
                m = re.search( r'\[(.*)\]\[(.*)\]\[(.*)\](.*)', line, re.M|re.I)
                data['date'] = datetime.strptime(m.group(1), '%a %b %d %H:%M:%S %Y')
                data['id']   = m.group(2)
                data['msgtype'] = m.group(3)
                rest =  m.group(4)
                rest = re.sub(' +}','}',rest).strip()
                if rest.startswith("running"):
                        data['linetype'] = "running"
                        return rest 
                elif rest.startswith("calling"):
                        data['linetype'] = "calling"
                        return rest 
                else:
                        location = rest.index(":")
                        linetype = rest[0:location]
                        data['linetype'] = re.sub('\(\)','',linetype).strip()
                        rest = rest[location+1:].strip()
                        return rest
        except (ValueError, AttributeError):
                data['linetype'] = "IGNORE"
                return
        except:
                data['linetype'] = "IGNORE"
                return

    def ccInstance_parser(self, rest, data):
        """parses the line and returns a dict"""

        # replace print_ccInstance(): with linetype=print_ccInstance
        #rest = rest.replace("print_ccInstance():","linetype=print_ccInstance")
        # replace refreshinstances(): with calltype=refresh_instances

        #RunInstances():
        rest = rest.replace("RunInstances():","calltype=run_instances")   # removing multiple spaces
        rest = rest.replace("refresh_instances():","calltype=refresh_instances")   # removing multiple spaces

        #separate easy assignments from those that would contain groups, for now simply put groups as a string
        # all others are merged into a string with *=* into rest
        m = re.search( r'(.*)keyName=(.*)ccnet=(.*)ccvm=(.*)ncHostIdx=(.*)volumes=(.*)groupNames=(.*)', rest, re.M|re.I)

        # Version 3.0.2
        # Deleted: emiId, kernelId, ramdiskId, emiURL, kernelURL and ramdiskURL
        # Added: accountId, platform, and bundleTaskStateName
        # Changed: value of ownerId is changed

        try:
                data['keyName'] = m.group(2).strip()
                data["ccnet"] = m.group(3).strip()
                data["ccvm"] = m.group(4).strip()
                data["volumes"] = m.group(6).strip()
                data["groupNames"] = m.group(7).strip()
                # assemble the rest string
                rest = m.group(1) + "ncHostIdx=" +m.group(5)
        except:
                return

        # GATHER ALL SIMPLE *=* assignments into a single rest line and add each entry to dict via eval
        rest = self.convert_str_to_dict_str(rest)
        try:
            restdata = eval (rest)
        except:
            print "eval failed:(" + str(sys.exc_info()[0]) + "), (" + str(rest) + ")"
            return

        data.update(restdata)

        # convert ccvm and ccnet to dict
        self.convert_data_to_dict(data,"ccvm")
        self.convert_data_to_dict(data,"ccnet")

        # converts volumes and groupNAmes to list
        self.convert_data_to_list(data,"groupNames")
        self.convert_data_to_list(data,"volumes")

        # convert the timestamp
        data["ts"] = datetime.fromtimestamp(int(data["ts"]))

        return data

    def refresh_resource_parser(self, rest, data):
        #[Wed Nov  9 19:50:08 2011][008128][EUCADEBUG ] refresh_resources(): received data from node=i2 mem=24276/22740 disk=306400/305364 cores=8/6
        if (rest.find("received") > -1):
            rest = re.sub("received data from","",rest).strip()
        # node=i2 mem=24276/22740 disk=306400/305364 cores=8/6
            m = re.search( r'node=(.*) mem=(.*)[/](.*) disk=(.*)/(.*) cores=(.*)/(.*)', rest, re.M|re.I)
            data["node"] = m.group(1)
            data["mem"] = m.group(2)
            data["mem_max"] = m.group(3)
            data["disk"] = m.group(4)
            data["disk_max"] = m.group(5)
            data["cores"] = m.group(6)
            data["cores_max"] = m.group(7)
        else:
            data["calltype"] = "ignore" 
        return data

    def terminate_instances_param_parser(self, rest, data):

        rest = rest.strip()
        if rest.startswith("params"):
            #params: userId=(null), instIdsLen=1, firstInstId=i-417B07B2
            rest = re.sub("params:","",rest).strip()
            # node=i2 mem=24276/22740 disk=306400/305364 cores=8/6
            m = re.search( r'userId=(.*) instIdsLen=(.*) firstInstId=(.*)', rest, re.M|re.I)
            userid = m.group(1)
            if userid == "(null),":
                data["userId"] = "null"
            else:
                data["userId"] = m.group(1)
            data["instIdsLen"] = m.group(2)
            data["firstInstId"] = m.group(3)
        else:
            data["calltype"] = "ignore" 
        return data

    def print_counter (self, label, counter):
        print label + " = " + str(counter)

    def parse_file (self, filename, analyze, parse_types, gzip,  debug=False, progress=True):

        if gzip :
            import zlib
            CHUNKSIZE=1024
            gz = zlib.decompressobj(16+zlib.MAX_WBITS)

        print filename
        f = open(filename, 'r')
        lines_total = 0
        lines_ignored = 0
        count_terminate_instances = 0
        count_refresh_resource = 0
        count_ccInstance_parser = 0 
        read_bytes = 0
        file_size = os.path.getsize(filename)
        if debug:
            print "SIZE>:" + str(file_size)

        progress_step = file_size / 100
        for line in f:
            if gzip:
                line = gz.decompress(line)
            ignore = False
            lines_total += 1
            read_bytes += len(line)
            if (debug or progress) and ((lines_total % 1000) == 0):
                percent = int(100 * read_bytes / file_size ) 
                sys.stdout.write("\r%2d%%" % percent)
                sys.stdout.flush()
            if debug:
                print "DEBUG " + str(lines_total) +"> " + line
            data = {}
            rest = self.parse_type_and_date (line, data)
            '''
            Temporarily prince_ccInstance is only available to parse

            if data["linetype"] == "TerminateInstances" and "TerminateInstances" in parse_types:
                count_terminate_instances += 1
                terminate_instances_param_parser(rest, data)
            elif data["linetype"] == "refresh_resources" and "refresh_resources" in parse_types:
                count_refresh_resource += 1
                refresh_resource_parser(rest, data)
            el'''
            if data["linetype"] == "print_ccInstance" and "print_ccInstance" in parse_types:
                count_ccInstance_parser += 1
                if not ccInstance_parser(rest, data):
                        ignore = True
            else:
                ignore = True
            if ignore:
                lines_ignored +=1
                if debug:
                    print "IGNORE> " + line
            else:
                if data["linetype"] == "print_ccInstance" and "print_ccInstance" in parse_types:
                    analyze(data)

            # For Debugging to make it faster terminate at 5
            if debug and (len(instance) > 5):
                break

        print_counter("lines total",lines_total)
        print_counter("lines ignored = ", lines_ignored)
        print_counter("count_terminate_instances",count_terminate_instances)
        print_counter("count_refresh_resource",count_refresh_resource)
        print_counter("count_ccInstance_parser ",count_ccInstance_parser )
               
        return

    #####################################################################
    # MAIN
    #####################################################################
    def parse_test(f, line):
        print "------------------------------------------------------------"
        print "- parsetest: " + str(f)
        print "------------------------------------------------------------"
        print "INPUT>"
        print line
        data = {}
        rest = parse_type_and_date (line, data)
        print "REST>"
        print rest
        f(rest, data)
        print "OUTPUT>"
        print pp.pprint(data)

    def test1():
        parse_test(ccInstance_parser, 
                   "[Wed Nov  9 19:58:12 2011][008128][EUCADEBUG ] print_ccInstance(): refresh_instances():  instanceId=i-42BA06B1 reservationId=r-3D3306BC emiId=emi-0B951139 kernelId=eki-78EF12D2 ramdiskId=eri-5BB61255 emiURL=http://149.165.146.135:8773/services/Walrus/centos53/centos.5-3.x86-64.img.manifest.xml kernelURL=http://149.165.146.135:8773/services/Walrus/xenkernel/vmlinuz-2.6.27.21-0.1-xen.manifest.xml ramdiskURL=http://149.165.146.135:8773/services/Walrus/xeninitrd/initrd-2.6.27.21-0.1-xen.manifest.xml state=Extant ts=1320693195 ownerId=sharif keyName=ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCp13CbKJLtKG5prGiet/VHct36CXzcpBKVgYsh/lxIXWKuositayvvuKux+I5GZ9bFWzMF71xAjmFinmAT3FXFKMd54FebPKZ2kBPCRqtmxz2jT1SG4hy1g1eDPzVX+qt5w8metAs7W//BCaBvWpU5IBuKSNqxO5OUIjIKkw3xkSswRpqSzrUBAmQP7e4dzQvmhqIxq4ZWqcEIWsAik0fSODTipa+Z6DvVKe02f5OtdUsXzz7pIivZ3qRGQveI5SOTdgFPqG+VglMsPURLbFFVWW1l51gCmRUwTf9ClySshSpkpAtaOx/OApQoII/vJxgr/EdYPOu1QLkubS4XH6+Z sharif@eucalyptus ccnet={privateIp=10.0.4.4 publicIp=149.165.159.130 privateMac=D0:0D:42:BA:06:B1 vlan=10 networkIndex=4} ccvm={cores=1 mem=512 disk=5} ncHostIdx=24 serviceTag=http://i1:8775/axis2/services/EucalyptusNC userData= launchIndex=0 volumesSize=0 volumes={} groupNames={sharifnew }")

        # Version 3.0.2
        # [Wed May 16 11:59:25 2012][032119][EUCADEBUG ] print_ccInstance(): refresh_instances():  instanceId=i-5CDD447C reservationId=r-A8053C5D state=Extant accountId=514855794567 ownerId=EJMBZFNPMDQ73AUDPOUS3 ts=1337194539 keyName=ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCMm5cR9ukIHyy7w3V3FJ45LkdHjafTrfuGU6aonaJ10SJb8oLlqRiT+fPlGcLaZWrHSMbK+TODUa7hgu297BIAN0gUm68ZNKpkLoSXw+IeK0W3u42BYs1+imBMmyXFa8qWjVqt+Xrw2RPImnH+zqqGUvB8DOwLfzXBfJ09o/GuwapZahUm5FjaVCSTp2JptAR7F2nTrKXVTn7S81yzhUF/oM+ublfcav87MDetKVtB591rspjUhtDVnDS+tkvSZfWYpkpKR/4VB3ZXqhzWM5HXw/RFS6J5ywY3a1/FbsOFUFj5y94EAqQkWzSBcJ4cig1e+DQ2SkMAnHraWHL8hQpB 514855794567@eucalyptus.euca3-test ccnet={privateIp=10.135.86.238 publicIp=198.202.120.202 privateMac=D0:0D:5C:DD:44:7C vlan=3759 networkIndex=110} ccvm={cores=1 mem=256 disk=4} ncHostIdx=0 serviceTag=http://s61:8775/axis2/services/EucalyptusNC userData= launchIndex=21 platform=linux bundleTaskStateName=none, volumesSize=0 volumes={} groupNames={514855794567-fd6a9f37-b775-43ec-918c-cc9584f74043 }

        # Deleted: emiId, kernelId, ramdiskId, emiURL, kernelURL and ramdiskURL
        # Added: accountId, platform, and bundleTaskStateName
        # Changed: Value of ownerId is changed

        return

    def test2():
        ''' RESOURCE PARSER '''

        parse_test(refresh_resource_parser, 
                   "[Wed Nov  9 22:52:10 2011][008128][EUCAERROR ] refresh_resources(): bad return from ncDescribeResource(i23) (1)")
        parse_test(refresh_resource_parser, 
                   "[Wed Nov  9 22:52:11 2011][008128][EUCADEBUG ] refresh_resources(): done")
        parse_test(refresh_resource_parser, 
                   "[Wed Nov  9 22:52:19 2011][008128][EUCAINFO  ] refresh_resources(): called")
        parse_test(refresh_resource_parser, 
                   "[Wed Nov  9 19:50:08 2011][008128][EUCADEBUG ] refresh_resources(): received data from node=i2 mem=24276/22740 disk=306400/305364 cores=8/6")

        return

    def test3():
        ''' TerminateInstance Parser'''
        parse_test(terminate_instances_param_parser,
                   "[Thu Nov 10 10:14:37 2011][021251][EUCADEBUG ] TerminateInstances(): params: userId=(null), instIdsLen=1, firstInstId=i-417B07B2")

        parse_test(terminate_instances_param_parser,
                   "[Thu Nov 10 13:04:16 2011][016124][EUCADEBUG ] TerminateInstances(): done.")

        parse_test(terminate_instances_param_parser,
                   "[Thu Nov 10 13:04:16 2011][016168][EUCAINFO  ] TerminateInstances(): called")
        return

    def test4():
        parse_file ("/tmp/cc.log.4",jason_dump,debug=False)
        return

    # Convert 2012-01-28-04-13-04-cc.log to datetime
    def filename_todate(str):
        filename = str.split(".")[0]
        return datetime.strptime(filename, '%Y-%m-%d-%H-%M-%S-cc')

    def test_file_read(filename,progress=True, debug=False):
        parse_file (filename,instances.add,debug,progress)
        instances.dump()
        return

    def test_sql_read():
        instances.read_from_db()
        instances.dump()
        return

    def test_sql_write(filename,progress=True, debug=False):
        parse_file (filename,instances.add,debug,progress)
        instances.write_to_db()

    def read_log_files_and_store_to_db (instances, path, from_date, to_date, linetypes, gzip):

        listing = os.listdir(path)
        f_date = datetime.strptime(from_date + " 00:00:00", '%Y%m%d %H:%M:%S')
        t_date = datetime.strptime(to_date + " 23:59:59", '%Y%m%d %H:%M:%S')

        for filename in listing:
            try:
                if f_date <= filename_todate(filename) and filename_todate(filename) <= t_date:
                    print "Processing file is: " + filename
                    #parse_file(path + "/" + filename, instances.add, linetypes, gzip, debug=False, progress=True)
                    parse_file(path + "/" + filename, instances.update_traceinfo, linetypes, gzip, debug=False, progress=True)
            except (ValueError):
                continue

        instances.write_to_db()

        # set userinfo
        instances.set_userinfo()
        instances.write_userinfo_to_db()

    def read_from_stdin_and_store_to_db(instances, linetypes):

        lines_total = 0 
        lines_ignored = 0 
        count_ccInstance_parser = 0

        while 1:
            try:
                line = sys.stdin.readline()
                line = line.rstrip()

                lines_total += 1
                    
                data = {}
                rest = parse_type_and_date (line, data)
                if data["linetype"] == "print_ccInstance" and "print_ccInstance" in linetypes:

                    count_ccInstance_parser += 1
                    if not ccInstance_parser(rest, data):
                        lines_ignored += 1 
                    else:
                        single_data = instances.update_traceinfo(data)
                        instances.eucadb.write(single_data)
            except:
                break

        self.print_counter("lines total",lines_total)
        self.print_counter("lines ignored", lines_ignored)
        self.print_counter("count_ccInstance_parser",count_ccInstance_parser )

        return


    def utility_insert_userinfo_from_file_or_std():

        '''Store userinfo into database by reading a userid(s) from a text file or a standard input
        This command will read a userid(s) and do ldapsearch to find userinfo. And then it will
        store the userinfo into mysql database.

        Usage: $ fg-metrics-utility insert_userinfo -i filename [hostname]
               or
               $ fg-metrics-utility insert_userinfo userid [hostname]
        '''

        i = Instances()
        filename = ""
        userid = ""
        ownerid = ""
        username = ""
        project = ""

        if len(sys.argv) < 3 or sys.argv[1] != "insert_userinfo":
            print "usage: ./$ fg-metrics-utility insert_userinfo -i filename [hostname] \n\
                   or \n\
                   $ fg-metrics-utility insert_userinfo userid [hostname]"
            return

        if sys.argv[2] == "-i":
            filename = sys.argv[3]
            hostname = sys.argv[4]
        else:
            userid = sys.argv[2]
            hostname = sys.argv[3]

        if os.path.exists(filename):
            f = open(filename, "r")
            while 1:
                line = f.readline()
                if not line:
                    break

                ownerid = line.rstrip()
                # For comma seperated lines
                # E.g. 5TQVNLFFHPWOH22QHXERX,hyunjoo,fg45
                # Ownerid, username, projectid
                m = re.search(r'(.*),(.*),(.*)', line.rstrip())

                if m:
                    try:
                        userid = m.group(1)
                        username = m.group(2)
                        project = m.group(3)
                    except:
                        m = None
                        pass

                    # In euca3.0+, username is an ownerid of past version of euca
                    if username:
                        ownerid = username
                res = self.retrieve_userinfo_ldap(ownerid)
                if res:
                    if m:
                        # if m exists, res (dict) should be merged with the comma separated values in order to store the info into db
                        res["ownerid"] = userid
                        res["username"] = username
                        res["project"] = project
                        if hostname:
                            res["hostname"] = hostname
                    print res
                    i.userinfo_data.append(res)
        else:
            res = self.retrieve_userinfo_ldap(userid)
            if res:
                i.userinfo_data.append(res)

        i.write_userinfo_to_db()

def main():

    users = {}
    instances = Instances()
    instance = instances.data
    pp = pprint.PrettyPrinter(indent=4)

    def_s_date = "19700101"
    def_e_date = "29991231"
    def_conf = "futuregrid.cfg"
    def_linetypes = ["TerminateInstances", "refresh_resources", "print_ccInstance"]

    ''' argument parser added '''

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--from", dest="s_date", default=def_s_date,
		    help="start date to begin parsing (type: YYYYMMDD)")
    parser.add_argument("-e", "--to", dest="e_date", default=def_e_date,
		    help="end date to finish parsing (type: YYYYMMDD)")
    parser.add_argument("-i", dest="input_dir", required=True,
		    help="Absolute path where the files (e.g. 2012-02-16-00-21-17-cc.log generated by fg-unix) exist")
    parser.add_argument("--conf", dest="conf",
		    help="configuraton file of the database to be used")
    parser.add_argument("--cleandb", action="store_true", dest="cleandb", default=False,
		    help="This command without any parameter deletes the entire database. *Be careful with this")
    parser.add_argument("--parse", nargs="+", dest="linetypes", default=def_linetypes,
                    help="specify function names which you want to parse (types: print_ccInstance, refresh_resources)")
    parser.add_argument("-z", "--gzip", action="store_true", default=False,
                    help="gzip compressed files will be loaded")
    args = parser.parse_args()
    print args
    
    '''
    Parameters
    ----------
    dest=variable name
    - 'dest' in parser.add_argument sets a variable name where the input to be allocated
    required=True
    - To set an argument is mandatory (required=False is default)
    help=text
    - Description for the argument

    How we can use argparse in this file?
    -------------------------------------
    1) fg-parser.py -s start date -e end date; will parse logs between the period that specified by -s and -e options
       ex) fg-parser.py -s 20120216 -e 20120216
           => 2012-02-16-00-21-17-cc.log ~ 2012-02-16-23-47-16-cc.log will be parsed
    2) fg-parser.py -f filename; Only parse the file that specified by -f option
       ex) fg-parser.py -f 2012-02-16-00-21-17-cc.log
           => Only that file will be parsed
    '''

    # change conf file by --conf filename
    if args.conf:
	    instances.set_conf(args.conf)

    # Clean database if -cleandb is true
    #if args.cleandb:
	    #import FGCleanupTable
	    #FGCleanupTable.main()

    if args.input_dir == "-":
	read_from_stdin_and_store_to_db(instances, args.linetypes)
    else:
	read_log_files_and_store_to_db(instances, args.input_dir, args.s_date, args.e_date, args.linetypes, args.gzip)
    
if __name__ == "__main__":
    main()