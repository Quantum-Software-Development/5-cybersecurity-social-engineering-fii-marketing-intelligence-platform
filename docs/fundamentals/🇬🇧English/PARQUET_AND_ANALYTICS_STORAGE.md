## ⚡ Apache Spark & PySpark

<br><br>

## Overview

In this project, Apache Spark is used as the distributed processing engine responsible for the parallel execution of analytical tasks.

PySpark provides integration between Spark and Python.

<br><br>

## Technical Definition

Apache Spark is a distributed computing platform designed for in-memory data processing.

PySpark is Spark’s Python API.

<br><br>

## Purpose

- distributed processing  
- ETL  
- distributed NLP  
- analytics  
- machine learning  
- parallel processing  

<br><br>

## Application in This Project

The architecture uses Spark for:

- text cleaning  
- tokenization  
- TF-IDF  
- distributed analytics  
- sentiment processing  
- parquet artifact generation  

<br><br>

## Example

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("FIIAnalytics").getOrCreate()
