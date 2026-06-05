
# Apache Hadoop & Spark Installation Guide on Windows

> [!WARNING]
> Apache Hadoop is not officially supported on modern Windows releases. This guide provides a learning-oriented setup suitable for Apache Spark, Hadoop client libraries, and local experimentation. For full HDFS and YARN deployments, Ubuntu Linux or WSL2 is recommended.

This guide explains how to install OpenJDK, Apache Spark, Hadoop client dependencies, and optional `mrjob` support on Windows for local development and learning purposes.

## Prerequisites

The system should be Windows 10 or Windows 11 with:

- Administrator access
- Internet access
- PowerShell or Command Prompt
- A file extraction utility such as 7-Zip

## Install OpenJDK

Apache Spark and Hadoop require Java.

Install OpenJDK 17 or OpenJDK 11.

Set the `JAVA_HOME` environment variable:

```text
JAVA_HOME=C:\Program Files\Java\jdk-17
```

Add Java to the system `Path`:

```text
%JAVA_HOME%\bin
```

Verify the installation:

```cmd
java -version
```

Expected output:

```text
openjdk version "17.x.x"
```

## Create Big Data Directories

Create standard directories for Hadoop and Spark.

```cmd
cd \
mkdir hadoop
mkdir spark
```

The resulting structure will be:

```text
C:\
├── hadoop
└── spark
```

## Configure Hadoop Client Dependencies

Windows-based Spark installations often require Hadoop helper binaries for compatibility.

Set the `HADOOP_HOME` environment variable:

```text
HADOOP_HOME=C:\hadoop
```

Add Hadoop to the system `Path`:

```text
%HADOOP_HOME%\bin
```

Create the Hadoop binary directory:

```cmd
mkdir C:\hadoop\bin
```

Place any required Hadoop helper binaries (such as `winutils.exe`) inside:

```text
C:\hadoop\bin
```

Verify the environment variable:

```cmd
echo %HADOOP_HOME%
```

Expected output:

```text
C:\hadoop
```

## Install Apache Spark

Download a Spark distribution built for Hadoop 3.

Extract it into:

```text
C:\spark
```

Example:

```text
C:\spark\spark-4.x.x-bin-hadoop3
```

Set the `SPARK_HOME` variable:

```text
SPARK_HOME=C:\spark\spark-4.x.x-bin-hadoop3
```

Add Spark to the system `Path`:

```text
%SPARK_HOME%\bin
```

Verify the installation:

```cmd
spark-shell
```

A successful launch should display the Spark shell prompt.

Exit Spark:

```scala
:quit
```

## Verify Environment Variables

Check all configured variables:

```cmd
echo %JAVA_HOME%
echo %HADOOP_HOME%
echo %SPARK_HOME%
```

Verify Java:

```cmd
java -version
```

Verify Spark:

```cmd
spark-shell
```

## Hadoop, HDFS, and YARN Considerations

Apache Hadoop can run on Windows for educational purposes, but support is limited compared to Linux environments.

Common limitations include:

- Additional compatibility requirements
- Dependency on helper binaries
- Reduced community support
- Potential issues with HDFS and YARN services

For production environments or complete Hadoop clusters, Ubuntu Linux is generally preferred.

## Install Python

Verify Python:

```cmd
python --version
```

If Python is not installed, install Python 3 and ensure the option to add Python to `PATH` is enabled during installation.

Verify:

```cmd
python --version
pip --version
```

## Install mrjob

Create a virtual environment:

```cmd
python -m venv venv-mrjob
```

Activate it:

```cmd
venv-mrjob\Scripts\activate
```

Install `mrjob`:

```cmd
pip install "mrjob>=0.7,<0.8"
```

Verify:

```cmd
pip show mrjob
```

## Run a Local MapReduce Job

Example:

```cmd
python my_job.py input.txt
```

This executes the MapReduce job locally.

## Run a Hadoop-Based Job

If a working Hadoop installation is available:

```cmd
python my_job.py -r hadoop hdfs:///user/USER/input.txt
```

## Validation Checklist

Confirm the following:

- Java installed and accessible
- `JAVA_HOME` configured
- `HADOOP_HOME` configured
- `SPARK_HOME` configured
- Spark shell starts successfully
- Python installed
- Virtual environment created
- `mrjob` installed

## Summary

The environment now includes:

- OpenJDK
- Apache Spark
- Hadoop client dependencies
- Python
- mrjob

=
