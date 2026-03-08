# Real-Time-GCP-Pipeline-for-Household-Data-Analysis
# Business Overview : 
A comprehensive data pipeline is essential for extracting, processing, and analyzing
such household income and expenditure data, particularly in regions transitioning from
planned to market economies, such as Eastern Europe and the former Soviet Union.
This data pipeline leverages scalable GCP services, including Google Cloud Storage,
Google Cloud Functions, Google BigQuery, and Looker Studio, to efficiently handle
large datasets, which enables seamless ingestion, distributed storage, and actionable
insights.
The project addresses the challenges of declining incomes and rising inequality in these
regions. It aims to analyze the effectiveness of social assistance programs to help
vulnerable households and identify programs that most effectively reduce poverty.

# Aim : 
The project aims to analyze household income and expenditure data across regions
and demographic groups in Eastern Europe and the former Soviet Union to uncover
insights into income distribution, spending behavior, and the impact of social assistance
programs in transitioning economies. The project will be executed through an
automated Google Cloud pipeline to efficiently process new data batches for further
analysis.

* Tech Stack:
   * Language: SQL, Python
   * Services: Google Cloud Storage, Google Cloud Functions, Google BigQuery, Looker Studio

* Google Cloud Storage:
A Google Cloud Storage (GCS) bucket is a simple, scalable storage solution in the
cloud that allows users to store and manage their data.

* Google Cloud Functions:
Google Cloud Functions is a serverless computing service that allows users to run code
in response to events, without worrying about the underlying infrastructure.

* Google BigQuery:
Google BigQuery is a fully managed, serverless, and highly scalable data warehouse
designed for real-time analytics on large datasets. It allows users to run SQL queries on
vast amounts of data in a fast and cost-effective manner.

* Looker Studio:
Google Looker Studio (formerly Google Data Studio) is a powerful and user-friendly
data visualization tool that allows users to create interactive and shareable reports and
dashboards.

# Approach:
* A project was created in the GCP console, which allows seamless creation of
other GCP services.
* The raw collected household data was loaded into Google Cloud Storage (GCS)
as the central storage for efficient data management.
* Cloud Functions was set up to trigger automatically whenever new data files are
uploaded to GCS. These functions transformed the data into the required format
and prepared it for analysis.
* The transformed data was then loaded into a Google BigQuery table for analysis.
* Looker Studio was used to create interactive visualizations from the BigQuery
table, to create visualization insights such as poverty rate comparisons and
trends across countries.

# Architecture Diagram:
<img width="1516" height="420" alt="image" src="https://github.com/user-attachments/assets/eff554b3-2715-4e3e-bb76-e566952d94af" />


