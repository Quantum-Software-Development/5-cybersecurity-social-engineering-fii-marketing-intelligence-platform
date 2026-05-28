# macOS Big Data Stack Installation Guide

This guide explains how to install OpenJDK, Hadoop, HDFS, YARN, Spark, and optional `mrjob` support on macOS for a local single-node lab environment.

## Prerequisites

The system should be macOS with terminal access, Homebrew installed, and internet access for package downloads.

## Install OpenJDK

Spark and Hadoop require Java, and OpenJDK is the standard open-source distribution used on macOS as well.

Install OpenJDK with Homebrew:

```bash
brew install openjdk@11
```

Link it into the shell environment:

```bash
echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 11)' >> ~/.zshrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

Verify Java:

```bash
java -version
```

## Install Hadoop

Download and extract Hadoop manually on macOS.

```bash
cd ~
curl -O https://downloads.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz
tar -xzf hadoop-3.4.0.tar.gz
mv hadoop-3.4.0 hadoop
```

Set Hadoop variables:

```bash
echo 'export HADOOP_HOME=$HOME/hadoop' >> ~/.zshrc
echo 'export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop' >> ~/.zshrc
echo 'export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin' >> ~/.zshrc
source ~/.zshrc
```

Set Java for Hadoop:

```bash
sed -i '' "s|^export JAVA_HOME=.*|export JAVA_HOME=$JAVA_HOME|" \
  $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

## Configure HDFS

Edit `core-site.xml`:

```bash
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```

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

```xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///Users/USER/hadoop_data/nn</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///Users/USER/hadoop_data/dn</value>
  </property>
</configuration>
```

Create data directories:

```bash
mkdir -p /Users/USER/hadoop_data/nn
mkdir -p /Users/USER/hadoop_data/dn
```

## Configure YARN for MapReduce

Create `mapred-site.xml`:

```bash
cp $HADOOP_HOME/etc/hadoop/mapred-site.xml.template \
   $HADOOP_HOME/etc/hadoop/mapred-site.xml
nano $HADOOP_HOME/etc/hadoop/mapred-site.xml
```

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

```xml
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
</configuration>
```

These settings enable MapReduce on YARN in a single-node Hadoop setup.

## Start Hadoop on macOS

Format the NameNode once:

```bash
hdfs namenode -format
```

Start HDFS daemons:

```bash
hdfs --daemon start namenode
hdfs --daemon start datanode
hdfs --daemon start secondarynamenode
```

Start YARN daemons directly:

```bash
yarn --daemon start resourcemanager
yarn --daemon start nodemanager
```

Check processes:

```bash
jps
```

Direct daemon commands are often more practical on local macOS labs because `start-yarn.sh` may rely on SSH to `localhost`.

## Install Spark

Spark can be installed with Homebrew or from the Apache tarball.

Homebrew option:

```bash
brew install apache-spark
```

Manual option:

```bash
cd ~
curl -O https://downloads.apache.org/spark/spark-4.1.2/spark-4.1.2-bin-hadoop3.tgz
tar -xzf spark-4.1.2-bin-hadoop3.tgz
mv spark-4.1.2-bin-hadoop3 spark
```

Set Spark variables if using the manual installation:

```bash
echo 'export SPARK_HOME=$HOME/spark' >> ~/.zshrc
echo 'export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' >> ~/.zshrc
source ~/.zshrc
```

Test Spark:

```bash
spark-shell
```

## Install mrjob

Create a Python virtual environment and install `mrjob`:

```bash
python3 -m venv venv-mrjob
source venv-mrjob/bin/activate
pip install "mrjob>=0.7,<0.8"
```

Run locally:

```bash
python my_job.py input.txt
```

Run on Hadoop:

```bash
python my_job.py -r hadoop hdfs:///user/USER/input.txt
```
