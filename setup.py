from setuptools import setup

setup(name='redpanda',
      version='0.1.0',
      description='Red Panda Game Framework',
      author='Wayne Moorefield',
      author_email='wayne.moorefield@gmail.com',
      packages=['redpanda',
                'redpanda.ecs',
                'redpanda.ecs.systems',
                'redpanda.parser',
                'redpanda.template',
      ]
)

