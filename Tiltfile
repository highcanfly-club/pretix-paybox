#########################################################################
# © Ronan LE MEILLAT 2023
# released under the GPLv3 terms
#########################################################################
Namespace='pretix'

default_registry('ttl.sh/pretix-1hfsqk5')
Registry='ttl.sh/pretix-17az23'


os.putenv ( 'DOCKER_USERNAME' , 'ociregistry' ) 
os.putenv ( 'DOCKER_PASSWORD' , 'eiFoGjsUoh8h4e' ) 
os.putenv ( 'DOCKER_EMAIL' , 'none@example.org' ) 
os.putenv ( 'DOCKER_REGISTRY' , Registry ) 
os.putenv('NAMESPACE',Namespace)

allow_k8s_contexts('kubernetesOCI')

# k8s_yaml('deploy.yaml')
yaml = helm(
  'helm/pretix',
  # The release name, equivalent to helm --name
  name='pretix-4.20',
  # The namespace to install in, equivalent to helm --namespace
  namespace='pretix',
  # The values file to substitute into the chart.
  values=['./_values.yaml'],
  )
k8s_yaml(yaml)

custom_build('highcanfly/pretix','./kaniko-build.sh',[
  'developer', './docker-entrypoint.sh','./data','./pretix_paybox'
],skips_local_docker=True, 
  live_update=[
    sync('./pretix_paybox/.', '/pretix-paybox/pretix_paybox'),
    run('sudo -u pretixuser pretix collectstatic --noinput && sudo -u pretixuser pretix compress', trigger='./pretix_paybox/static'),
    run('cd /pretix-paybox && make', trigger='./pretix_paybox/locale'),
    run('supervisorctl -s unix:///tmp/supervisor.sock restart pretixweb', trigger='./pretix_paybox')
])


