import functions_framework
import csv
import tempfile
from google.cloud import bigquery, storage

# Full list of columns matching your BigQuery schema exactly after renaming
EXPECTED_COLUMNS = [
    "Country", "HouseholdId", "Food_Expenditure", "Health_Expenditure", "Rent_Expenditure",
    "Transportation_Expenditure", "Clothing_Expenditure", "Housing_Expenditure", "Education_Expenditure",
    "Other_Expenditure", "Total_Income", "Monthly_Wage_Income", "Other_Members_Wage_Income",
    "Self_Employment_Income", "Pension_Income", "Family_Support_Income", "Social_Assistance_Income",
    "Unemployment_Income", "Other_Social_Benefits", "Income_Tax", "Property_Tax", "Other_Taxes",
    "Land_Ownership", "Region", "Durable_Goods_Owned", "Socio_Economic_Group", "Household_Size",
    "Income_to_Expenditure_Ratio", "Per_Capita_Income",
    "amenita", "local", "carda", "tvclda", "refigda", "tenanca"
]

def transform_data(row):
    """
    Cleans, transforms, and aligns data with BigQuery schema.
    """
    numeric_fields = [
        'Foodx', 'Healthx', 'Rentx', 'Transx', 'Clothx', 'Housex', 'Educx', 'Otherx',
        'wagey', 'wagemy', 'wageky', 'selfemy', 'totpeny', 'familyy', 'socassy',
        'unempy', 'othsocy', 'sstaxy', 'pitaxy', 'othatxy', 'hhsize', 'landa', 'region1',
        'durabla', 'seg', 'amenita', 'local', 'carda', 'tvclda', 'refigda', 'tenanca'
    ]

    #Clean and convert numeric fields
    for field in numeric_fields:
        if field not in row or row[field] in (None, ''):
            row[field] = 0
        else:
            try:
                row[field] = float(row[field])
            except ValueError:
                row[field] = 0

    #Derived columns
    if float(row.get('Foodx', 0)) != 0:
        row['Income_to_Expenditure_Ratio'] = float(row['wagey']) / float(row['Foodx'])
    else:
        row['Income_to_Expenditure_Ratio'] = None

    if float(row.get('hhsize', 0)) != 0:
        row['Per_Capita_Income'] = float(row['wagey']) / float(row['hhsize'])
    else:
        row['Per_Capita_Income'] = None

    #Rename columns to match schema
    column_mapping = {
        'Foodx': 'Food_Expenditure',
        'Healthx': 'Health_Expenditure',
        'Rentx': 'Rent_Expenditure',
        'Transx': 'Transportation_Expenditure',
        'Clothx': 'Clothing_Expenditure',
        'Housex': 'Housing_Expenditure',
        'Educx': 'Education_Expenditure',
        'Otherx': 'Other_Expenditure',
        'wagey': 'Total_Income',
        'wagemy': 'Monthly_Wage_Income',
        'wageky': 'Other_Members_Wage_Income',
        'selfemy': 'Self_Employment_Income',
        'totpeny': 'Pension_Income',
        'familyy': 'Family_Support_Income',
        'socassy': 'Social_Assistance_Income',
        'unempy': 'Unemployment_Income',
        'othsocy': 'Other_Social_Benefits',
        'sstaxy': 'Income_Tax',
        'pitaxy': 'Property_Tax',
        'othatxy': 'Other_Taxes',
        'Country': 'Country',
        'hhsize': 'Household_Size',
        'landa': 'Land_Ownership',
        'region1': 'Region',
        'durabla': 'Durable_Goods_Owned',
        'seg': 'Socio_Economic_Group',
        'amenita': 'amenita',
        'local': 'local',
        'carda': 'carda',
        'tvclda': 'tvclda',
        'refigda': 'refigda',
        'tenanca': 'tenanca',
        'HouseholdId': 'HouseholdId'
    }

    transformed_row = {column_mapping.get(k, k): v for k, v in row.items()}

    #Drop unexpected columns
    transformed_row = {k: v for k, v in transformed_row.items() if k in EXPECTED_COLUMNS}

    #Fill missing expected columns
    for col in EXPECTED_COLUMNS:
        if col not in transformed_row:
            transformed_row[col] = None

    return transformed_row



@functions_framework.cloud_event
def import_to_big_query_with_transform(cloud_event):
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"]
    generation = data.get("generation", "unknown")

    #NEW GUARD CONDITION — prevents re-processing of marker files
    if file_name.startswith("processed/"):
        print(f"Skipping marker file: {file_name}")
        return

    print(f"Triggered by upload: gs://{bucket_name}/{file_name} (generation: {generation})")

    if not file_name.lower().endswith(".csv"):
        print("Skipping non-CSV file.")
        return

    storage_client = storage.Client()
    bq_client = bigquery.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    marker_blob_name = f"processed/{file_name}.done"
    marker_blob = bucket.blob(marker_blob_name)
    if marker_blob.exists():
        print(f"Skipping {file_name} as already processed.")
        return

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        blob.download_to_filename(temp_file.name)
        print(f"Downloaded {file_name} to {temp_file.name}")

    transformed_rows = []
    with open(temp_file.name, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transformed_rows.append(transform_data(row))

    with tempfile.NamedTemporaryFile(delete=False, mode="w", newline="", encoding="utf-8") as temp_csv:
        writer = csv.DictWriter(temp_csv, fieldnames=EXPECTED_COLUMNS)
        writer.writeheader()
        writer.writerows(transformed_rows)
        transformed_path = temp_csv.name

    print("Transformation complete. Loading data into BigQuery...")

    dataset = "household"
    table = "household_data"
    table_id = f"{bq_client.project}.{dataset}.{table}"

    schema = [
        bigquery.SchemaField("Country", "STRING"),
        bigquery.SchemaField("HouseholdId", "INTEGER"),
        bigquery.SchemaField("Food_Expenditure", "FLOAT"),
        bigquery.SchemaField("Health_Expenditure", "FLOAT"),
        bigquery.SchemaField("Rent_Expenditure", "FLOAT"),
        bigquery.SchemaField("Transportation_Expenditure", "FLOAT"),
        bigquery.SchemaField("Clothing_Expenditure", "FLOAT"),
        bigquery.SchemaField("Housing_Expenditure", "FLOAT"),
        bigquery.SchemaField("Education_Expenditure", "FLOAT"),
        bigquery.SchemaField("Other_Expenditure", "FLOAT"),
        bigquery.SchemaField("Total_Income", "FLOAT"),
        bigquery.SchemaField("Monthly_Wage_Income", "FLOAT"),
        bigquery.SchemaField("Other_Members_Wage_Income", "FLOAT"),
        bigquery.SchemaField("Self_Employment_Income", "FLOAT"),
        bigquery.SchemaField("Pension_Income", "FLOAT"),
        bigquery.SchemaField("Family_Support_Income", "FLOAT"),
        bigquery.SchemaField("Social_Assistance_Income", "FLOAT"),
        bigquery.SchemaField("Unemployment_Income", "FLOAT"),
        bigquery.SchemaField("Other_Social_Benefits", "FLOAT"),
        bigquery.SchemaField("Income_Tax", "FLOAT"),
        bigquery.SchemaField("Property_Tax", "FLOAT"),
        bigquery.SchemaField("Other_Taxes", "FLOAT"),
        bigquery.SchemaField("Land_Ownership", "FLOAT"),
        bigquery.SchemaField("Region", "FLOAT"),
        bigquery.SchemaField("Durable_Goods_Owned", "FLOAT"),
        bigquery.SchemaField("Socio_Economic_Group", "FLOAT"),
        bigquery.SchemaField("Household_Size", "FLOAT"),
        bigquery.SchemaField("Income_to_Expenditure_Ratio", "FLOAT"),
        bigquery.SchemaField("Per_Capita_Income", "FLOAT"),
        bigquery.SchemaField("amenita", "FLOAT"),
        bigquery.SchemaField("local", "FLOAT"),
        bigquery.SchemaField("carda", "FLOAT"),
        bigquery.SchemaField("tvclda", "FLOAT"),
        bigquery.SchemaField("refigda", "FLOAT"),
        bigquery.SchemaField("tenanca", "FLOAT"),
    ]

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        autodetect=False,
        skip_leading_rows=1,
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
    )

    with open(transformed_path, "rb") as source_file:
        load_job = bq_client.load_table_from_file(source_file, table_id, job_config=job_config)
        load_job.result()

    print(f"Data loaded into BigQuery table {table_id}")
    print(f"Job ID: {load_job.job_lid}")

    # Create marker file so this CSV is never reprocessed
    marker_blob.upload_from_string("processed")
    print(f"Marker file {marker_blob_name} created")
    print(f"Processing complete for: {file_name}")