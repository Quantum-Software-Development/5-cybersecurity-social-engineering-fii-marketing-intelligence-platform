# Big Data Stack Installation Guide

This document explains how to install and configure OpenJDK, Hadoop, HDFS, YARN, Spark, and optional `mrjob` support on a single-node Ubuntu environment running on a Mac through a virtual machine or similar setup.

## Check Ubuntu Version

If Ubuntu is running on a Mac through a virtual machine, the first step is to verify the Ubuntu release before choosing package versions and installation commands.

Run one of the following commands in the Ubuntu terminal:

```bash
lsb_release -a
```

or:

```bash
cat /etc/os-release
```

Typical output includes the distribution name, release number, and codename, such as Ubuntu 22.04 LTS or Ubuntu 24.04 LTS.

## Prerequisites

The installation assumes a recent Ubuntu system, terminal access, sudo privileges, and internet access for downloading packages and binaries.

Update the package index and existing packages before beginning the installation:

```bash
sudo apt update && sudo apt upgrade -y
```

## Install OpenJDK

Hadoop and Spark require Java, and OpenJDK is the open-source JDK commonly used for this stack.

Install OpenJDK 11:

```bash
sudo apt install -y openjdk-11-jdk
```

Verify the installation:

```bash
java -version
```

Set `JAVA_HOME` and update the shell path:

```bash
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

## Install Hadoop

A single-node Hadoop installation provides HDFS for storage and YARN for resource management on the same machine

### Download and extract Hadoop 🐘

```bash
cd ~
wget https://downloads.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz
tar -xzf hadoop-3.4.0.tar.gz
mv hadoop-3.4.0 hadoop
```

Set Hadoop environment variables:

```bash
echo 'export HADOOP_HOME=$HOME/hadoop' >> ~/.bashrc
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop' >> ~/.bashrc
echo 'export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin' >> ~/.bashrc
source ~/.bashrc
```

Point Hadoop to the installed Java runtime:

```bash
sed -i "s|^export JAVA_HOME=.*|export JAVA_HOME=$JAVA_HOME|" \
  $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

### Configure HDFS

Edit `core-site.xml`:

```bash
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```

Use the following content:

```xml
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://localhost:9000</value>
  </property>
</configuration>
```

Edit `hdfs-site.xml`:

```bash
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```

Use the following content, replacing `USER` with the Ubuntu username:

```xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///home/USER/hadoop_data/nn</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///home/USER/hadoop_data/dn</value>
  </property>
</configuration>
```

Create the HDFS data directories:

```bash
mkdir -p /home/USER/hadoop_data/nn
mkdir -p /home/USER/hadoop_data/dn
```

These settings create a single replica and store NameNode and DataNode data on the local filesystem.

### Configure YARN for MapReduce

Create `mapred-site.xml` from the template:

```bash
cp $HADOOP_HOME/etc/hadoop/mapred-site.xml.template \
   $HADOOP_HOME/etc/hadoop/mapred-site.xml
nano $HADOOP_HOME/etc/hadoop/mapred-site.xml
```

Use the following content:

```xml
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>
```

Edit `yarn-site.xml`:

```bash
nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
```

Use the following content:

```xml
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
</configuration>
```

This configuration tells Hadoop to execute MapReduce jobs on YARN and enables the shuffle service required by reducers.

### Format HDFS and start Hadoop

Format the NameNode once before the first startup:

```bash
hdfs namenode -format
```

Start HDFS daemons:

```bash
hdfs --daemon start namenode
hdfs --daemon start datanode
hdfs --daemon start secondarynamenode
```

Start YARN daemons:

```bash
yarn --daemon start resourcemanager
yarn --daemon start nodemanager
```

Check the Java processes:

```bash
jps
```

A correct single-node setup should list `NameNode`, `DataNode`, `SecondaryNameNode`, `ResourceManager`, and `NodeManager`.[cite:98]

### Test HDFS

Create and upload a sample file:

```bash
echo "Hello Hadoop ! 🌺 Yo HDFS  ! Aloha Yarn 🏄‍♀️ ! Will be Forever Loving Jah  🇯🇲!!!" > test.txt
hdfs dfs -mkdir -p /user/$USER
hdfs dfs -put test.txt /user/$USER
hdfs dfs -ls /user/$USER
```

If the file appears in the listing, HDFS is operating correctly.

## Use YARN for MapReduce

YARN becomes useful after the required daemons are running and the MapReduce framework is configured to use it.

### Optional JobHistory server

To track completed MapReduce jobs in the web interface, start the JobHistory server:

```bash
mr-jobhistory-daemon.sh start historyserver
```

The JobHistory service commonly uses port 19888 for its web UI.

### Run a built-in MapReduce example

Locate the Hadoop examples JAR:

```bash
find $HADOOP_HOME -name "hadoop-mapreduce-examples*.jar"
```

Run the `pi` example on YARN:

```bash
yarn jar \
  $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.0.jar \
  pi 10 1000
```

This submits a MapReduce job through YARN so it can be monitored through the terminal output and the ResourceManager interface.

## Install Spark

Apache Spark can run with Hadoop libraries and access HDFS and YARN when installed with a Hadoop-compatible distribution.

### Download and configure Spark

```bash
cd ~
wget https://downloads.apache.org/spark/spark-4.1.2/spark-4.1.2-bin-hadoop3.tgz
tar -xzf spark-4.1.2-bin-hadoop3.tgz
mv spark-4.1.2-bin-hadoop3 spark
```

Set Spark environment variables:

```bash
echo 'export SPARK_HOME=$HOME/spark' >> ~/.bashrc
echo 'export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' >> ~/.bashrc
source ~/.bashrc
```

### Run Spark

Start the Spark shell in local mode:

```bash
spark-shell
```

Spark standalone mode can also be started with:

```bash
start-master.sh
start-worker.sh spark://localhost:7077
```

Submit the bundled `pi.py` example:

```bash
$SPARK_HOME/bin/spark-submit \
  --master spark://localhost:7077 \
  $SPARK_HOME/examples/src/main/python/pi.py 10
```

Spark distributions built for Hadoop 3 are designed to work with Hadoop client libraries and common HDFS/YARN workflows

## Install mrjob for Python MapReduce

`mrjob` is a Python library that makes it easier to write MapReduce jobs and run them locally or on Hadoop.

### Create a virtual environment

```bash
cd ~/projects/mrjob-demo
python3 -m venv venv-mrjob
source venv-mrjob/bin/activate
```

### Install mrjob

```bash
pip install "mrjob>=0.7,<0.8"
```

### Run locally

```bash
python my_job.py input.txt
```

### Run on Hadoop/YARN

```bash
python my_job.py -r hadoop hdfs:///user/USER/input.txt
```

In Hadoop runner mode, `mrjob` uses Hadoop Streaming to execute Python-based MapReduce jobs on the cluster.

## Troubleshooting Notes

If `start-yarn.sh` fails with an SSH connection error on a local environment, starting `resourcemanager` and `nodemanager` directly with `yarn --daemon start ...` is often more appropriate for a simple single-node lab setup.

If YARN services fail to remain active, inspect the log files inside `$HADOOP_HOME/logs` because malformed XML in `mapred-site.xml` or `yarn-site.xml` can prevent the daemons from starting.

Warnings about the native Hadoop library on macOS or some local environments do not necessarily indicate a fatal error because Hadoop can fall back to built-in Java classes.
