SELECT * FROM `shruti-project-425403.household.household_data` LIMIT 1000


-- 1. Expenditure Analysis
-- Average Expenditure per Category:
SELECT 
    AVG(Food_Expenditure) AS avg_food_expenditure,
    AVG(Health_Expenditure) AS avg_health_expenditure,
    AVG(Rent_Expenditure) AS avg_rent_expenditure,
    AVG(Transportation_Expenditure) AS avg_transportation_expenditure,
    AVG(Clothing_Expenditure) AS avg_clothing_expenditure,
    AVG(Housing_Expenditure) AS avg_housing_expenditure
FROM `shruti-project-425403.household.household_data`;

-- Average Expenditure per Category per Country:
SELECT 
    `Country `,
    AVG(Food_Expenditure) AS avg_food_expenditure,
    AVG(Health_Expenditure) AS avg_health_expenditure,
    AVG(Rent_Expenditure) AS avg_rent_expenditure,
    AVG(Transportation_Expenditure) AS avg_transportation_expenditure,
    AVG(Clothing_Expenditure) AS avg_clothing_expenditure,
    AVG(Housing_Expenditure) AS avg_housing_expenditure
FROM `shruti-project-425403.household.household_data`
GROUP BY `Country ` 
ORDER BY `Country ` ;


-- Expenditure as a Percentage of Income:
SELECT 
    HouseholdId,
    (Food_Expenditure / Total_Income) * 100 AS food_percentage_of_income,
    (Rent_Expenditure / Total_Income) * 100 AS rent_percentage_of_income,
    (Health_Expenditure / Total_Income) * 100 AS health_percentage_of_income
FROM `shruti-project-425403.household.household_data`
WHERE Total_Income > 0;


-- 2.Income and Poverty Analysis
-- Income Distribution:
WITH aggregated_data AS (
    SELECT 
        PERCENTILE_CONT(Total_Income, 0.5) OVER() AS median_income,
        AVG(Total_Income) OVER() AS mean_income,
        MIN(Total_Income) OVER() AS min_income,
        MAX(Total_Income) OVER() AS max_income
    FROM `shruti-project-425403.household.household_data`
)
SELECT DISTINCT
    median_income,
    mean_income,
    min_income,
    max_income
FROM aggregated_data;


-- Poverty Classification:
SELECT 
    HouseholdId,
    CASE 
        WHEN Total_Income < 1000 THEN 'Below Poverty Line'
        WHEN Total_Income BETWEEN 1000 AND 5000 THEN 'Low Income'
        WHEN Total_Income BETWEEN 5000 AND 10000 THEN 'Middle Income'
        ELSE 'High Income'
    END AS poverty_classification
FROM `shruti-project-425403.household.household_data`;



-- 3. Demographic Analysis
-- Household Size and Income:
SELECT 
    Household_Size, 
    AVG(Total_Income) AS avg_income
FROM `shruti-project-425403.household.household_data`
GROUP BY Household_Size
ORDER BY Household_Size;


-- Region-based Analysis:
SELECT 
    Region,
    AVG(Total_Income) AS avg_income,
    AVG(Food_Expenditure) AS avg_food_expenditure,
    AVG(Housing_Expenditure) AS avg_housing_expenditure
FROM `shruti-project-425403.household.household_data`
GROUP BY Region
ORDER BY Region;



-- 4. Asset Ownership and Wealth Distribution
-- Asset Ownership vs. Income:
SELECT 
    Durable_Goods_Owned, 
    AVG(Total_Income) AS avg_income
FROM `shruti-project-425403.household.household_data`
GROUP BY Durable_Goods_Owned;

-- Land Ownership Analysis:
SELECT 
    Land_Ownership, 
    AVG(Total_Income) AS avg_income,
    AVG(Food_Expenditure) AS avg_food_expenditure
FROM `shruti-project-425403.household.household_data`
GROUP BY Land_Ownership;


-- 6. Multivariate Analysis
-- Correlation Between Income and Expenditure:
SELECT 
    CORR(Total_Income, Food_Expenditure) AS corr_income_food,
    CORR(Total_Income, Rent_Expenditure) AS corr_income_rent,
    CORR(Total_Income, Health_Expenditure) AS corr_income_health
FROM `shruti-project-425403.household.household_data`;



-- Clustering Households (Basic K-means Example):
-- If you're using BigQuery ML:
CREATE OR REPLACE MODEL `shruti-project-425403.household.kmeans_model`
OPTIONS(model_type='kmeans', num_clusters=3) AS
SELECT 
    Total_Income,
    Food_Expenditure,
    Rent_Expenditure,
    Health_Expenditure
FROM `shruti-project-425403.household.household_data`;

-- Evaluating model
SELECT * FROM ML.EVALUATE(MODEL `shruti-project-425403.household.kmeans_model`);

-- Predict Cluster Assignments
SELECT 
    Total_Income,
    Food_Expenditure,
    Rent_Expenditure,
    Health_Expenditure,
    predicted_cluster
FROM ML.PREDICT(MODEL `shruti-project-425403.household.kmeans_model`, 
    (SELECT * FROM `shruti-project-425403.household.household_data`));


SELECT *
FROM ML.EVALUATE(
    MODEL `shruti-project-425403.household.kmeans_model`
);

SELECT *
FROM ML.PREDICT(
    MODEL `shruti-project-425403.household.kmeans_model`, 
    (SELECT 
         Total_Income, 
         Food_Expenditure, 
         Rent_Expenditure, 
         Health_Expenditure 
     FROM `shruti-project-425403.household.household_data`)
)
LIMIT 10;


SELECT 
    Total_Income,
    Food_Expenditure,
    Rent_Expenditure,
    Health_Expenditure,
    CENTROID_ID AS predicted_cluster,
    NEAREST_CENTROIDS_DISTANCE AS distance_to_cluster
FROM ML.PREDICT(
    MODEL `shruti-project-425403.household.kmeans_model`, 
    (SELECT 
         Total_Income, 
         Food_Expenditure, 
         Rent_Expenditure, 
         Health_Expenditure 
     FROM `shruti-project-425403.household.household_data`)
);


SELECT 
    CENTROID_ID AS cluster_id,
    AVG(Total_Income) AS avg_income,
    AVG(Food_Expenditure) AS avg_food_expenditure,
    AVG(Rent_Expenditure) AS avg_rent_expenditure,
    AVG(Health_Expenditure) AS avg_health_expenditure
FROM ML.PREDICT(
    MODEL `shruti-project-425403.household.kmeans_model`, 
    (SELECT 
         Total_Income, 
         Food_Expenditure, 
         Rent_Expenditure, 
         Health_Expenditure 
     FROM `shruti-project-425403.household.household_data`)
)
GROUP BY CENTROID_ID;





