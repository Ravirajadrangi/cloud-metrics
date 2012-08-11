''' Gregor von Laszewski, http://gregor.cyberaide.org '''

import sys
import AmieUsageRecord as amie

def header(name):
    print "\n", 60 * '-', "\n   ", name, '\n', 60 * '-'
    
def test(object, label=object):
    header(label)
    object.export(sys.stdout,0)

transform = amie.TransformType (Algorithm='Algorithm',
                                anytypeobjs_='anytypeobjs_',
                                XPath='XPath',
                                valueOf_='valueOf_',
                                #mixedclass_='mixedclass_',
                                #content_='content_')
                                )
transforms = amie.TransformsType (Transform=[transform])

digestmethod = amie.DigestMethodType (Algorithm='Algorithm',
                                      anytypeobjs_='anytypeobjs_',
                                      valueOf_='valueOf_',
                                      #mixedclass_='mixedclass_',
                                      #content_='content_')
                                      )

reference = amie.ReferenceType (Type='Type',
                                Id='Id',
                                URI='URI',
                                Transforms=transforms,
                                DigestMethod=digestmethod,
                                #DigestValue='digestvalue')
                                )

spkidata = amie.SPKIDataType (SPKISexp='SPKISexp',
                              #anytypeobjs_='anytypeobjs_')
                              )

pgpdata = amie.PGPDataType (PGPKeyID='PGPKeyID',
                            PGPKeyPacket='PGPKeyPacket',
                            #anytypeobjs_='anytypeobjs_')
                            )

x509issuerserial = amie.X509IssuerSerialType (X509IssuerName='X509IssuerName',
                                              X509SerialNumber='X509SerialNumber')

x509data = amie.X509DataType (X509IssuerSerial=x509issuerserial,
                              X509SKI='X509SKI',
                              X509SubjectName='X509SubjectName',
                              X509Certificate='X509Certificate',
                              X509CRL='X509CRL',
                              #anytypeobjs_='anytypeobjs_')
                              )


retrievalmethod = amie.RetrievalMethodType (Type='Type',
                                            URI='URI',
                                            Transforms=transforms)


keyinfo = amie.KeyInfoType (Id='Id',
                            KeyName='KeyName',
                            KeyValue='KeyValue',
                            RetrievalMethod=retrievalmethod,
                            X509Data=x509data,
                            PGPData=pgpdata,
                            SPKIData=spkidata,
                            MgmtData='MgmtData',
                            anytypeobjs_='anytypeobjs_',
                            valueOf_='valueOf_',
                            #mixedclass_='mixedclass_',
                            #content_='content_')
                            )
test(keyinfo)


#CHECK THIS
network = amie.Network (storageUnit='storageUnit',
                        metric='to',
                        description='description',
                        phaseUnit='phaseUnit',
                        valueOf_='valueOf_')
#CHECK THIS
disk = amie.Disk (storageUnit='storageUnit',
                  metric='to',
                  type_='type_',
                  description='description',
                  phaseUnit='phaseUnit',
                  valueOf_='valueOf_')
#CHECK THIS
memory = amie.Memory (storageUnit='storageUnit',
                      metric='to',
                      type_='type_',
                      description='description',
                      phaseUnit='phaseUnit',
                      valueOf_='valueOf_')
#CHECK THIS
swap = amie.Swap (storageUnit='storageUnit',
                  metric='to',
                  type_='type_',
                  description='description',
                  phaseUnit='phaseUnit',
                  valueOf_='valueOf_')

#CHECK THIS
nodecount = amie.NodeCount (metric='to',
                            description='description',
                            valueOf_='valueOf_')

processors = amie.Processors (consumptionRate=0.4,
                              metric='metric',
                              description='description',
                              valueOf_='valueOf_')

timeduration = amie.TimeDuration (type_='type_',
                                  valueOf_='valueOf_')

timeinstant = amie.TimeInstant (type_='type_',
                                valueOf_='valueOf_')

servicelevel = amie.ServiceLevel (type_='type_',
                                  valueOf_='valueOf_')

cpuduration = amie.CpuDuration (usageType='usageType',
                                description='description',
                                valueOf_='valueOf_')

wallduration = amie.WallDuration (description='description',
                                  valueOf_='valueOf_')

endtime = amie.EndTime (description='description',
                        valueOf_='valueOf_')

starttime = amie.StartTime (description='description',
                            valueOf_='valueOf_')

machinename = amie.MachineName (description='description',
                                valueOf_='valueOf_')

submithost = amie.SubmitHost (description='description',
                              valueOf_='valueOf_')

#check this
host = amie.Host (description='description',
                  primary='primary=',
                  valueOf_='valueOf_')

queue = amie.Queue (description='description',
                    valueOf_='valueOf_')

jobname = amie.JobName (description='description',
                        valueOf_='valueOf_')

projectname = amie.ProjectName (description='description',
                                valueOf_='valueOf_')

status = amie.Status (description='description',
                      valueOf_='valueOf_')

charge = amie.Charge (formula='formula',
                      description='description',
                      unit='unit',
                      valueOf_='valueOf_')

jobidentity = amie.JobIdentity (GlobalJobId='GlobalJobId',
                                LocalJobId='LocalJobId',
                                ProcessId='ProcessId')

useridentity = amie.UserIdentity (LocalUserId='LocalUserId',
                                  KeyInfo=keyinfo)

recordidentity = amie.RecordIdentity (recordId='recordId',
                                      createTime='createTime',
                                      KeyInfo=keyinfo)

consumableresource = amie.ConsumableResourceType (units='units',
                                                  description='description',
                                                  valueOf_='valueOf_',
                                                  extensiontype_='extensiontype_')

resource = amie.ResourceType (description='description',
                              valueOf_='valueOf_')

canonicalizationmethod = amie.CanonicalizationMethodType (Algorithm='Algorithm',
                                                          anytypeobjs_='anytypeobjs_',
                                                          valueOf_='valueOf_',
                                                          #mixedclass_='mixedclass_',
                                                          #content_='content_')
                                                          )

signaturemethod = amie.SignatureMethodType (Algorithm='Algorithm',
                                            HMACOutputLength='HMACOutputLength',
                                            anytypeobjs_='anytypeobjs_',
                                            valueOf_='valueOf_',
                                            #mixedclass_='mixedclass_',
                                            #content_='content_')
                                            )

signedinfo = amie.SignedInfoType (Id='Id',
                                  CanonicalizationMethod=canonicalizationmethod,
                                  SignatureMethod=signaturemethod,
                                  Reference=[reference])

signaturevalue = amie.SignatureValueType (Id='Id',
                                          valueOf_='valueOf_')

amieobject = amie.ObjectType (MimeType='MimeType',
                              Id='Id',
                              Encoding='Encoding',
                              anytypeobjs_='anytypeobjs_',
                              valueOf_='valueOf_',
                              #mixedclass_='mixedclass_',
                              #content_='content_')
                              )                              

signature = amie.SignatureType (Id='Id',
                                SignedInfo=signedinfo,
                                SignatureValue=signaturevalue,
                                KeyInfo=keyinfo,
                                Object=[amieobject])


keyvalue = amie.KeyValueType (#DSAKeyValue='DSAKeyValue',
                              #RSAKeyValue='RSAKeyValue',
                              anytypeobjs_='anytypeobjs_',
                              valueOf_='valueOf_',
                              #mixedclass_='mixedclass_',
                              #content_='content_')
                              )




manifest = amie.ManifestType (Id='Id',
                              Reference=[reference])

signatureproperty = amie.SignaturePropertyType (Target='Target',
                                                Id='Id',
                                                anytypeobjs_='anytypeobjs_',
                                                valueOf_='valueOf_',
                                                #mixedclass_='mixedclass_',
                                                #content_='content_')
                                                )


signatureproperties = amie.SignaturePropertiesType (Id='Id',
                                                    SignatureProperty=[signatureproperty])


''' unclear
dsakeyvalue = amie.DSAKeyValueType (P='P',
                                    Q='Q',
                                    G='G',
                                    Y='Y',
                                    J='J',
                                    Seed='Seed',
                                    PgenCounter='PgenCounter')



#360 bits
#512 bits
#1024 bits
#2048 bits
rsakeyvalue = amie.RSAKeyValueType (Modulus='Modulus',
                                    Exponent='Exponent')
'''

volumeresource = amie.VolumeResource (units='units',
                                      description='description',
                                      storageUnit='storageUnit')

phaseresource = amie.PhaseResource (units='units',
                                    description='description',
                                    phaseUnit='phaseUnit')


usagerecord = amie.UsageRecordType (RecordIdentity=recordidentity,
                                    JobIdentity=jobidentity,
                                    UserIdentity=[useridentity],
                                    JobName=jobname,
                                    Charge=charge,
                                    Status=status,
                                    Disk=[disk],
                                    Memory=[memory],
                                    Swap=[swap],
                                    Network=[network],
                                    TimeDuration=[timeduration],
                                    TimeInstant=[timeinstant],
                                    ServiceLevel=[servicelevel],
                                    WallDuration=wallduration,
                                    CpuDuration=[cpuduration],
                                    NodeCount=nodecount,
                                    Processors=processors,
                                    EndTime=endtime,
                                    StartTime=starttime,
                                    MachineName=machinename,
                                    SubmitHost=submithost,
                                    Queue=queue,
                                    ProjectName=[projectname],
                                    Host=[host],
                                    PhaseResource=[phaseresource],
                                    VolumeResource=[volumeresource],
                                    Resource=[resource],
                                    ConsumableResource=[consumableresource],
                                    #extensiontype_='extensiontype_')
                                    )

jobusagerecord = amie.JobUsageRecord (RecordIdentity=recordidentity,
                                    JobIdentity=jobidentity,
                                    UserIdentity=[useridentity],
                                    JobName=jobname,
                                    Charge=charge,
                                    Status=status,
                                    Disk=[disk],
                                    Memory=[memory],
                                    Swap=[swap],
                                    Network=[network],
                                    TimeDuration=[timeduration],
                                    TimeInstant=[timeinstant],
                                    ServiceLevel=[servicelevel],
                                    WallDuration=wallduration,
                                    CpuDuration=[cpuduration],
                                    NodeCount=nodecount,
                                    Processors=processors,
                                    EndTime=endtime,
                                    StartTime=starttime,
                                    MachineName=machinename,
                                    SubmitHost=submithost,
                                    Queue=queue,
                                    ProjectName=[projectname],
                                    Host=[host],
                                    PhaseResource=[phaseresource],
                                    VolumeResource=[volumeresource],
                                    Resource=[resource],
                                    ConsumableResource=[consumableresource],
                                    #extensiontype_='extensiontype_')
                                      )

usagerecords = amie.UsageRecords (Usage=[usagerecord])


#    records.add_record(record)

#    records.export(sys.stdout, 0)

        
        
test(network, 'network')
test(disk, 'disk')
test(memory, 'memory')
test(swap, 'swap')
test(nodecount, 'nodecount')
test(processors, 'processors')
test(timeduration, 'timeduration')
test(timeinstant, 'timeinstant')
test(servicelevel, 'servicelevel')
test(cpuduration, 'cpuduration')
test(wallduration, 'wallduration')
test(endtime, 'endtime')
test(starttime, 'starttime')
test(machinename, 'machinename')
test(submithost, 'submithost')
test(host, 'host')
test(queue, 'queue')
test(jobname, 'jobname')
test(projectname, 'projectname')
test(status, 'status')
test(charge, 'charge')
test(jobidentity, 'jobidentity')
test(consumableresource, 'consumableresource')
test(resource, 'resource')
test(signaturevalue, 'signaturevalue')
test(x509issuerserial, 'x509issuerserial')
test(volumeresource, 'volumeresource')
test(phaseresource, 'phaseresource')


test(keyinfo, 'keyinfo')

test(useridentity, 'useridentity')

print
print "REST IS STILL BROKEN"
print
test(manifest, 'manifest')
test(amieobject, 'amieobject')
test(spkidata, 'spkidata')
test(pgpdata, 'pgpdata')
test(x509data, 'x509data')
test(retrievalmethod, 'retrievalmethod')
test(keyvalue, 'keyvalue')

test(digestmethod, 'digestmethod')
test(transforms, 'transforms')
test(transform, 'transform')
test(reference, 'reference')
test(signaturemethod, 'signaturemethod')
test(canonicalizationmethod, 'canonicalizationmethod')
test(signature, 'signature')
test(signedinfo, 'signedinfo')
test(recordidentity, 'recordidentity')

test(usagerecord, 'usagerecord')
test(jobusagerecord, 'jobusagerecord')
test(usagerecords, 'usagerecords')

#test(rsakeyvalue, 'rsakeyvalue')
#test(dsakeyvalue, 'dsakeyvalue')
test(signatureproperty, 'signatureproperty')

test(signatureproperties, 'signatureproperties')
