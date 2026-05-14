export LITELLM_KEY=$(~/bin/secret.sh get dss-k3s-01 LITELLM_MASTER_KEY)
curl -s http://litellm.default.svc.cluster.local:4000/v1/models -H "Authorization: Bearer $LITELLM_KEY"
