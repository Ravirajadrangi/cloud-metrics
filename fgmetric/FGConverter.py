import argparse, os, sys
import sqlite3 as lite
import MySQLdb
from collections import deque
from datetime import datetime
from fgmetric.FGEucaMetricsDB import FGEucaMetricsDB
from fgmetric.FGConstants import FGConst

class FGConverter:

    eucadb = FGEucaMetricsDB()

    #future = instances.in_the_future
    #past = instances.in_the_past

    s_date = None
    e_date = None

    filename = None
    filepath = None

    platform = None
    platform_version = None
    hostname = None
    confname = None
    database = None
    dbname = None
    dbname_nova = None
    dbname_keystone = None
    dbhost = None
    dbuser = None
    dbpass = None
    dbport = None

    query = None
    rows = None     #from database
    records = None  #for fg database

    userinfo = None
    cloudplatform = None

    def convert_to_fg(self):
        self.check_platform()
        self.read_database()
        self.map_to_fg()
        self.write_db()

    def check_platform(self):
        _check = getattr(self, "check_platform_" + self.platform)
        _check()

    def check_platform_nimbus(self):

        if not self.filename or not self.filepath:
            msg = "sqlite3 file is missing"
            print msg
            raise ValueError(msg)

        self.platform_version = self.platform_version or FGConst.DEFAULT_NIMBUS_VERSION
        self.database = FGConst.DEFAULT_NIMBUS_DB

        # this query is for sqlite3 because [timestamp] is only used on sqlite3?
        self.query = 'SELECT t1.time as "t_start [timestamp]",\
                    t3.time as "t_end [timestamp]",\
                    t1.uuid as instanceId,\
                    t2.dn,\
                    t1.cpu_count as ccvm_cores,\
                    t1.memory as ccvm_mem,\
                    t1.vmm as serviceTag \
                    from create_events t1, user t2, remove_events t3 \
                    on t1.user_id=t2.id and t1.uuid=t3.uuid \
                    where t1.time >= \'' + str(self.s_date) + '\' and t3.time <= \'' + str(self.e_date) + '\''

    def check_platform_openstack(self):

        if not self.dbname_nova or not self.dbname_keystone or not self.dbhost or not self.dbuser or not self.dbpass:
            msg = "db info is missing"
            print msg
            raise ValueError(msg)

        self.platform_version = self.platform_version or FGConst.DEFAULT_OPENSTACK_VERSION

        self.query = 'SELECT created_at as trace_extant_start,\
                    id,\
                    user_id as ownerId,\
                    project_id as accountId,\
                    image_ref as emiId,\
                    kernel_id as kernelId,\
                    ramdisk_id as ramdiskId,\
                    key_data as keyName,\
                    vm_state as state,\
                    memory_mb as ccvm_mem, \
                    vcpus as ccvm_cores, \
                    host as serviceTag, \
                    reservation_id as reservationId,\
                    COALESCE(launched_at, created_at, scheduled_at) as t_start, \
                    COALESCE(terminated_at, deleted_at) as t_end, \
                    uuid as instanceId, \
                    access_ip_v4 as ccnet_publicIp,\
                    ephemeral_gb as ccvm_disk \
                    from instances \
                    where updated_at >= \'' + str(self.s_date) + '\' and updated_at <= \'' + str(self.e_date) + '\''

    def read_database(self):
        conn_database = getattr(self, "connect_" + self.database)
        conn = conn_database()
        self.query_db(conn)
        self.close_db(conn)

    def oonnect_sqlite3(self):

        try: 
            con = lite.connect(self.filepath + "/" + self.filename, detect_types = lite.PARSE_COLNAMES)
            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d
            con.row_factory = dict_factory#lite.Row
            con.text_factory = str
            return con
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            if con:
                con.close()
            return None

    def connect_mysql(self):

        conn = None
        try:
            conn = MySQLdb.connect (self.dbhost, self.dbuser, self.dbpass, self.dbname_nova, self.dbport, cursorclass=MySQLdb.cursors.DictCursor)
            cursor = conn.cursor ()#MySQLdb.cursors.DictCursor)
            # 1. draw mapping table between openstack 'instances' and fg 'instance' table.
            # 2. define each column to know what exactly it means
            # 3. leave comments for missing and skipped columns
            # 4. check search options to see it is validate
            return conn
        except MySQLdb.Error, e:
            print "Error %s:" % e.args[0]
            if conn:
                cursor.close()
                conn.close()
            return None

    def query_db(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute(self.query)
            self.rows = cursor.fetchall()
        except (lite.Error, MySQLdb.Error) as e:
            print "Error %s:" % e.args[0]
            if conn:
                cursor.close()
                conn.close()

    def close_db(self, conn):
        if conn:
           #conn.cursor.close()
           conn.close()

    def convert_userinfo_of_nova(self):
        res = read_userinfo_of_nova_with_project_info()
        for row in res:
            ret = retrieve_ldap(row["name"])
            ret["ownerid"] = row["id"]
            ret["username"] = row["name"]
            ret["project"] = row["project_id"]
            ret["hostname"] = self.hostname
            rets.append(ret)
        write_userinfo(rets)

    def read_cloudplatform(self):
        if self.cloudplatform:
            return
        self.cloudplatform = self.eucadb.read_cloudplatform()

    def get_cloudplatform_id(self, querydict={}):
        class ContinueOutOfALoop(Exception): pass
        self.read_cloudplatform()
        for row in self.cloudplatform:
            try:
                for key in querydict:
                    if row[key] != querydict[key]:
                        raise ContinueOutOfALoop
                return row["cloudPlatformId"]
            except ContinueOutOfALoop:
                continue
        return None

    def map_to_fg(self):
        rows = self.rows
        records = []

        whereclause = { "platform": self.platform, "hostname": self.hostname, "version": self.platform_version }
        cloudplatformid = self.get_cloudplatform_id(whereclause)

        for row in rows:
            record = row

            record["instanceId"] = record["instanceId"][:15]
            record["ts"] = record["t_start"]
            #record["calltype"] = ""
            #record["userData"] = ""
            #record["kernelId"] = ""
            #record["emiURL"] = ""
            #record["t_start"] = row["t_start"]
            #record["t_end"] = row["t_end"]
            record["duration"] = (record["t_end"] - record["t_start"]).total_seconds()
            #record["trace"] = {
            #    "pending" : { "start" : self.future, "stop" : self.past, "queue" : deque("",10)},
            #    "extant" : { "start" : self.future, "stop" : self.past, "queue" : deque("",10)},
            #    "teardown" : { "start" : self.future, "stop" : self.past, "queue" : deque("",10)}
            #    }
            #record["serviceTag"] = row["serviceTag"] or ""
            #record["groupNames"] = ""
            #record["keyName"] = ""
            #record["msgtype"] = ""
            #record["volumesSize"] = 0.0
            #record["linetype"] = ""
            if "dn" in record and not "ownerId" in record:
                if len(record["dn"].split("CN=")) > 1:
                    record["ownerId"] = record["dn"].split("CN=")[1]
                else:
                    record["ownerId"] = record["dn"]
            record["date"] = record["t_start"]
            #record["id"] = 0
            #record["ncHostIdx"] = 0
            #record["ccvm"] = { "mem" : record["ccvm_mem"], "cores" : record["ccvm_cores"], "disk" : record[0 }
            #if "ccvm_disk" in row:
            #    record["ccvm"]["disk"] = row["ccvm_disk"]
            #if "emiId" in row:
            #    record["emiId"] = row["emiId"]
            #else:
            #    record["emiId"] = ""
            #record["ccnet"] = { "publicIp" : "", "privateMac" : "", "networkIndex" : "", "vlan" : "", "privateIp" : "" }

            #record["ramdiskURL"] = ""
            #record["accountId"] = ""
            #record["kernelURL"] = ""
            #record["ramdiskId"] = ""
            #record["volumes"] = ""
            #record["launchIndex"] = 0
            #record["bundleTaskStateName"] = ""
            #record["reservationId"] = ""
            record["platform"] = self.platform
            record["euca_hostname"] = self.hostname
            record["euca_version"] = self.platform_version
            #record["state"] = "Teardown" # need to be changed
            if not "state" in record:
                record["state"] = "Teardown"
            record["state"] = self.convert_state(record["state"])
            record["cloudplatformid"] = cloudplatformid
            print record
            break
            records.append(record)

        self.records = records

    def convert_state(self, state):
        if self.platform == "openstack":
            if state == "active":
                return "Extant"
            elif state == "building":
                return "Pending"
            elif state == "deleted" or "shutoff":
                return "Teardown"
            elif state == "error":
                return state
        return state

    def write_db(self):
        for record in self.records:
            print record
            self.eucadb._write(record)

    def set_instance_conf(self, confname=""):
        if confname and len(confname) > 0:
            self.eucadb.__init__(confname)

    def set_parser(self):
        def_s_date = "19700101"
        def_e_date = "29991231"
        def_conf = "futuregrid.cfg"
        def_nova = "nova"
        def_keystone = "keystone"
        def_db = "mysql"

        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--from", dest="s_date", default=def_s_date,
                help="Start date to begin parsing (type: YYYYMMDD)")
        parser.add_argument("-e", "--to", dest="e_date", default=def_e_date,
                help="End date to finish parsing (type: YYYYMMDD)")

        parser.add_argument("-p", "--platform", required=True,
                help="Cloud platform name, required. (e.g. nimbus, openstack, eucalyptus, etc)")
        parser.add_argument("-pv", "--platform_version",
                help="Cloud platform version. (e.g. 2.9 for nimbus, essex for openstack, and  2.0 or 3.1 for eucalyptus)")
        parser.add_argument("-n", "--hostname", required=True,
                help="Hostname of the cloud platform, required. (e.g., hotel, sierra, india, alamo, foxtrot)")
        parser.add_argument("--conf", dest="conf",
                help="futuregrid.cfg filepath (e.g. $HOME/.futuregrid/futuregrid.cfg)")

        parser.add_argument("-db", "--database", default=def_db,
                help="database type to load (e.g. mysql or sqlite3)")

        # sqlite3 for nimbus
        parser.add_argument("-i", "--file", dest="input_file",
                help="the sqlite3 filename with path (e.g. /home/metric/nimbus/alamo/alamo)")

        # mysql for openstack
        parser.add_argument("-dbn", "--dbname_nova", default=def_nova,
                help="Database of nova to use")
        parser.add_argument("-dbk", "--dbname_keystone", default=def_keystone,
                help="Database of keystone to use")
        parser.add_argument("-dh", "--dbhost",
                help="Connect to database host")
        parser.add_argument("-du", "--dbuser",
                help="User for login of database")
        parser.add_argument("-dp", "--dbpass",
                help="Password to use when connecting to database server")
        parser.add_argument("-dP", "--dbport", default=3306,
                help="Port number to use for connection or 3306 for default")

        args = parser.parse_args()
        print args

        try:
 
            self.s_date = datetime.strptime(args.s_date, "%Y%m%d")
            self.e_date = datetime.strptime(args.e_date, "%Y%m%d")
            self.platform = args.platform
            self.platform_version = args.platform_version
            self.hostname = args.hostname
            self.confname = self.set_instance_conf(args.conf)
   
            self.database = args.database
            self.dbname_nova = args.dbname_nova
            self.dbname_keystone = args.dbname_keystone
            self.dbhost = args.dbhost
            self.dbuser = args.dbuser
            self.dbpass = args.dbpass
            self.dbport = args.dbport

            abspath = os.path.abspath(args.input_file)
            filename = os.path.basename(abspath)
            filepath = os.path.dirname(abspath)
            self.filename = filename
            self.filepath = filepath

        except:
            pass#print sys.exc_info()[0]

        self.parser = parser

def main():
    converter = FGConverter()
    converter.set_parser()
    converter.convert_to_fg()

if __name__ == "__main__":
    main()
