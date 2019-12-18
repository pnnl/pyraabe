PyRaabe
=======
PyRaabe is a package to automate [Raabe table](http://mae.engr.ucdavis.edu/wexler/lungs/LF53-Raabe/text.pdf) generation from a triangulated surface of an airway geometry. It relies heavily on the [Vascular Modeling Toolkit (VMTK)](http://www.vmtk.org/index.html) to extract a centerline from the 3D surface mesh and and subsequently computes the relevant attributes for the Raabe table, including length, diameter, bifurcation angle, and gravity angle.

Installation
------------
Use [``conda``](https://www.anaconda.com/download/) to create a virtual environment with required dependencies.

Ensure ``conda`` and ``anaconda-client`` are installed and updated:
```bash
conda install anaconda-client
conda update conda anaconda-client
```

Create the virtual environment:
```bash
conda create -n raabe -c vmtk python=3.6 itk vtk vmtk numpy pandas
```

Activate the virtual environment:
```
conda activate raabe
```

Install PyRaabe using [``pip``](https://pypi.org/project/pip/):
```bash
# clone/install
git clone https://github.com/pnnl/pyraabe.git
pip install pyraabe/

# direct
pip install git+https://github.com/pnnl/pyraabe
```

Usage:
------
Executing PyRaabe is quite simple. After installation, the command ``pyraabe`` will become available in your terminal. Usage overview is accessible via ``pyraabe --help`` or ``-h``, but all that needs to be supplied is a path to the input surface (.stl) and a path to the desired output folder. Note that the input surface must be open at the inlet and all outlets.
```bash
pyraabe input.stl output_dir/
```
A VMTK window will appear; simply follow the onscreen instructions to identify inlet and outlets. Specifying the single inlet first will allow all outlets to be defined automatically when prompted.

Both a centerline (.vtp) and Raabe table (.tsv) will be saved to the output directory.

Citing PyRaabe
-------------
If you would like to reference PyRaabe in an academic paper, we ask you include the following reference:
* PyRaabe, version 0.1.0 http://github.com/pnnl/pyraabe (accessed MMM YYYY)

Disclaimer
----------
This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the United States Government nor the United States Department of Energy, nor Battelle, nor any of their employees, nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the United States Government or any agency thereof, or Battelle Memorial Institute. The views and opinions of authors expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

PACIFIC NORTHWEST NATIONAL LABORATORY operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY under Contract DE-AC05-76RL01830
