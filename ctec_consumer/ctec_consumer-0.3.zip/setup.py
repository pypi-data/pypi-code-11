import distutils.core

version = '0.3'

distutils.core.setup(
        name='ctec_consumer',
        version=version,
        packages=['ctec_consumer', 'ctec_consumer.models', 'ctec_consumer.dummy', 'ctec_consumer.dummy.models',
                  'ctec_consumer.gevent', 'ctec_consumer.gevent.models'],
        author='ZhangZhaoyuan',
        author_email='zhangzhy@chinatelecom.cn',
        url='http://www.189.cn',
        description='189 rabbitMQ consumer',
        requires=['kombu', 'gevent']
)
