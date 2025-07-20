import pandas as pd

# Load M5 Walmart datasets
df_train = pd.read_csv('train.csv')
df_test = pd.read_csv('test.csv')
df_features = pd.read_csv('features.csv')
df_stores = pd.read_csv('stores.csv')
df_sample_submission = pd.read_csv('sampleSubmission.csv')

# Display basic info
def print_basic_info(df, name):
    print(f'--- {name} ---')
    print(df.info())
    print(df.head())
    print(df.describe(include="all"))
    print('\n')

print_basic_info(df_train, 'train')
print_basic_info(df_test, 'test')
print_basic_info(df_features, 'features')
print_basic_info(df_stores, 'stores')
print_basic_info(df_sample_submission, 'sampleSubmission') 