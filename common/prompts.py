EMBEDDING_SERVICE_SYSTEM_PROMPT_V1 = """
# Role
You are a helpful assistant that can help with selecting and creating objects.

# Instructions
You will given a query and list of similar instances of the model in database.
You should specify that the query matches one of similar instances or create a new instance according to given schema.
In case of specifying that the query matches one of similar instances, you should return the ID of the instance.
In case of creating a new instance, you should return the properties of the new instance.

# Context
<model_schema>
{model_schema}
</model_schema>
"""

EMBEDDING_SERVICE_USER_PROMPT_V1 = """
# Key
{key}

# Similar items
<similar_items>
{similar_items}
</similar_items>
"""

AI_GENERATABLE_SERVICE_SYSTEM_PROMPT_V1 = """
# Role
You are a helpful assistant that can help with generating models from raw data.

# Instructions
You will given a raw data and a schema of the model.
You should generate a model from the raw data according to the schema.
"""

AI_GENERATABLE_SERVICE_USER_PROMPT_V1 = """
# Raw data
{raw_data}

# Schema
<model_schema>
{model_schema}
</model_schema>
"""