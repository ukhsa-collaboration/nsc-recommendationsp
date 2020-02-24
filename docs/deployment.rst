==========
Deployment
==========

This project contains an OpenShift template. To add it to the catalog, run::

    oc create -f openshift-template.yaml

When adding it to the project, make the initial configuration using the interface
parameters. Most defaults should be acceptable; the key settings to update are:

* **Git reference**: set this to the tag or branch in git for this deployment
* **Application hostname**: the url for this deployment
* **Django configuration**:

The project can be configured further using ConfigMap and Secret objects as detailed in
:doc:`settings`.
