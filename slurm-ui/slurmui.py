import os
from flask import Flask
from flask_restful import Resource, reqparse, Api
import pwd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, desc
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pymysql
import pyslurm

pymysql.install_as_MySQLdb()

DB_HOST = 'localhost'
DB_USER = 'slurm'
DB_PASS = os.environ.get('SLURM_DB_PASS', 'AlsoReplaceWithASecurePasswordInTheVault')
SLURM_CLUSTER_NAME = os.environ.get('SLURM_CLUSTER_NAME', 'deepops')
DB_NAME = 'slurm_acct_db'
ASSOC_TABLE_NAME = SLURM_CLUSTER_NAME + '_assoc_table'
JOB_TABLE_NAME = SLURM_CLUSTER_NAME + '_job_table'

app = Flask(__name__, static_folder='static', static_url_path='')
app.config["DEBUG"] = False

api = Api(app)

engine = create_engine('mysql://%s:%s@%s/%s' %(DB_USER,DB_PASS,DB_HOST,DB_NAME))
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    
    Base.metadata.create_all(bind=engine)


class Slurm_Queue(Resource):
    def get(self):
        j = pyslurm.job()
        data = j.get()
        for id,job in data.items():
            job['user_name'] = pwd.getpwuid(job['user_id'])[0]
        return data

class Slurm_Statistics(Resource):
    def get(self):
        s = pyslurm.statistics()
        data = s.get()
        return data

class Slurm_Nodes(Resource):
    def get(self):
        n = pyslurm.node()
        data = n.get()
        return data

class Slurm_Partitions(Resource):
    def get(self):
        p = pyslurm.partition()
        data = p.get()
        return data


class Assoc(Base):
    __tablename__ = ASSOC_TABLE_NAME
    id_assoc = Column(Integer, primary_key=True)
    user = Column(String(128))
    acct = Column(String(128))
    partition = Column(String(128))

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        me = dict()
        me['id_assoc']=int(self.id_assoc)
        me['user']= self.user
        me['acct']= self.acct
        me['partition']= self.partition
        return me

class Job(Base):
    __tablename__ = JOB_TABLE_NAME
    id_job =  Column(Integer, primary_key=True)
    id_user = Column(Integer)
    id_assoc = Column(Integer)
    job_name = Column(String(1024))
    cpus_req = Column(Integer)
    mem_req = Column(Integer)
    account = Column(String(128))
    nodelist = Column(String(2048))
    partition = Column(String(128))
    nodes_alloc = Column(Integer)
    timelimit = Column(Integer)
    time_submit = Column(Integer)
    time_start  = Column(Integer)
    time_end  = Column(Integer)
    priority  = Column(Integer)
    state = Column(Integer)

    def __repr__(self):
        return str(self.to_dict())

    def conv_timestamp(self,time):
        rval =""
        if time>0:
            rval = datetime.fromtimestamp(time).ctime()
        return rval

    def conv_timelimit(self, minutes):
        hours, mins = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return "%dd:%dh:%dm" %(days,hours,mins)

    def to_dict(self):
        states = [
          'JOB_PENDING',
          'JOB_RUNNING',
          'JOB_SUSPENDED',
          'JOB_COMPLETE',
          'JOB_CANCELLED',
          'JOB_FAILED',
          'JOB_TIMEOUT',
          'JOB_NODE_FAIL',
          'JOB_PREEMPTED',
          'JOB_BOOT_FAIL',
          'JOB_DEADLINE'
        ]
        me = dict()
        me['id_job']=int(self.id_job)
        me['id_user']= int(self.id_user)
        me['id_assoc']= int(self.id_assoc)
        me['job_name']= self.job_name
        me['cpus_req']= int(self.cpus_req)
        me['mem_req']= int(self.mem_req)
        me['account']= self.account
        me['nodelist']= self.nodelist
        me['partition']= self.partition
        me['nodes_alloc']= int(self.nodes_alloc)
        me['timelimit']=self.conv_timelimit(int(self.timelimit))
        me['time_submit']=self.conv_timestamp(int(self.time_submit))
        me['time_start']=self.conv_timestamp(int(self.time_start))
        me['time_end']=self.conv_timestamp(int(self.time_end))
        me['priority']=int(self.priority)
        self.state= max(min(10, int(self.state)),0)
        me['state'] = states[self.state]
        return me



class UserAssocApi(Resource):
    def get(self):
        parser =reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()
        if args['name']:
            userlist = Assoc.query.filter(Assoc.user == args['name']).all()
        else:
            userlist = Assoc.query.filter(Assoc.user != "").all()
        ul = list()
        for user in userlist:
            ul.append(user.to_dict())
        return ul

class JobHistoryApi(Resource):

    def get(self):
        parser =reqparse.RequestParser()
        parser.add_argument('limit', type=int, default=10, location='args')
        parser.add_argument('offset', type=int, default=0, location='args')
        parser.add_argument('user', location='args')
        parser.add_argument('associd', type=int, default=None, location='args')
        parser.add_argument('state', type=int, default=None, location='args')
        parser.add_argument('startbefore', location='args')
        parser.add_argument('startafter', location='args')
        parser.add_argument('endafter', location='args')
        parser.add_argument('endbefore', location='args')
        parser.add_argument('jobname', location='args')
        parser.add_argument('partition', location='args')
        parser.add_argument('jobid', type=int, location='args')
        args = parser.parse_args()
        criterion = list()

        if args['user']:
            userlist = Assoc.query.filter(Assoc.user==args['user']).all()
            id_list = list()
            for assoc in userlist:
                id_list.append(assoc.id_assoc)
            criterion.append(Job.id_assoc.in_(id_list))
        if args['associd']:
            criterion.append(Job.id_assoc==args['associd'])
        if args['jobname']:
            criterion.append(Job.job_name==args['jobname'])
        if args['jobid']:
            criterion.append(Job.id_job==args['jobid'])
        if args['partition']:
            criterion.append(Job.partition==args['partition'])
        if args['state']:
            criterion.append(Job.state==args['state'])

        userlist = Assoc.query.all()
        joblist = Job.query.filter(*criterion).order_by(desc(Job.time_submit)).limit(args['limit']).offset(args['offset']).all()

        users = dict()
        for user in userlist:
            users[user.id_assoc]=user.user
        rlist = list()
        for job in joblist:
            jd = job.to_dict()
            jd['user_name'] = users.get(jd['id_assoc'], "")
            rlist.append(jd)
        return rlist      

def start():
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    init_db()

    api.add_resource(JobHistoryApi, '/history')
    api.add_resource(UserAssocApi, '/users')

    api.add_resource(Slurm_Queue, '/queue')
    api.add_resource(Slurm_Nodes, '/nodes')
    api.add_resource(Slurm_Partitions, '/partitions')
    api.add_resource(Slurm_Statistics, '/stats')
    app.run(host="0.0.0.0", port=45000)

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    start()
