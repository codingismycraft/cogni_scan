
# How to Run Niftiviewer Using Vagrant

Niftiviewer is an easy-to-use desktop application designed with tkinter that
lets you analyze a nifti file and predict the possibility of the file's subject
developing dementia in the future.

You can effortlessly run Niftiviewer from a virtual machine that is managed by
a Vagrant file located in this directory. You can use any Operating system that
supports `virtualbox` and `vagrant` such as MS-Windows or any flavor of Linux.

## Prerequisites:

- Install [Vagrant](https://developer.hashicorp.com/vagrant/docs/installation).

- Install [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## Getting Started

Follow these steps to copy the code to your desired directory:

```
mkdir ~/nifti-files
mkdir cogni_scan
cd cogni_scan
git clone https://git@github.com:neuproscan/cogni_scan.git
cd cogni_scan
vagrant up
vagrant ssh
```

To run NiftiViewer from the vagrant box, enter:

```
nv
```

## Opening a nifti file

To access a nifti file with Niftiviewer, add it to the `~/nifti-files`
directory you created earlier. This will make it appear in the
`/cogni_scan/shared` directory from inside the vagrant box.

After adding a nifti file to the `nifti-files` directory, you can then open it
within the NiftiViewer application using the open option from the main menu.

## Making predictions

To generate a prediction for the currently open nifti file, go to `Options |
Make predictions` in the main menu. This will run the file through all
available models, and update the screen with the predicted chance of the
subject developing dementia in the future.


## Troubleshoot

If you encounter any issues while cloning the repository, launching the Vagrant
box, or using the NiftiViewer application, please visit our [FAQs](insert link)
page or [contact support](insert link).

Remember to frequently check this repository for updates and improvements to
the NiftiViewer application.

## Feedback

Your feedback is very valuable to us! If you have any suggestions for
improvements or new features for the NiftiViewer application, please feel free
to create an issue on our GitHub repository.

`git clone https://github.com/neuproscan`

