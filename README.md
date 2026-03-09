# ICARUS POT accounting scripts

## Setting it up

This is a guide updated to March 9th. The setup follows different steps.

> **IMPORTANT** Do not clone this repository AS-IS. Please follow these instruction, making sure that at the end it all will work properly. 

### 1. Installing `conda`

The first step is to have`conda` running on the `icarusgpvm` servers. This is needed to have a python environment working outside of the SL& container. `conda` OG is not allowed by FNAL since is not open-source, and so we need to use its open-source twin `conda-forge`. You can download it from the official site or using the command (from within the `icarusgpvm`) below

```bash
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
```

It is recomended you install the miniconda in your `/exp/icarus/app/users/$USER/` path, by passing `/exp/icarus/app/users/$USER/miniconda3/` when asked during the installation process, that you run with

```bash
sh Miniforge3-$(uname)-$(uname -m).sh
```

> **Important** You should pass the path without env. variables, so for example if your `$USER` was `johndoe` you would pass `/exp/icarus/app/user/johndoe/miniforge3/`.

At this point in order to have the `conda` script available, you sould run the following command

```bash
source /exp/icarus/app/user/$USER/miniforge3/etc/profile.d/conda.sh
```
Now you are able to create the `conda` environment.

### 2. Creating the `conda` environment

You can create the conda environment now with the command

```bash
conda create -n runCo python=3.12
```

After the environment is created, you can activate it with

```bash
conda activate runCo
```

### 3. Installing the needed software

You can install the required python packages with the command 

```bash
pip install beautifulsoup4 Bottleneck brotli click lxml mplhep numexpr pandas pyOpenSSL PyQt5 requests sip SQLAlchemy tornado wheel
```

> **Note** This environment can be used also for the E-Log web scraping tools, described in [ascarpel/ELOGWebScraping](https://github.com/ascarpel/ELOGWebScraping). 

### 4. Installing the POT code and setting it up

You should create a `runCo/` directory. It's suggested you create it in the `/exp/icarus/app/users/$USER/` path. 

```bash
mkdir -p /exp/icarus/app/users/$USER/runCo
```

Once created, do
```bash 
cd /exp/icarus/app/users/$USER/runCo
```

#### 4.1 Installing Oracle instantclient

Before continuing on with the normal installation, we first get the 

To commit the POT to the Fermilab directorate performance database you will need to 
1. Be granted access to the actual database with your Fermilab SERVICE account. Ask fo help on #icarus_runco or #icarus-commissioning-rc slack channels. Those are 
    - [Experiments Operations Performance Database/develop-area](https://ccdapps-dev.fnal.gov/pls/apex/f?p=104), and
    - [Experiments Operations Performance Database/production-area](https://ccdapps-prod.fnal.gov/pls/apex/f?p=104).
2. Have the Oracle instantclient software libraries installed. 

For the latter, you can get them here (make sure you are in the `/exp/icarus/app/users/$USER/runCo` path)

```bash
wget https://download.oracle.com/otn_software/linux/instantclient/218000/instantclient-basic-linux.x64-21.8.0.0.0dbru.zip
```

Once downloaded, you can unzip them with 

```bash
unzip instantclient-basic-linux.x64-21.8.0.0.0dbru.zip
```

#### 4.2 Git repository and POT scripts

In that directory you are going to create a `setup.sh` file. This will be the script you are going to run each time you need to use the POT accounting scripts. 

To create the setup.sh script, start with the command

```bash 
echo "source /exp/icarus/app/users/${USER}/miniforge3/etc/profile.d/conda.sh" > setup.sh
echo "conda activate runCo" >> setup.sh
```

This will add the lines 

```bash
source /exp/icarus/app/users/${USER}/miniforge3/etc/profile.d/conda.sh
conda activate runCo
```
to the script.

Add also the following lines to the `setup.sh` script

```bash
export USER_BASE=/exp/icarus/app/users/$(id -un)/runCo

# === Oracle Instant Client ===
export ORACLE_HOME=${USER_BASE}/instantclient_21_8
export LD_LIBRARY_PATH=${ORACLE_HOME}:$LD_LIBRARY_PATH
export PATH=${ORACLE_HOME}:$PATH

export beamdburl=https://dbdata1vm.fnal.gov:9443/ifbeam/data
export gatewayhostname=icarus-gateway03.fnal.gov
export ICARUSACCOUNT=ICARUS_DETECTOR_INTERFACE
export ICARUSPWD=Icrs63_cff

export POT_DIR=${USER_BASE}/potAccounting
export potDir=$POT_DIR
cd $POT_DIR
```

#### 4.3 Cloning THIS repository 

At this point you can clone this repository. Make sure to be in the `/exp/icarus/app/users/$(id -un)/runCo` path, and run 

```bash
git clone https://github.com/mattiasotgia/ICARUSPOTAccounting.git potAccounting
```

> **Remark** Please note that the directory where the repository will be cloned won't be named `ICARUSPOTAccounting`, but it will be named `potAccounting`

At this point you should have the scripts installed and ready to be used

## Running the code _the first time_

Set up the code sourcing the `setup.sh` script, run 

```bash 
source setup.sh
```
You'll find yourself in the `potAccounting` directory. From there you'll want to create some directories that are needed for the scripts to work

```bash
mkdir fig dbase
```

Finally you will need to create an initial `.db` file. You can either
1.  Create a new one with `python CreateDB.py`, or
2.  Copy from existing one (**suggested** approach, will work most of the times), for example 
```bash
cp /exp/icarus/app/users/msotgia/runCo/potAccounting/share/RunSummary.db ${potDir}/dbase/
```

Now you're all set up, and the instruction are the same for the first and the other times, that you can find in the next section. 

## Running the POT accounting script(s)

To have the POT accounting for the week you'll need to do three steps: 1. get the latest `DAQInterface` log file and parse it correctly, 2. Update the delivered/collected POT databases from the beam monitoring database and 3. draw the plots. 

### 1. Getting and parsing the `DAQInterface` log file
The `DAQInterface` log file (e.g., `/daq/log/DAQInterface_partition1.log`) contains typically $\mathcal O(1\times10^6)$ lines. We parse this file and save the run start/stop times into a database, before we query BNB/NuMI DBs. This is done in two steps.

First you get the DAQ log file, by running 
```bash
source getDAQLog.sh
```

After this is done, you can parse it by running 
```bash
python ParseDAQLog.py -i YYYY-MM-DD -f YYYY-MM-DD
```
This has the following options
- `-i YYYY-MM-DD`,  which is the day from which to start updating
- `-f YYYY-MM-DD`, which is the day up to which update

## 2. Update delivered/collected POT

This is done in two steps. First you run the command to update the delivered POT

```bash
python pot_account.py update-daily-pot YYYY-MM-DD YYYY-MM-DD <True/False>
```
Here
- `YYYY-MM-DD YYYY-MM-DD` are the start and the end date to be updated
- `True/False` are booleans for _override_ option; `True` if you want to update the current table with new values.

Then you update the collected POT,

```bash 
python pot_account.py update-daily-runs YYYY-MM-DD YYYY-MM-DD <True/False>
```
Here 
- `YYYY-MM-DD YYYY-MM-DD` are the start and the end date to be updated
- `True/False` are booleans for "override" option; `True` if you want to update the current table with new values

## 3. Draw plots

To draw the plots (which are produced in the `fig/` directory under the `potAccounting` path) you can run 

```bash 
python pot_account.py make-daq-plots YYYY-MM-DD YYYY-MM-DD
```
Here, like for the other commands, 
- `YYYY-MM-DD YYYY-MM-DD` are the start and the end date to be updated

There is an handy script for running al these steps together, the `RunAllStep.sh` 

Inside the structure is quite simple. Declared are two variables, `start` and `end` that are passed to all the steps, 

```bash
start="2026-01-09"
end="2026-03-01"

source getDAQLog.sh
python ParseDAQLog.py -i ${start} -f ${end}
python pot_account.py update-daily-pot ${start} ${end} True
python pot_account.py update-daily-runs ${start} ${end} True
python pot_account.py make-daq-plots ${start} ${end}
```

All the plots refer to the period you have selected. However one additional plot is produced adding up all the data from the very beginning of data taking (start of Run 1) up to the last day. This is produced, provided the data is present in the database.

Custom figure size/styling of the plots can be set by changing the script in `plotting/plot_utils.py`

## Commit weekly report to Fermilab directorate performance database

Each week the runCo is expected to also upload the POT data to the databases. There is a script that query the `dbase/RunSummary.db` file (this requres the previous steps to be run) that automatically upload the data to both 
- [Experiments Operations Performance Database/develop-area](https://ccdapps-dev.fnal.gov/pls/apex/f?p=104), and
- [Experiments Operations Performance Database/production-area](https://ccdapps-prod.fnal.gov/pls/apex/f?p=104).

You need to run it twice, one for the develop-area (for debugging purpouses) 
```bash
python UpdateFermiDB.py -i YYYY-MM-DD --dev
```
and another one for the production-area
```bash
python UpdateFermiDB.py -i YYYY-MM-DD --prod
```

The options for the `UpdateFermiDB.py` scripts are 
- `-i YYYY-MM-DD`, which is the start day (__should be Monday__)
- `-f (optional)`, which is the end date (if not set, will be automatically set to Sunday)
- `--no_commit`, prevents the scripts to upload the data to the database, for testing the script before you update date the DB. 

You can check the committed data from 
- [Experiments Operations Performance Database/develop-area](https://ccdapps-dev.fnal.gov/pls/apex/f?p=104), and
- [Experiments Operations Performance Database/production-area](https://ccdapps-prod.fnal.gov/pls/apex/f?p=104).
You will need VPN if you are offsite.  If you need a permission, contact computing division for the access. 
