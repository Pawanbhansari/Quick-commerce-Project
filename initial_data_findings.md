# Initial Data Findings

## Instacart Dataset

**Key Observations:**
- Large datasets: orders (3.4M rows), order_products__prior (32M+ rows), order_products__train (1.3M+ rows).
- No obvious missing values except for `days_since_prior_order` (NaN for first order per user).
- Data types look correct.
- Product, aisle, and department info is available for enrichment.

**What’s Needed:**
- Check for and handle any missing or anomalous values (especially in `days_since_prior_order`).
- Join product/aisle/department info for richer analysis.
- Visualize order frequency, reorder rates, and product popularity.
- Aggregate demand by time (day of week, hour) and user.

---

## M5 Walmart Dataset

**Key Observations:**
- `train.csv`: 421,570 rows, columns: Store, Dept, Date, Weekly_Sales, IsHoliday.
- `features.csv`: Many missing values in MarkDown1-5, CPI, Unemployment.
- `stores.csv`: 45 stores, with Type and Size.
- `test.csv` and `sampleSubmission.csv` are for forecasting/competition.
- Data types are mostly correct, but Date columns are objects (should be datetime).

**What’s Needed:**
- Convert `Date` columns to datetime.
- Handle missing values in features (MarkDowns, CPI, Unemployment).
- Merge train/test with features and stores for full context.
- Visualize sales trends, seasonality, and holiday effects.
- Aggregate sales by store, department, and time. 