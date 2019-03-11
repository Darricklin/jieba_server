import multiprocessing
bind = '0.0.0.0:5000'
timeout = 30
worker_class = 'gevent'

workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
# loglevel ="debug"
# access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
# errorlog = "/home/ec2-user/jiebafenci/gunicorn_error.log"
# accesslog = "/home/ec2-user/annotation/app/log/gunicorn_access.log"


