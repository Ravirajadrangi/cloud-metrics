import os
import sys
import ConfigParser
import MySQLdb
import sqlite3

class FGDatabase:

    instance_table = "instance"
    userinfo_table = "userinfo"
    cloudplatform_table = "cloudplatform"
    column_cp_ins = "cloudPlatform"
    column_cp_cp = "cloudPlatformId"

    def __init__(self):
        self.config_filename = FGConst.DEFAULT_CONFIG_FILENAME
        self.config_filepath = FGConst.DEFAULT_CONFIG_FILEPATH
        self.config = self.config_filepath + "/" + self.config_filename
        self.db_type = "mysql"

    def __del__(self):
        self.close()

    def conf(self):
        config = ConfigParser.ConfigParser()
        config.read(self.config)

        try:
            dbhost = config.get('EucaLogDB', 'host')
            dbport = int(config.get('EucaLogDB', 'port'))
            dbuser = config.get('EucaLogDB', 'user')
            dbpasswd = config.get('EucaLogDB', 'passwd')
            dbname = config.get('EucaLogDB', 'db')
            euca_hostname = config.get('EucaLogDB', 'euca_hostname')
            euca_version = config.get('EucaLogDB', 'euca_version')
        except ConfigParser.NoSectionError:
            raise

    def set_conf(self, input_file):

        try:
            abspath = os.path.abspath(input_file)
            self.config_filename = os.path.basename(abspath)
            self.config_filepath = os.path.dirname(abspath)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def get_userinfo(self):
    def get_instance(self):

    def connect(self):
        conn_database = getattr(self, "connect_" + self.db_type)
        conn = conn_database()

    def connect_mysql(self):
        try:
            self.conn = MySQLdb.connect (self.dbhost, self.dbuser, self.dbpasswd, self.dbname, self.dbport, cursorclass=MySQLdb.cursors.DictCursor)
            #self.cursor = self.conn.cursor()
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def connect_sqlite3(self):

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        try:
            conn = sqlite3.connect(self.sqlite3_file, detect_types = sqlite3.PARSE_COLNAMES)
            conn.row_factory = dict_factory#lite.Row
            conn.text_factory = str
            self.conn = conn
        except lite.Error, e:
            print "Error %s:" % e.args[0]

    def close(self):
        #if self.cursor:
        #    self.cursor.close()
        if self.conn:
            self.conn.close()

    '''
    def select(self):
    def insert(self):
    def alter(self):
    def delete(self):
    '''

    def read(self, querydict={}, optional=""):
        ''' read from the database '''
        
        foreign_key_for_cloudplatform = self.instance_table + "." + self.column_cp_ins + "=" + self.cloudplatform_table + "." + self.column_cp_cp
        querystr = "";
        if querydict:
            for key in querydict:
                value = querydict[key]
                astr = key + "='" + value + "'"
                if querystr != "":
                    querystr += " and "
                querystr += astr            
                print "qstr:->" + querystr + "<---"
                rquery = "SELECT * FROM " + self.instance_table + "," + self.cloudplatform_table + " where " + foreign_key_for_cloudplatform + " and " + querystr + optional
                #rquery = "select * from instance, cloudplatform  where instance.cloudPlatform=cloudplatform.cloudPlatformId limit 5";    
        else:
            rquery = "SELECT * from " + self.instance_table + "," + self.cloudplatform_table + " where " + foreign_key_for_cloudplatform + " " + optional
        self.cursor.execute(rquery)
        rows = self.cursor.fetchall()
        multikeys = ["trace", "ccvm", "ccnet"]
        listvalues = ["groupNames", "volumes"]
        lrows = list(rows)
        ret = []
        for arow in lrows:
            rowret = {}
            for key in arow:
                keys = key.rsplit("_")
                if keys[0] in multikeys:
                    self._assignVal2Multi(rowret, keys, arow[key])
                elif key in listvalues:
                    if not arow[key] is None:
                        values = arow[key].rsplit(" ")
                        rowret[key] = values
                    else:
                        rowret[key] = []
                else:
                    rowret[key] = arow[key]
            ret.append(rowret)
        return ret

    def _assignVal2Multi(self, themulti, keys, value=None):
        ''' help function to initialize(if necessary) and assign value to nested dict '''
        tolevel = len(keys) - 1
        curlevel = 0
        nextlevel = curlevel + 1
        if not themulti.has_key(keys[curlevel]):
            themulti[keys[curlevel]] = {}
        cur = themulti[keys[curlevel]]
        while nextlevel < tolevel:
            if not cur.has_key(keys[nextlevel]):
                cur[keys[nextlevel]] = {}
            cur = cur[keys[nextlevel]]
            curlevel += 1
            nextlevel += 1

        cur[keys[nextlevel]] = value
        return cur

    def _read(self, cursor, tablename, querydict, optional=""):
        
        querystr = "";
        ret = []

        if querydict:
            for key in querydict:
                value = querydict[key]
                astr = key + "='" + value + "'"
                if querystr != "":
                    querystr += " and "
                querystr += astr            
                rquery = "SELECT * FROM " + tablename + " where " + querystr + optional
        else:
            rquery = "SELECT * from " + tablename + optional
           
        try:
            cursor.execute(rquery)
        except (MYSQLdb.Error, sqlite3.Error) as e:
            print str(e)
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

        rows = cursor.fetchall()
        for arow in list(rows):
            ret.append(arow)
        return ret

    def read_instance(self, querydict={}):
        return self._read(self.cursor, self.instance_table, querydict)

    def read_userinfo(self, querydict={}):
        return self._read(self.cursor, self.userinfo_table, querydict)

    def _delete(self, tablename, querydict):

        querystr = "";
        if querydict:
            for key in querydict:
                value = querydict[key]
                astr = key + "='" + value + "'"
                if querystr != "":
                    querystr += " and "
                querystr += astr            
                rquery = "delete FROM " + tablename + " where " + querystr
        else:
            rquery = "delete from " + tablename 
 
	try:
            self.cursor.execute(rquery)
        except (MySQLdb.Error, sqlite3.Error) as e:
            print str(e)
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def delete_instance(self, querydict={}):
        self._delete(self.instance_table, querydict)

    def delete_userinfo(self, querydict={}):
        self._delete(self.userinfo_table, querydict)

    def write(self, entryObj):
        ''' write instance object into db '''
        uidcat = entryObj["instanceId"] + " - " + str(entryObj["ts"])
        m = hashlib.md5()
        m.update(uidcat)
        uid = m.hexdigest()
        pp.pprint(entryObj)
        wquery = "INSERT INTO " + self.instance_table + " ( uidentifier, \
                                    instanceId, \
                                    ts, \
                                    calltype, \
                                    userData, \
                                    kernelId, \
                                    emiURL, \
                                    t_start, \
                                    t_end, \
                                    duration, \
                                    trace_pending_start, \
                                    trace_pending_stop, \
                                    trace_extant_start, \
                                    trace_extant_stop, \
                                    trace_teardown_start, \
                                    trace_teardown_stop, \
                                    serviceTag, \
                                    groupNames, \
                                    keyName, \
                                    msgtype, \
                                    volumesSize, \
                                    linetype, \
                                    ownerId, \
                                    date, \
                                    id, \
                                    ncHostIdx, \
                                    ccvm_mem, \
                                    ccvm_cores, \
                                    ccvm_disk, \
                                    emiId, \
                                    ccnet_publicIp, \
                                    ccnet_privateMac, \
                                    ccnet_networkIndex, \
                                    ccnet_vlan, \
                                    ccnet_privateIp, \
                                    ramdiskURL, \
                                    state, \
                                    accountId, \
                                    kernelURL, \
                                    ramdiskId, \
                                    volumes, \
                                    launchIndex, \
                                    platform, \
                                    bundleTaskStateName, \
                                    reservationId, \
                                    euca_hostname, \
                                    euca_version ) \
                            VALUES (" \
                                    + self._fmtstr(uid) + "," \
                                    + self._fmtstr(entryObj["instanceId"]) + "," \
                                    + self._fmtstr(str(entryObj["ts"])) + "," \
                                    + self._fmtstr(entryObj["calltype"]) + "," \
                                    + self._fmtstr(entryObj["userData"]) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "kernelId")) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "emiURL")) + "," \
                                    + self._fmtstr(str(entryObj["t_start"])) + "," \
                                    + self._fmtstr(str(entryObj["t_end"])) + "," \
                                    + str(entryObj["duration"]) + "," \
                                    + self._fmtstr(str(entryObj["trace"]["pending"]["start"])) + "," \
                                    + self._fmtstr(str(entryObj["trace"]["pending"]["stop"])) + "," \
                                    + self._fmtstr(str(entryObj["trace"]["extant"]["start"])) + "," \
                                    + self._fmtstr(str(entryObj["trace"]["extant"]["stop"])) + "," \
                                    + self._fmtstr(str(entryObj["trace"]["teardown"]["start"])) + "," \
                                    + self._fmtstr(str(entryObj["trace"]["teardown"]["stop"])) + "," \
                                    + self._fmtstr(entryObj["serviceTag"]) + "," \
                                    + self._fmtstr(" ".join(entryObj["groupNames"])) + "," \
                                    + self._fmtstr(entryObj["keyName"]) + "," \
                                    + self._fmtstr(entryObj["msgtype"]) + "," \
                                    + str(entryObj["volumesSize"]) + "," \
                                    + self._fmtstr(entryObj["linetype"]) + "," \
                                    + self._fmtstr(entryObj["ownerId"]) + "," \
                                    + self._fmtstr(str(entryObj["date"])) + "," \
                                    + str(entryObj["id"]) + "," \
                                    + str(entryObj["ncHostIdx"]) + "," \
                                    + str(entryObj["ccvm"]["mem"]) + "," \
                                    + str(entryObj["ccvm"]["cores"]) + "," \
                                    + str(entryObj["ccvm"]["disk"]) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "emiId")) + "," \
                                    + self._fmtstr(entryObj["ccnet"]["publicIp"]) + "," \
                                    + self._fmtstr(entryObj["ccnet"]["privateMac"]) + "," \
                                    + self._fmtstr(entryObj["ccnet"]["networkIndex"]) + "," \
                                    + self._fmtstr(entryObj["ccnet"]["vlan"]) + "," \
                                    + self._fmtstr(entryObj["ccnet"]["privateIp"]) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "ramdiskURL")) + "," \
                                    + self._fmtstr(entryObj["state"]) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "accountId")) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "kernelURL")) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "ramdiskId")) + "," \
                                    + self._fmtstr(" ".join(entryObj["volumes"])) + "," \
                                    + str(entryObj["launchIndex"]) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "platform")) + "," \
                                    + self._fmtstr(self._fillempty(entryObj, "bundleTaskStateName")) + "," \
                                    + self._fmtstr(entryObj["reservationId"]) + "," \
                                    + self._fmtstr(entryObj["euca_hostname"] or self.euca_hostname) + "," \
                                    + self._fmtstr(entryObj["euca_version"] or self.euca_version) + ")"


        wquery += " on duplicate key update " \
                + "t_end=" \
                + self._fmtstr(str(entryObj["t_end"])) + "," \
                + " duration=" \
                + str(entryObj["duration"]) + "," \
                + " trace_pending_start=LEAST(trace_pending_start, " \
                + self._fmtstr(str(entryObj["trace"]["pending"]["start"])) + ") ," \
                + " trace_pending_stop=GREATEST(trace_pending_stop, " \
                + self._fmtstr(str(entryObj["trace"]["pending"]["stop"])) + ") ," \
                + " trace_extant_start=LEAST(trace_extant_start, " \
                + self._fmtstr(str(entryObj["trace"]["extant"]["start"])) + ") ," \
                + " trace_extant_stop=GREATEST(trace_extant_stop, " \
                + self._fmtstr(str(entryObj["trace"]["extant"]["stop"])) + ") ," \
                + " trace_teardown_start=LEAST(trace_teardown_start, " \
                + self._fmtstr(str(entryObj["trace"]["teardown"]["start"])) + ") ," \
                + " trace_teardown_stop=GREATEST(trace_teardown_stop, " \
                + self._fmtstr(str(entryObj["trace"]["teardown"]["stop"])) + ") ," \
                + " date=" \
                + self._fmtstr(str(entryObj["date"])) + "," \
                + " state=" \
                + self._fmtstr(entryObj["state"])

        #print wquery
        try:
            self.cursor.execute(wquery)

        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def write_userinfo(self, entryObj):
        ''' write userinfo object into db '''
        self._write("userinfo", entryObj)

    def _write(self, tablename, entryObj):

        try:
            keys = ", ".join(entryObj.keys())
            values = "'" + "' ,'".join(str(x) for x in entryObj.values()) + "'"
            wquery = "INSERT INTO " + tablename + " ( " + keys + " ) VALUES ( " + values + " )"
            #print wquery
            self.cursor.execute(wquery)

        except (MySQLdb.Error, sqlite3.Error) as e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            pass
        except AttributeError, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def change_table(self, table_name):
	self.instance_table = table_name
        return