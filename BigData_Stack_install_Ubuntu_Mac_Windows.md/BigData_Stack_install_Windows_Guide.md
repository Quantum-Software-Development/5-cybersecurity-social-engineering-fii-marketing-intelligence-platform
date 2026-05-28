# Windows Big Data Stack Installation Guide

This guide explains how to install OpenJDK, Hadoop, HDFS, YARN, Spark, and optional `mrjob` support on Windows for a learning environment.

## Prerequisites

The system should be Windows 10 or Windows 11 with administrator access, internet access, and a tool such as 7-Zip for extracting archives.

## Install OpenJDK

Java is required by both Hadoop and Spark, and a supported JDK must be configured in the system environment variables.

Install an OpenJDK distribution, then define `JAVA_HOME` in the Environment Variables panel so it points to the JDK installation directory.

Typical example:

```text
JAVA_HOME=C:\Program Files\Java\jdk-17
```

Add Java to `Path`:

```text
%JAVA_HOME%\bin
```

Verify in Command Prompt:

```cmd
java -version
```

## Install Hadoop and Spark directories

Windows setups commonly use explicit folders such as `C:\hadoop` and `C:\Spark` for extracted binaries and helper files.

Create directories:

```cmd
cd \
mkdir hadoop
mkdir Spark
```

Download and extract Spark built for Hadoop into `C:\Spark`, then define `SPARK_HOME` to that installation directory.

Example:

```text
SPARK_HOME=C:\Spark\spark-4.x.x-bin-hadoop3
```

Add Spark to `Path`:

```text
%SPARK_HOME%\bin
```

## Hadoop helper binaries on Windows

Windows Spark and Hadoop lab guides commonly require `winutils.exe` in `C:\hadoop\bin` for compatibility with Hadoop-related file operations.

Define `HADOOP_HOME`:

```text
HADOOP_HOME=C:\hadoop
```

Add Hadoop to `Path`:

```text
%HADOOP_HOME%\bin
```

## Install Spark

After extraction and environment variable setup, Spark can be launched from Command Prompt using `spark-shell` if the path was configured correctly.

```cmd
spark-shell
```

Spark supports both Windows and UNIX-like systems as long as a supported Java version is available.

## Hadoop, HDFS, and YARN note for Windows

Hadoop can be used on Windows for learning, but local setup is generally more fragile than Linux-based environments, and many academic labs prefer Ubuntu or WSL for full HDFS and YARN workflows.

For a more stable Hadoop, HDFS, and YARN environment, Ubuntu inside WSL or a virtual machine is usually the safer choice for MapReduce practice.

## Install mrjob

Python virtual environments can still be used normally on Windows to run `mrjob` scripts locally or against Hadoop.

Create a virtual environment:

```cmd
python -m venv venv-mrjob
venv-mrjob\Scripts\activate
pip install "mrjob>=0.7,<0.8"
```

Run locally:

```cmd
python my_job.py input.txt
```

Run on Hadoop when a working Hadoop installation is available:

```cmd
python my_job.py -r hadoop hdfs:///user/USER/input.txt
```
