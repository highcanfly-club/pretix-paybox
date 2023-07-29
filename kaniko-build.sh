#!/bin/bash
#########################################################################
# © Ronan LE MEILLAT 2023
# released under the GPLv3 terms
#########################################################################
KANIKO_POD=$(kubectl -n $NAMESPACE get pods | grep "kaniko" | cut -d' ' -f1)
echo "NAMESPACE=$NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
kubectl -n $NAMESPACE delete pod $KANIKO_POD 1>/dev/null 2>/dev/null
tar -cv --exclude "node_modules" \
  --exclude "dkim.rsa" \
  --exclude "private" \
  --exclude "k8s" \
  --exclude ".git" --exclude ".github" --exclude-vcs \
  --exclude ".docker" \
  --exclude "_sensitive_datas" \
  --exclude "._*" \
  --exclude "build" -f - . | gzip -9 | kubectl run -n $NAMESPACE kaniko \
  --rm --stdin=true \
  --image=highcanfly/kaniko:latest --restart=Never \
  --overrides='{
  "apiVersion": "v1",
  "spec": {
    "containers": [
      {
        "name": "kaniko",
        "image": "highcanfly/kaniko:latest",
        "stdin": true,
        "stdinOnce": true,
        "args": [
          "-v","info",
          "--cache=true",
          "--dockerfile=Dockerfile'$EXT'",
          "--context=tar://stdin",
          "--skip-tls-verify",
          "--destination='$EXPECTED_REF'",
          "--image-fs-extract-retry=3",
          "--push-retry=3",
          "--use-new-run"
        ]
      }
    ],
    "restartPolicy": "Never"
  }
}'

#kubectl delete -n $NAMESPACE secret/registry-credentials
