__file__ = variables.get("PA_TASK_NAME")

if str(variables.get("TASK_ENABLED")).lower() == 'false':
    print("Task " + __file__ + " disabled")
    quit()

print("BEGIN " + __file__)

import bz2
import sys
import uuid

import pandas as pd

# -------------------------------------------------------------
# Get data from the propagated variables
#
FILE_URL = variables.get("FILE_URL")
FILE_DELIMITER = variables.get("FILE_DELIMITER")
LIMIT_OUTPUT_VIEW = variables.get("LIMIT_OUTPUT_VIEW")
LABEL_COLUMN = variables.get("LABEL_COLUMN")

assert FILE_URL is not None and FILE_URL is not ""
assert FILE_DELIMITER is not None and FILE_DELIMITER is not ""

dataframe = pd.read_csv(FILE_URL, FILE_DELIMITER)

dataframe_json = dataframe.to_json(orient='split').encode()
compressed_data = bz2.compress(dataframe_json)

dataframe_id = str(uuid.uuid4())
variables.put(dataframe_id, compressed_data)

print("dataframe id: ", dataframe_id)
print('dataframe size (original):   ', sys.getsizeof(dataframe_json), " bytes")
print('dataframe size (compressed): ', sys.getsizeof(compressed_data), " bytes")
print(dataframe.head())

resultMetadata.put("task.name", __file__)
resultMetadata.put("task.dataframe_id", dataframe_id)
resultMetadata.put("task.label_column", LABEL_COLUMN)

# -------------------------------------------------------------
# Preview results
#
LIMIT_OUTPUT_VIEW = variables.get("LIMIT_OUTPUT_VIEW")
LIMIT_OUTPUT_VIEW = 5 if LIMIT_OUTPUT_VIEW is None else int(LIMIT_OUTPUT_VIEW)
if LIMIT_OUTPUT_VIEW > 0:
    print("task result limited to: ", LIMIT_OUTPUT_VIEW, " rows")
    dataframe = dataframe.head(LIMIT_OUTPUT_VIEW).copy()
result = ''
with pd.option_context('display.max_colwidth', -1):
    result = dataframe.to_html(escape=False, classes='table table-bordered table-striped', justify='center')
result = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Machine Learning Preview</title>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" 
integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
</head>
<body class="container">
<h1 class="text-center my-4" style="color:#003050;">Data Preview</h1>
<div style="text-align:center">{0}</div>
</body></html>""".format(result)
result = result.encode('utf-8')
resultMetadata.put("file.extension", ".html")
resultMetadata.put("file.name", "output.html")
resultMetadata.put("content.type", "text/html")
# -------------------------------------------------------------

print("END " + __file__)
