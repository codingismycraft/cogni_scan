# Running niftiviewer from Vagrant

Niftiviewer is a front-end desktop application (written in tkinter) which
allows the user to pass a nifti file through the set of the available models
and get a prediction about how possible is for the subject to develop dementia
in the following years.  

To keep things easier to run NiftiViewer is bundled to run from a VM that is
managed from the Vagrant file that can be found in this directory.

### Requirements:

- [Vagrant](https://developer.hashicorp.com/vagrant/docs/installation)

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Instructions

Clone the code to any directory you like:

```
mkdir ~/nifti-files
mdikr cogni_scan
cd cogni_scan
git clone https://github.com/codingismycraft/cogni_scan.git
vagrant up
vagrant ssh
```

The first time you are running the code you need to create the database (while
on the vagrant box):

```
updatedb
```

To run the NiftiViewer (while on the vagrant box):
```
nv
```

To make a nifti file accessible to Niftiviewer you must copy it to the the
`~/nifti-files` directory that you created in the first step; doing so will
make it visible under the `/cogni_scan/shared` directory insider the vagrant
box.





