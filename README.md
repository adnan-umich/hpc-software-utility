# hpc-software-utility

## Usage
### CLI flags
* Collections
  * `-c`, `-c=Compilers`, `-c=Python`, `-c=Python,MPI,Bioinformatics`
* Filter
  * `-f=openmpi/4.1.4`
```
$ ./sw_util -c MPI -f open

MPI Ver.       Compiler        MPI Packages               Dependency
-------------  --------------  -------------------------  ------------
openmpi-4.1.2  intel-2022.1.2  phdf5/1.12.1               szip/2.1.1
openmpi-4.1.2  gcc-10.3.0      phdf5/1.12.1               szip/2.1.1
openmpi-4.1.6  intel-2022.1.2  fftw_mpi/3.3.10
openmpi-4.1.6  intel-2022.1.2  phdf5/1.12.1               szip/2.1.1
openmpi-4.1.6  gcc-10.3.0      phdf5/1.12.1               szip/2.1.1
openmpi-4.1.6  gcc-10.3.0      mpifileutils/0.10.2-arcts
openmpi-4.1.4  intel-2022.1.2  fftw_mpi/3.3.10
openmpi-4.1.4  intel-2022.1.2  parmetis/4.0.3
openmpi-4.1.4  gcc-10.3.0      phdf5/1.12.1               szip/2.1.1
openmpi-4.1.4  gcc-10.3.0      mpifileutils/0.10.2-arcts
```

## Building executable using poetry and pyinstaller
```
$ module load python
$ pip install poetry
$ poetry install
$ poetry shell
$ pip install pyinstaller
$ poetry run pyinstaller hpc-software-utility/__init__.py --hidden-import=tabulate --onefile --name <desired_executable_name> (ex. sw_util)
$ ./sw_util
```

## Running as a python application
```
$ module load python
$ pip install poetry
$ poetry install
$ poetry shell
$ python hpc-software-utility/__init__.py
```
