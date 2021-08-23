# proj_MRI: project timetable for MRI scanning


**proj_MRI** is a tool written in Python to help researchers to design a timetable for scannig a large number of animals. 

Right now, the proj_MRI is designed for MMoTH group to predict the MRI scanning timetable at the University of Kentucky. 

## Installation
To use **proj_MRI**, first the repository needs to be downloaded from github [repository](https://github.com/HosseinSharifii/proj_MRI). 

To clone the repository:
1. In terminal prompt, navigate to an empty folder that you want to download the repository into. 

2. execute below command:

`$ git clone https://github.com/HosseinSharifii/proj_MRI.git`

3. In couple of seconds you will have the repository downloaded into your local computer. 

## Dependencies

**proj_MRI** uses following python modules:
1. [os](https://docs.python.org/3/library/os.html)
2. [JSON](https://docs.python.org/3/library/json.html)
3. [sys](https://docs.python.org/3/library/sys.html)
4. [NumPy](https://numpy.org/)
5. [pandas](https://pandas.pydata.org/)
6. [datetime](https://docs.python.org/3/library/datetime.html)
7. [calendar](https://docs.python.org/3/library/calendar.html)
8. [PyCap](https://pycap.readthedocs.io/en/latest/index.html)

Usually, the first 7 modules are included in [anaconda](https://www.anaconda.com/) environment and thus you don't need to install them again. 

[PyCap](https://pycap.readthedocs.io/en/latest/index.html) modules is the only one you need to manually install on your computer. To do that use [pip](https://pypi.org/project/pip/) command:

`$ pip install PyCap`
[PyCap](https://pycap.readthedocs.io/en/latest/index.html) is an interface to the [REDCap](https://www.project-redcap.org/) Application Programming Interface (API).

## Documentation
