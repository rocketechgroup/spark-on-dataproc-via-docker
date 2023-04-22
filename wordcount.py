#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
from operator import add

from pyspark.sql import SparkSession
from datetime import datetime

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: wordcount <input gcs file location> <output gcs location>", file=sys.stderr)
        sys.exit(-1)

    input_location = sys.argv[1]
    output_location = sys.argv[2]

    spark = SparkSession \
        .builder \
        .appName("PythonWordCount") \
        .getOrCreate()

    lines = spark.read.text(input_location).rdd.map(lambda r: r[0])
    counts = lines.flatMap(lambda x: x.split(' ')) \
        .map(lambda x: (x, 1)) \
        .reduceByKey(add)

    timestamp = datetime.now()
    formatted_timestamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")

    counts.saveAsTextFile(f"{output_location}/{formatted_timestamp}/")
    spark.stop()
