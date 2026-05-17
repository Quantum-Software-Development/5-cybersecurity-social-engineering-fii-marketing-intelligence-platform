# ⚡ Apache Spark & PySpark

## Visão Geral

Neste projeto, o Apache Spark é utilizado como motor de processamento distribuído responsável pela execução paralela das etapas analíticas.

O PySpark fornece integração entre Spark e Python.

<br><br>

## Definição Técnica

Apache Spark é uma plataforma de computação distribuída orientada a processamento em memória.

PySpark é a API Python do Spark.

<br><br>

## Para que Serve

- processamento distribuído
- ETL
- NLP distribuído
- analytics
- machine learning
- processamento paralelo

<br><br>

## Aplicação neste Projeto

A arquitetura utiliza Spark para:

- limpeza textual
- tokenização
- TF-IDF
- analytics distribuído
- processamento de sentimentos
- geração de artefatos parquet

<br><br>

## Exemplo

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("FIIAnalytics").getOrCreate()
```

<br><br>

## Benefícios

- escalabilidade
- processamento paralelo
- integração com MinIO
- compatibilidade com analytics modern


